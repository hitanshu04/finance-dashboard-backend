from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal

# Base properties
class TransactionBase(BaseModel):
    amount: Decimal
    type: str
    category: str
    date: date
    notes: Optional[str] = None

    # Custom Validation. No chance of wrong data.
    @field_validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be strictly greater than 0')
        return v

    @field_validator('type')
    def type_must_be_valid(cls, v):
        allowed_types = ['income', 'expense']
        # .lower() sanitizes user input
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')
        return v.lower()

# When user sends data (Input)
class TransactionCreate(TransactionBase):
    pass

# When API responds (Output)
class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True