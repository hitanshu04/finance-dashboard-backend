from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.crud import crud_user
from app.schemas.user import UserCreate
from app.models.user import User
from app.core import security

def register_new_user(db: Session, user_in: UserCreate) -> User:
    """
    Handle the business logic for registering a new user.
    Includes email normalization, duplicate checks, and password hashing.
    """
    # 1. Normalize email to lowercase to prevent duplicate accounts 
    # (e.g., 'Test@test.com' and 'test@test.com' should be treated as the same email)
    normalized_email = user_in.email.lower()
    user_in.email = normalized_email

    # 2. Check if a user with this email already exists in the database
    existing_user = crud_user.get_user_by_email(db, email=normalized_email)
    if existing_user:
        # Raise a clean HTTP error that the API router will directly return to the client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists in the system."
        )

    # 3. Hash the password securely using our security service
    hashed_password = security.get_password_hash(user_in.password)

    # 4. Delegate the actual database insertion to the CRUD layer
    user = crud_user.create_user(db=db, user=user_in, hashed_password=hashed_password)
    
    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify a user's credentials during the login process.
    Returns the User object if successful, or raises/returns appropriately on failure.
    """
    # 1. Normalize the input email
    normalized_email = email.lower()
    
    # 2. Fetch the user from the database
    user = crud_user.get_user_by_email(db, email=normalized_email)
    
    # 3. If user doesn't exist, return None (Login fails)
    if not user:
        return None
        
    # 4. Verify if the provided password matches the hashed password in the DB
    if not security.verify_password(password, user.hashed_password):
        return None
        
    # 5. EDGE CASE HANDLING: Check active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact the administrator."
        )
        
    return user