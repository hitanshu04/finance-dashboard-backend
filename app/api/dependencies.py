from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.crud import crud_user

# This links our Auth logic to FastAPI's built-in Swagger UI.
# It tells the auto-generated docs exactly where to send the login request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validates the JWT token from the request header, decodes it, 
    and fetches the corresponding user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Token may be expired or invalid.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Cryptographically verify and decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 2. Extract the user ID (subject) from the payload
        # Note: In Login API, we will ensure we inject {"sub": str(user.id)} into the token.
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        # Convert string ID back to integer
        user_id = int(user_id_str)
        
    except (jwt.PyJWTError, ValueError, TypeError):
        # Catches expired tokens, malformed tokens, or invalid ID conversions
        raise credentials_exception

    # 3. Fetch the actual user object from the database
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    A sequential dependency that first gets the authenticated user, 
    then enforces that their account is still active in the database.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your account has been deactivated. Please contact support."
        )
    return current_user

# Callable Class for dynamic Role-Based Access Control
class RoleChecker:
    """
    A dynamic dependency class that enforces Role-Based Access Control (RBAC).
    Usage in router: Depends(RoleChecker(["Admin", "Analyst"]))
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        # If the user's role is not in the allowed list, block the request
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}. Your role: {user.role}."
            )
        return user