from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base, AsyncSessionLocal
from app.routers import tasks, auth
from app.models import User
from app.crud import get_user_by_username
from app.dependencies import get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        user = await get_user_by_username(session, "test")
        if not user:
            test_user = User(
                username="test",
                hashed_password=get_password_hash("123")
            )
            session.add(test_user)
            await session.commit()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(tasks.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello there!"}