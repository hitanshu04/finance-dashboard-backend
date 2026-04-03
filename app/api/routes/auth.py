from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import user_service
from app.core import security

# APIRouter makes URLs modular
router = APIRouter()

@router.post("/login/access-token")
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests.
    This strictly complies with FastAPI's automated Swagger UI documentation.
    """
    # 1. Form data extracts 'username' and 'password'. 
    # In our system, the 'username' is actually the user's email.
    user = user_service.authenticate_user(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    # 2. If authentication fails, throw a standard 400 Bad Request
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    
    # 3. If successful, generate the JWT token. 
    # We strictly inject the user's ID as the 'sub' (subject) field as per JWT standards.
    access_token = security.create_access_token(data={"sub": str(user.id)})
    
    # 4. Return the exact JSON structure required by the OAuth2 specification
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }