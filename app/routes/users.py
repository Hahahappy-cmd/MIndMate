from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets
from ..database import get_db
from .. import models, schemas
from .. import auth
from ..dependencies import get_current_user
from ..utils.security import generate_reset_token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_verified=False 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    
    access_token = auth.create_access_token(data={"sub": user.username})
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    payload = auth.verify_token(token_data.refresh_token, is_refresh=True)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    
    access_token = auth.create_access_token(data={"sub": username})
    refresh_token = auth.create_refresh_token(data={"sub": username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/password-reset-request")
def password_reset_request(
    request: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:

        # For now, we'll just create the token and return it
        reset_token = generate_reset_token()
        
        # Create reset token in database
        db_token = models.PasswordResetToken(
            token=reset_token,
            user_id=user.id
        )
        db.add(db_token)
        db.commit()
        
        # In production: send_email(user.email, reset_token)
        print(f"Password reset token for {user.email}: {reset_token}")
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/password-reset")
def password_reset(reset_data: schemas.PasswordReset, db: Session = Depends(get_db)):
    
    reset_token = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == reset_data.token,
        models.PasswordResetToken.used == False,
        models.PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update user password
    reset_token.user.hashed_password = auth.get_password_hash(reset_data.new_password)
    reset_token.used = True
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=schemas.UserWithEntries)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):

    return {"message": "Logged out successfully"}