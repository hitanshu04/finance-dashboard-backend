from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from typing import Optional

from app.crud import crud_transaction
from app.schemas.transaction import TransactionCreate
from app.models.transaction import Transaction

def _validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    """
    Internal helper to ensure logical date ranges.
    Prevents database errors or wasted compute cycles on invalid queries.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after the end date."
        )

def add_new_transaction(db: Session, transaction_in: TransactionCreate, user_id: int) -> Transaction:
    """
    Business logic for adding a transaction.
    Pydantic has already validated the payload, so we delegate to CRUD.
    """
    return crud_transaction.create_transaction(db=db, obj_in=transaction_in, user_id=user_id)

def remove_transaction(db: Session, transaction_id: int, user_id: int) -> dict:
    """
    Secure deletion of a transaction preventing IDOR vulnerabilities.
    """
    # 1. Fetch the transaction first
    txn = crud_transaction.get_transaction(db=db, transaction_id=transaction_id)
    
    # 2. Check if it exists
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Transaction not found."
        )
        
    # 3. SECURITY GUARD: Ensure the user trying to delete it actually owns it
    if txn.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to delete this record."
        )
        
    # 4. If all checks pass, proceed with deletion
    crud_transaction.delete_transaction(db=db, transaction_id=transaction_id)
    return {"message": "Transaction deleted successfully"}

def get_dashboard_data(
    db: Session, 
    user_id: int, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> dict:
    """
    Aggregates all dashboard data into a single, clean JSON response for the frontend.
    """
    # 1. Validate input dates
    _validate_date_range(start_date, end_date)
    
    # 2. Fetch the calculated totals directly from the DB layer
    totals = crud_transaction.get_dashboard_totals(db, user_id, start_date, end_date)
    
    # 3. Fetch category breakdowns
    income_categories = crud_transaction.get_category_wise_totals(db, user_id, "income", start_date, end_date)
    expense_categories = crud_transaction.get_category_wise_totals(db, user_id, "expense", start_date, end_date)
    
    # 4. Construct the final analytical payload
    return {
        "summary": totals,
        "income_by_category": income_categories,
        "expense_by_category": expense_categories
    }