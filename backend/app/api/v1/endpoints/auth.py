from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_password_reset_token,
    decode_token,
)
from app.core.rate_limit import (
    login_rate_limiter,
    register_rate_limiter,
    reset_rate_limiter,
    get_client_ip,
)
from app.api.deps import get_current_user
from app.services.audit import AuditService
from app.models.user import User, StudentProfile
from app.models.institution import Institution, Cohort
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserSummary,
    UserProfileResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    StudentProfileData,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Student Account Self-Registration",
    description="Registers a new student account. Strictly prevents arbitrary users from self-assigning staff or administrative privileges."
)
def register_student(
    request: Request,
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    client_ip = get_client_ip(request)
    register_rate_limiter.check(client_ip)

    # Validate password complexity
    validate_password_strength(payload.password)

    # Verify institution existence and active status
    institution = db.query(Institution).filter(Institution.id == payload.institution_id).first()
    if not institution or not institution.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive institution specified",
        )

    # Check for existing email registration
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address is already registered",
        )

    # Anti-Privilege Escalation: Public self-registration ALWAYS creates a STUDENT
    new_user = User(
        institution_id=payload.institution_id,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role="STUDENT",
        is_active=True,
    )
    db.add(new_user)
    db.flush()

    # Link student profile if roll number and cohort provided
    if payload.roll_number and payload.cohort_id:
        cohort = db.query(Cohort).filter(
            Cohort.id == payload.cohort_id,
            Cohort.department.has(institution_id=payload.institution_id)
        ).first()
        if not cohort:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cohort does not exist or does not belong to the specified institution",
            )
        student_prof = StudentProfile(
            user_id=new_user.id,
            cohort_id=payload.cohort_id,
            roll_number=payload.roll_number.strip(),
            placement_status="NOT_PLACED",
        )
        db.add(student_prof)

    db.commit()
    db.refresh(new_user)

    # Record security audit event
    AuditService.record_event(
        db=db,
        institution_id=new_user.institution_id,
        actor_user_id=new_user.id,
        action="USER_REGISTERED",
        entity_type="User",
        entity_id=str(new_user.id),
        ip_address=client_ip,
        details_json={"email": new_user.email, "role": new_user.role},
    )

    # Issue access token
    token = create_access_token(
        data={
            "sub": str(new_user.id),
            "role": new_user.role,
            "institution_id": str(new_user.institution_id),
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserSummary.model_validate(new_user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Secure User Authentication",
    description="Authenticates credentials, enforces rate limits, logs security events, and issues JWT token."
)
def login(
    request: Request,
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    client_ip = get_client_ip(request)
    login_rate_limiter.check(client_ip)

    user = db.query(User).filter(User.email == payload.email.lower()).first()

    # Generic invalid credentials message to prevent account enumeration
    if not user or not verify_password(payload.password, user.password_hash):
        if user:
            AuditService.record_event(
                db=db,
                institution_id=user.institution_id,
                actor_user_id=user.id,
                action="LOGIN_FAILED",
                entity_type="User",
                entity_id=str(user.id),
                ip_address=client_ip,
                details_json={"reason": "Incorrect password"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is deactivated. Contact the institutional administrator.",
        )

    # Log login success
    AuditService.record_event(
        db=db,
        institution_id=user.institution_id,
        actor_user_id=user.id,
        action="LOGIN_SUCCESS",
        entity_type="User",
        entity_id=str(user.id),
        ip_address=client_ip,
    )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "institution_id": str(user.institution_id),
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserSummary.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieves the profile and academic membership details of the currently authenticated user."
)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    profile_data = None
    if current_user.student_profile:
        profile_data = StudentProfileData.model_validate(current_user.student_profile)

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        institution_id=current_user.institution_id,
        is_active=current_user.is_active,
        student_profile=profile_data,
    )


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Generates an expiring, single-use password reset token."
)
def request_password_reset(
    request: Request,
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    client_ip = get_client_ip(request)
    reset_rate_limiter.check(client_ip)

    user = db.query(User).filter(User.email == payload.email.lower()).first()
    reset_token = None
    if user and user.is_active:
        reset_token = create_password_reset_token(user.email)
        AuditService.record_event(
            db=db,
            institution_id=user.institution_id,
            actor_user_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            entity_type="User",
            entity_id=str(user.id),
            ip_address=client_ip,
        )

    response = {
        "message": "If the email is registered, a password reset token has been issued.",
    }
    # In development mode, provide token for testing and verification without SMTP
    if settings.ENVIRONMENT == "development" and reset_token:
        response["dev_reset_token"] = reset_token

    return response


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Complete Password Reset",
    description="Resets user password using a verified, expiring single-use reset token."
)
def reset_password(
    request: Request,
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    client_ip = get_client_ip(request)
    token_payload = decode_token(payload.token)
    if token_payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type for password reset",
        )

    email = token_payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token payload invalid",
        )

    validate_password_strength(payload.new_password)

    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = hash_password(payload.new_password)
    db.commit()

    AuditService.record_event(
        db=db,
        institution_id=user.institution_id,
        actor_user_id=user.id,
        action="PASSWORD_RESET_COMPLETED",
        entity_type="User",
        entity_id=str(user.id),
        ip_address=client_ip,
    )

    return {"message": "Password successfully reset. You may now sign in with your new credentials."}
