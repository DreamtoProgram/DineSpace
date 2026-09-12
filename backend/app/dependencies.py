from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.services.auth_service import get_student_by_id
from app.services.security import decode_access_token

# Configure HTTPBearer scheme for Swagger UI integration
bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Enter JWT Bearer token format: Bearer <your_access_token>",
)


async def get_current_student(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency to extract, verify JWT, and retrieve authenticated student.

    Args:
        credentials: Optional Bearer authorization header credentials.

    Returns:
        The authenticated student record from MongoDB.

    Raises:
        HTTPException(401): If token is missing, expired, invalid, or student not found.
        HTTPException(403): If student account is inactive.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_id: Optional[str] = payload.get("sub")
    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token: missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated student not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not student.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student account is inactive. Please contact dining hall administration.",
        )

    return student
