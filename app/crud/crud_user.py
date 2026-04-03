from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Fetch a user by their email address.
    Used for login and duplicate email validation during registration.
    """
    # Using .first() stops the database search immediately after finding the first match.
    # This is an O(1) operation because 'email' is indexed in our database model.
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Fetch a user by their primary key (ID).
    Used primarily in the authentication middleware to verify the token's owner.
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    """
    Insert a new user record into the database.
    Notice that we pass the 'hashed_password' separately, not the raw password.
    """
    # Create the SQLAlchemy model instance
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    # Add the instance to the database session
    db.add(db_user)
    
    # Commit the transaction to ensure ACID compliance
    db.commit()
    
    # Refresh the instance to get the auto-generated ID from the database
    db.refresh(db_user)
    
    return db_user