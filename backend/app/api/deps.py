import uuid
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# OAuth2 scheme extracting Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Decodes JWT access token, checks expiration and validity,
    and returns the active User record from the database.
    """
    payload = decode_token(token)
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for API access",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact institutional administrator.",
        )

    return user


def require_roles(allowed_roles: List[str]) -> Callable[[User], User]:
    """
    Dependency factory that enforces server-side Role-Based Access Control.
    Raises 403 Forbidden if the user's role is not in allowed_roles.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Access requires one of {allowed_roles} roles. Your role is '{current_user.role}'.",
            )
        return current_user

    return role_checker


def verify_institution_boundary(target_institution_id: uuid.UUID, current_user: User) -> None:
    """
    Enforces multi-institution boundary isolation.
    Raises 403 Forbidden if an actor attempts to access or mutate records from another college.
    """
    if current_user.institution_id != target_institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Multi-institution boundary violation. You cannot access or modify records of another institution.",
        )


def verify_student_record_ownership(target_student_id: uuid.UUID, current_user: User) -> None:
    """
    Enforces record ownership for students.
    Students can only view or mutate their own records.
    Staff (Trainer, Placement Officer, Admin) can view student records within their institution.
    """
    if current_user.role == "STUDENT" and current_user.id != target_student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cross-user access violation. Students can only access their own records.",
        )
