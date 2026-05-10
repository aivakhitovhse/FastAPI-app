import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app import crud, models, schemas
from app.database import Base

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user_and_get_user_by_username(db_session):
    user_data = schemas.UserCreate(username="alice", password="password")
    created_user = await crud.create_user(db_session, user_data, hashed_password="hashed-password",
    )
    found_user = await crud.get_user_by_username(db_session, "alice")

    assert created_user.id is not None
    assert found_user == created_user
    assert found_user.username == "alice"
    assert found_user.hashed_password == "hashed-password"

@pytest.mark.asyncio
async def test_create_task_sets_owner_id(db_session):
    user = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                  hashed_password="hashed-password",)
    task_data = schemas.TaskCreate(title="Пойти за хлебом", description="бородинский")
    task = await crud.create_task(db_session, task_data, user_id=user.id)
    assert task.id is not None
    assert task.title == "Пойти за хлебом"
    assert task.description == "бородинский"
    assert task.owner_id == user.id
    assert task.status == models.TaskStatus.pending
    assert task.priority == 0

@pytest.mark.asyncio
async def test_get_tasks_returns_only_current_user_tasks(db_session):
    alice = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                   hashed_password="hashed-password",)
    bob = await crud.create_user(db_session,schemas.UserCreate(username="bob", password="password"),
                                 hashed_password="hashed-password",)
    await crud.create_task(db_session, schemas.TaskCreate(title="Alice task", description="private"),user_id=alice.id,)
    await crud.create_task(db_session, schemas.TaskCreate(title="Bob task", description="private"), user_id=bob.id,)
    tasks = await crud.get_tasks(db_session, user_id=alice.id)
    assert len(tasks) == 1
    assert tasks[0].title == "Alice task"
    assert tasks[0].owner_id == alice.id

@pytest.mark.asyncio
async def test_get_tasks_sorts_by_priority_desc(db_session):
    user = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                  hashed_password="hashed-password",)
    await crud.create_task(db_session,schemas.TaskCreate(title="Low", description="low", priority=1),user_id=user.id,)
    await crud.create_task( db_session,schemas.TaskCreate(title="High", description="high", priority=10), user_id=user.id,)
    await crud.create_task(db_session,schemas.TaskCreate(title="Medium", description="medium", priority=5),user_id=user.id,)

    tasks = await crud.get_tasks(db_session, user_id=user.id,sort_by="priority",sort_desc=True,)
    assert [task.title for task in tasks] == ["High", "Medium", "Low"]

@pytest.mark.asyncio
async def test_update_task_changes_only_passed_fields(db_session):
    user = await crud.create_user(db_session,schemas.UserCreate(username="alice", password="password"),hashed_password="hashed-password",)
    task = await crud.create_task(db_session,schemas.TaskCreate(title="Old title",description="Old description",priority=1,), user_id=user.id,)
    updated_task = await crud.update_task(db_session, task_id=task.id, user_id=user.id, task_update=schemas.TaskUpdate(title="New title"),)

    assert updated_task.title == "New title"
    assert updated_task.description == "Old description"
    assert updated_task.priority == 1

@pytest.mark.asyncio
async def test_update_task_returns_none_for_another_user_task(db_session):
    alice = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                   hashed_password="hashed-password",)
    bob = await crud.create_user(db_session, schemas.UserCreate(username="bob", password="password"),
                                 hashed_password="hashed-password",)
    task = await crud.create_task(db_session,schemas.TaskCreate(title="Alice task", description="private"),user_id=alice.id,)

    updated_task = await crud.update_task(db_session, task_id=task.id,user_id=bob.id,
                                          task_update=schemas.TaskUpdate(title="Bob update"),)

    assert updated_task is None


@pytest.mark.asyncio
async def test_delete_task_removes_task(db_session):
    user = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                  hashed_password="hashed-password",)
    task = await crud.create_task(db_session, schemas.TaskCreate(title="Task", description="Description"),user_id=user.id,)
    deleted = await crud.delete_task(db_session, task_id=task.id, user_id=user.id)
    task_after_delete = await crud.get_task(db_session, task_id=task.id, user_id=user.id)

    assert deleted is True
    assert task_after_delete is None


@pytest.mark.asyncio
async def test_delete_task_returns_false_for_missing_task(db_session):
    deleted = await crud.delete_task(db_session, task_id=999, user_id=1)

    assert deleted is False


@pytest.mark.asyncio
async def test_search_tasks_finds_matches_in_title_and_description(db_session):
    user = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),
                                  hashed_password="hashed-password",)
    await crud.create_task(db_session,schemas.TaskCreate(title="Read FastAPI docs", description="Study routing"),user_id=user.id,)
    await crud.create_task(db_session, schemas.TaskCreate(title="Write tests", description="Cover FastAPI app"), user_id=user.id,)
    await crud.create_task(db_session,schemas.TaskCreate(title="Buy groceries", description="Milk and bread"),user_id=user.id,)

    tasks = await crud.search_tasks(db_session, user_id=user.id, query_text="FastAPI")
    assert {task.title for task in tasks} == {"Read FastAPI docs","Write tests"}


@pytest.mark.asyncio
async def test_get_top_priority_tasks_returns_limited_highest_priority_tasks(db_session):
    user = await crud.create_user(db_session, schemas.UserCreate(username="alice", password="password"),hashed_password="hashed-password",)
    await crud.create_task(db_session, schemas.TaskCreate(title="Low", description="low", priority=1), user_id=user.id,)
    await crud.create_task( db_session, schemas.TaskCreate(title="High", description="high", priority=10),  user_id=user.id )
    await crud.create_task( db_session, schemas.TaskCreate(title="Medium", description="medium", priority=5),user_id=user.id,)

    tasks = await crud.get_top_priority_tasks(db_session, user_id=user.id, limit=2)
    assert [task.title for task in tasks] == ["High", "Medium"]
