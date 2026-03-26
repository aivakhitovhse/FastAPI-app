from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, dependencies, database

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.User)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(database.get_db)
):
    existing_user = await crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой user уже существует"
        )
    hashed_password = dependencies.get_password_hash(user.password)
    new_user = await crud.create_user(db, user, hashed_password)
    return new_user

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(database.get_db)
):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not dependencies.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="неправильный  username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = dependencies.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}