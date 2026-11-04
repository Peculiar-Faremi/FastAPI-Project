from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from app.schemas import CreateUser,UserResponse
from app.services import users as user_service
router= APIRouter(
    tags=["Users"]
)

@router.post("/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: CreateUser, db: Session = Depends(get_db)):
    return  user_service.create_user(db, new_user)