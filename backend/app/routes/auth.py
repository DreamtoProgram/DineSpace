from typing import Any, Dict
from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_student
from app.schemas.auth import LoginRequest, LoginResponse, RFIDTapRequest, SSOLoginRequest, StudentPublic
from app.services.auth_service import authenticate_rfid, authenticate_sso, authenticate_student
from app.services.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Student Login",
    description="Authenticate a student using their Student ID and password. Returns a JWT access token and public profile.",
    responses={
        200: {"description": "Authentication successful, returns JWT bearer token."},
        401: {"description": "Invalid student credentials."},
        403: {"description": "Student account is inactive."},
        422: {"description": "Validation error (missing or malformed fields)."},
    },
)
def login(payload: LoginRequest) -> LoginResponse:
    """Authenticate student credentials and generate an access token.

    Note:
    - QR login ('Continue with QR') is deferred to later tasks as per project specs.
    - Password recovery ('Forgot password?') will be implemented in future phases.
    """
    student = authenticate_student(student_id=payload.studentId, password=payload.password)

    # Generate JWT token with student ID as the subject claim
    access_token = create_access_token(data={"sub": student["studentId"]})

    return LoginResponse(
        success=True,
        message="Login successful",
        accessToken=access_token,
        tokenType="bearer",
        student=StudentPublic(
            studentId=student["studentId"],
            name=student["name"],
            role=student.get("role", "student"),
            department=student.get("department"),
        ),
    )


@router.get(
    "/me",
    response_model=StudentPublic,
    status_code=status.HTTP_200_OK,
    summary="Current Authenticated Student Profile",
    description="Retrieve the public profile of the currently logged-in student. Requires Bearer JWT token.",
    responses={
        200: {"description": "Authenticated student profile returned successfully."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
    },
)
def get_current_user_profile(
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> StudentPublic:
    """Return the currently authenticated student profile for UI header/display."""
    return StudentPublic(
        studentId=current_student["studentId"],
        name=current_student["name"],
        role=current_student.get("role", "student"),
        department=current_student.get("department"),
        email=current_student.get("email"),
        rfidCardUid=current_student.get("rfidCardUid"),
        ssoProvider=current_student.get("ssoProvider"),
    )


@router.post(
    "/sso/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="University SSO Login",
    description="Authenticate via institutional Google Workspace, Microsoft 365, or Campus ERP Single Sign-On.",
)
def sso_login(payload: SSOLoginRequest) -> LoginResponse:
    """Authenticate or dynamically provision student via institutional SSO."""
    student = authenticate_sso(
        provider=payload.provider,
        token=payload.token,
        email=payload.email,
        name=payload.name,
    )
    access_token = create_access_token(data={"sub": student["studentId"]})
    return LoginResponse(
        success=True,
        message=f"SSO authentication successful via {payload.provider.title()}",
        accessToken=access_token,
        tokenType="bearer",
        student=StudentPublic(
            studentId=student["studentId"],
            name=student["name"],
            role=student.get("role", "student"),
            department=student.get("department"),
            email=student.get("email"),
            rfidCardUid=student.get("rfidCardUid"),
            ssoProvider=student.get("ssoProvider", payload.provider),
        ),
    )


@router.post(
    "/rfid/tap",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="University RFID / NFC Card Tap Authentication",
    description="Authenticate a student by tapping their physical RFID university smart card / NFC badge.",
)
def rfid_tap_login(payload: RFIDTapRequest) -> LoginResponse:
    """Authenticate student by scanning/tapping physical RFID smart card."""
    student = authenticate_rfid(card_uid=payload.cardUid)
    access_token = create_access_token(data={"sub": student["studentId"]})
    return LoginResponse(
        success=True,
        message="RFID card verified successfully",
        accessToken=access_token,
        tokenType="bearer",
        student=StudentPublic(
            studentId=student["studentId"],
            name=student["name"],
            role=student.get("role", "student"),
            department=student.get("department"),
            email=student.get("email"),
            rfidCardUid=student.get("rfidCardUid"),
            ssoProvider="rfid_nfc",
        ),
    )
