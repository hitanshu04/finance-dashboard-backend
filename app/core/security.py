import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

# Setup the password hashing context using the industry-standard bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Securely compare a plain text password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Convert a plain text password into a secure bcrypt hash.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generate a JSON Web Token (JWT) with an explicit expiration time.
    """
    # 1. Create a copy of the data so we don't mutate the original dictionary
    to_encode = data.copy()
    
    # 2. Determine expiration time (Edge Case Handling: Always use UTC)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # 3. Add the expiration timestamp ('exp') to the JWT payload
    to_encode.update({"exp": expire})
    
    # 4. Cryptographically sign the token using our SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt