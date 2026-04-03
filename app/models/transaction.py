from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # We keep Amount as DECIMAL and not as Float.
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Type: "income" OR "expense"
    type = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    notes = Column(String, nullable=True)

    # Relation setup. Checks which user created this record
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
