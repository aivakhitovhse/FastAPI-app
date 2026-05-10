import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app import crud, database, dependencies, schemas
from app.database import Base
from app.routers import auth, tasks

@pytest_asyncio.fixture
async def test_session_maker():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    yield session_maker
    await engine.dispose()

@pytest_asyncio.fixture
async def auth_client(test_session_maker):
    app = FastAPI()
    app.include_router(auth.router)

    async def override_get_db():
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[database.get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def tasks_client(test_session_maker):
    async with test_session_maker() as session:
        current_user = await crud.create_user(
            session,
            schemas.UserCreate(username="alice", password="password"),
            hashed_password="hashed-password",
        )

    app = FastAPI()
    app.include_router(tasks.router)

    async def override_get_db():
        async with test_session_maker() as session:
            yield session

    async def override_get_current_user():
        return current_user

    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[dependencies.get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client, current_user
    app.dependency_overrides.clear()
