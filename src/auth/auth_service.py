"""
Authentication service for multi-user product.
Handles user registration, login, JWT tokens, and token encryption for stored credentials.

Uses:
- passlib (bcrypt) for password hashing
- PyJWT for access tokens
- cryptography (Fernet) for encrypting stored Instagram access tokens
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import SETTINGS
from src.database.models import User


# ========== Password Hashing ==========

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT Token Management ==========

def create_access_token(
    user_id: int,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id: The user's database ID
        email: The user's email address
        expires_delta: Custom expiration time (default: settings JWT_EXPIRY_HOURS)

    Returns:
        Encoded JWT string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=SETTINGS.JWT_EXPIRY_HOURS)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        SETTINGS.JWT_SECRET,
        algorithm=SETTINGS.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT string

    Returns:
        Decoded payload dict with 'sub', 'email', 'iat', 'exp'

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    return jwt.decode(
        token,
        SETTINGS.JWT_SECRET,
        algorithms=[SETTINGS.JWT_ALGORITHM],
    )


# ========== Token Encryption (for stored Instagram credentials) ==========

def get_fernet() -> Fernet:
    """
    Get Fernet cipher for encrypting/decrypting stored access tokens.
    
    The encryption key should be generated once and stored in .env:
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    if not SETTINGS.ENCRYPTION_KEY:
        raise ValueError(
            "ENCRYPTION_KEY not set. Generate one with:\n"
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return Fernet(SETTINGS.ENCRYPTION_KEY.encode())


def encrypt_token(plaintext_token: str) -> str:
    """Encrypt an access token for secure database storage."""
    f = get_fernet()
    return f.encrypt(plaintext_token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored access token for API use."""
    f = get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()


# ========== User Operations ==========

async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: Optional[str] = None,
) -> User:
    """
    Register a new user.

    Args:
        session: Database session
        email: User's email address
        password: Plaintext password (will be hashed)
        full_name: Optional full name

    Returns:
        Created User object

    Raises:
        ValueError: If email already exists
    """
    # Check if email already exists
    existing = await session.execute(
        select(User).where(User.email == email)
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError(f"User with email {email} already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    session.add(user)
    await session.flush()  # Get the generated ID
    return user


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate a user by email and password.

    Args:
        session: Database session
        email: User's email
        password: Plaintext password

    Returns:
        User object if credentials are valid, None otherwise
    """
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by their database ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
