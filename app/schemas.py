from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] =None

class Task(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    tasks: list[Task] = []
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


