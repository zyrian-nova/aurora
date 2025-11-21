"""
Security utilities for Aurora
"""
from uuid import UUID
from jose import JWTError, jwt
from typing import Optional, TypedDict, cast
from datetime import datetime, timedelta, timezone
from app.settings import get_logger, settings
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

logger = get_logger(__name__)

# Type definitions for the dictionaries in functions:
# decode_token
# generate_test_token
class TokenPayload(TypedDict, total=False):
    """Type definition for JWT token payload."""
    sub: str        # User ID (UUID as string)
    username: str   # Username (Only in access token)
    exp: float      # Expiration timestamp
    iat: float      # Issued at timestamp
    type: str       # Token type: "access" or "refresh"

class TokenResponse(TypedDict):
    """Type definition for token response."""
    access_token: str
    refresh_token: str
    token_type: str

# Password hashing
ph = PasswordHasher(
    time_cost=2,        # Iterations
    memory_cost=65536,  # Memory usage in KiB (64MB)
    parallelism=4,      # Parallel threads
    hash_len=32,        # Length of hash in bytes
    salt_len=16         # Length of salt in bytes
)

def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2id."""
    try:
        return ph.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password."""
    try:
        # Verify() raises VerifyMismatchError if password is wrong
        ph.verify(hashed_password, plain_password)
        # Check if hash needs rehashing (parameters changed)
        if ph.check_needs_rehash(hashed_password):
            logger.info("Password hash needs rehashing with updated parameters")
        return True
    except VerifyMismatchError:
        # Wrong password expected - not an error
        return False
    except (VerificationError, InvalidHashError) as e:
        # Hash is corrupted or invalid format
        logger.error(f"Invalid password hash: {e}")
        return False
    except Exception as e:
        logger.error(f"Password verification error: {e}")
    return False

def needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs to be rehashed."""
    try:
        return ph.check_needs_rehash(hashed_password)
    except Exception as e:
        logger.error(f"Error checking hash: {e}")
        return False

# JWT Generation
def create_access_token(
    user_id: UUID,
    username: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token fro authenticated user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # Payload data
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "exp": expire.timestamp(), # Expiration time
        "iat": datetime.now(timezone.utc), # Issued at
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def create_refresh_token(
  user_id: UUID,
  expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token for token renewal."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    # Payload data
    to_encode = {
        "sub": str(user_id),
        "exp": expire.timestamp(), # Expiration time
        "iat": datetime.now(timezone.utc), # Issued at
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # Validate payload before cast
        if "sub" not in payload or "type" not in payload:
            logger.warning("Invalid token payload: missing required fields")
            return None
        # Explicitly cast dict[str, Any] to TokenPayload structure
        return cast(TokenPayload, payload)
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None

def get_user_id_from_token(token: str) -> Optional[UUID]:
    """Extract user ID from a JWT token."""
    payload = decode_token(token)
    if payload and "sub" in payload:
        try:
            return UUID(payload["sub"])
        except (ValueError, TypeError):
            logger.error(f"invalid UUID in token payload: {payload.get('sub')}")
            return None
    return None

def verify_token_type(token: str, expected_type: str) -> bool:
    """Verify that a token is of the expected type (access or refresh)."""
    payload = decode_token(token)
    if not payload:
        return False

    token_type = payload.get("type")
    return token_type == expected_type

# Token utilities
def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired."""
    payload = decode_token(token)
    if not payload:
        return True # Invalid token is expired

    exp = payload.get("exp")
    if not exp:
        return True

    # JWT exp is in UTC timestamp
    expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
    return datetime.now(timezone.utc) > expiration

def get_tokenexpiration(token: str) -> Optional[datetime]:
    """Get the expiration datetime of a token."""
    payload = decode_token(token)
    if not payload or "exp" not in payload:
        return None

    return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

# Password validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 10 characters long"

    if len(password) > 50:
        return False, "Password must be less than 50 characters long"

    # This will have more rules (uppercase, numbers, special characters)
    return True, ""

# Testing helpers
def generate_test_tokens(user_id: UUID, username: str) -> TokenResponse:
    """Generate test tokens for development/testing."""
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot generate test tokens in production!")

    return {
        "access_token": create_access_token(user_id, username),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer"
    }
