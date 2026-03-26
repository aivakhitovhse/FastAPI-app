from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, database, dependencies, models

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=schemas.Task)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return await crud.create_task(db, task, current_user.id)

@router.get("/", response_model=list[schemas.Task])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    sort_by: str = Query("created_at", pattern="^(created_at|title|status|priority)$"),
    sort_desc: bool = True,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    tasks = await crud.get_tasks(db, current_user.id, skip, limit, sort_by, sort_desc)
    return tasks

@router.get("/search", response_model=list[schemas.Task])
async def search_task(
    q: str,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    tasks = await crud.search_tasks(db, current_user.id, q)
    return tasks

@router.get("/top", response_model=list[schemas.Task])
async def top_priority_tasks(
    n: int = Query(5, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    tasks = await crud.get_top_priority_tasks(db, current_user.id, limit=n)
    return tasks

@router.get("/{task_id}", response_model=schemas.Task)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    task = await crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    task = await crud.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    deleted = await crud.delete_task(db, task_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return