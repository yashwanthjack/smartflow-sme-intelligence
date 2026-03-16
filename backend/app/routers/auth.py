"""
Authentication Router - Login, Register, Profile
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth import (
    Token, UserCreate, UserResponse,
    authenticate_user, create_access_token, create_user,
    get_user_by_email, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.
    Get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    First user registered becomes an Admin.
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # For MVP: Every new user is an Admin of their own organization
    role = UserRole.ADMIN
    
    from app.models.entity import Entity
    # Create a new Organization for this user
    org_name = f"{user_data.full_name}'s Organization" if user_data.full_name else "My Organization"
    new_entity = Entity(name=org_name, entity_type="sme")
    db.add(new_entity)
    db.commit()
    db.refresh(new_entity)
    entity_id = new_entity.id
    
    new_user = create_user(db, user_data, role=role, entity_id=entity_id)
    return new_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current logged in user's profile.
    """
    return current_user


@router.get("/health")
async def auth_health():
    """Health check for auth service."""
    return {"status": "ok", "service": "auth"}
