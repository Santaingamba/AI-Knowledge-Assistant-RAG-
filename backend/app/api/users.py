from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_db
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import get_current_user
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)
        
    await db.commit()
    await db.refresh(current_user)
    return current_user
