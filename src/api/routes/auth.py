"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db_session
from src.auth.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user_by_id,
)

router = APIRouter()


# ========== Request/Response Models ==========

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    is_active: bool


# ========== Auth Dependency ==========

async def get_current_user(
    token: str = Depends(lambda: ""),  # Will be replaced by proper header extraction
):
    """Extract current user from JWT token."""
    # In production, extract from Authorization header
    pass


# ========== Routes ==========

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Register a new user."""
    try:
        user = await register_user(
            session=session,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Login to get an access token."""
    user = await authenticate_user(session, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
    )
