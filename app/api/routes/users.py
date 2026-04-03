from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.api.dependencies import get_current_active_user
from app.models.user import User

# Initialize the router for user-related endpoints
router = APIRouter()

# POST: Register a new user
@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Register a new user in the system.
    The router simply receives the validated Pydantic model (UserCreate) 
    and passes it to the service layer where the actual business logic resides.
    """
    return user_service.register_new_user(db=db, user_in=user_in)

# GET: Fetch current user profile
@router.get(
    "/me", 
    response_model=UserResponse, 
    status_code=status.HTTP_200_OK
)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the profile details of the currently authenticated user.
    Notice how there is zero database querying here. The dependency 
    'get_current_active_user' handles all the token validation and DB fetching.
    """
    return current_user