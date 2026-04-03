from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# 1. Create Engine (The Connection Pool)
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 2. SessionLocal (The Worker)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base Class (For Models)
Base = declarative_base()

# 4. Dependency Injection (The Safe Pipeline)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()