"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import secrets

from ..database import get_db, Database

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: dict
    token: str
    expires_at: str


def create_token() -> tuple[str, str]:
    """Create a new session token and expiration"""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    return token, expires_at


async def get_current_user(authorization: Optional[str] = Header(None), db: Database = Depends(get_db)):
    """Dependency to get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    session = db.get_session(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if token expired
    if datetime.fromisoformat(session['expires_at']) < datetime.now():
        db.delete_session(token)
        raise HTTPException(status_code=401, detail="Token expired")
    
    user = db.get_user_by_id(session['user_id'])
    if not user or not user['is_active']:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db: Database = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if db.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.get_user_by_username(request.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user = db.create_user(request.email, request.username, request.password)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create session
    token, expires_at = create_token()
    db.create_session(user['id'], token, expires_at)
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return AuthResponse(
        user=user_data,
        token=token,
        expires_at=expires_at
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Database = Depends(get_db)):
    """Login with email and password"""
    user = db.get_user_by_email(request.email)
    
    if not user or not db.verify_password(request.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user['is_active']:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Update last login
    db.update_last_login(user['id'])
    
    # Create session
    token, expires_at = create_token()
    db.create_session(user['id'], token, expires_at)
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return AuthResponse(
        user=user_data,
        token=token,
        expires_at=expires_at
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None), db: Database = Depends(get_db)):
    """Logout and invalidate session"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        db.delete_session(token)
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info"""
    user_data = {k: v for k, v in user.items() if k != 'password_hash'}
    return {"user": user_data}


@router.get("/admin/stats")
async def get_admin_stats(user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    """Get admin statistics (admin only)"""
    if not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = db.get_admin_stats()
    return stats
