from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_task(db: AsyncSession, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_tasks(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100,
                    sort_by: str = "created_at", sort_desc: bool = True):
    query = select(models.Task).where(models.Task.owner_id == user_id)
    if sort_by == "title":
        order = desc(models.Task.title) if sort_desc else asc(models.Task.title)
    elif sort_by == "status":
        order = desc(models.Task.status) if sort_desc else asc(models.Task.status)
    elif sort_by == "priority":
        order = desc(models.Task.priority) if sort_desc else asc(models.Task.priority)
    elif sort_by == "created_at":
        order = desc(models.Task.created_at) if sort_desc else asc(models.Task.created_at)
    query = query.order_by(order).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(select(models.Task).where(models.Task.id == task_id, models.Task.owner_id == user_id))
    return result.scalar_one_or_none()

async def update_task(db: AsyncSession, task_id: int, user_id: int, task_update: schemas.TaskUpdate):
    db_task = await get_task(db, task_id, user_id)
    if not db_task:
        return None
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int, user_id: int):
    db_task = await get_task(db, task_id, user_id)
    if not db_task:
        return False
    await db.delete(db_task)
    await db.commit()
    return True

async def search_tasks(db: AsyncSession, user_id: int, query_text: str):
    stmt = select(models.Task).where(
        models.Task.owner_id == user_id,
        (models.Task.title.contains(query_text)) | (models.Task.description.contains(query_text))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_top_priority_tasks(db: AsyncSession, user_id: int, limit: int = 5):
    stmt = (
        select(models.Task)
        .where(models.Task.owner_id == user_id)
        .order_by(desc(models.Task.priority), desc(models.Task.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()