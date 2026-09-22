from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from jose import jwt, JWTError
from app.core.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse, Token, RefreshRequest
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
        
    access_token = create_access_token(data={"email": user.email, "sub": user.id})
    refresh_token = create_refresh_token(data={"email": user.email, "sub": user.id})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    try:
        payload = jwt.decode(body.refresh_token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise UnauthorizedException("Invalid refresh token")
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Inactive user")

    new_access = create_access_token(data={"email": user.email, "sub": user.id})
    new_refresh = create_refresh_token(data={"email": user.email, "sub": user.id})
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    # In a real system, you might blacklist the token here.
    return {"message": "Successfully logged out"}
