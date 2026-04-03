from pydantic import BaseModel, EmailStr
from typing import Optional

# Base properties which are common everywhere
class UserBase(BaseModel):
    email: EmailStr  # Pydantic checks whether email is in valid format or not
    role: Optional[str] = "Viewer"

# When new user registers(Input)
class UserCreate(UserBase):
    password: str

# When API gives response(Output)
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # Allows SQLAlchemy model conversion to Pydantic 