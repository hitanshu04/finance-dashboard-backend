from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Roles will be validated by Pydantic, for now keep as simple string.
    role = Column(String, default="Viewer", nullable=False) 
    
    # Manages user status as active or inactive
    is_active = Column(Boolean, default=True)