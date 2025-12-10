from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import get_db
from . import models
from .auth import SECRET_KEY, ALGORITHM, verify_token


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        if token.startswith("Bearer "):
            token = token[7:]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
    except JWTError as e:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Optional dependency - returns user if authenticated, None otherwise
    """
    try:
        token = credentials.credentials
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = verify_token(token)
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            return None
        
        user = db.query(models.User).filter(models.User.username == username).first()
        return user
    except Exception:
        return None