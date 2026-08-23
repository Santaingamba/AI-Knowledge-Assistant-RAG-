from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.models.sqlmodel_models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_in: UserCreate) -> User:
        # Check if user exists
        result = await self.db.execute(select(User).where(User.email == user_in.email))
        if result.scalars().first():
            raise ConflictException(detail="Email already registered")

        # Create user
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise UnauthorizedException(detail="Could not validate credentials")
    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise UnauthorizedException(detail="User not found")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")
    return user
