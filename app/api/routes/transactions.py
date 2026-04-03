from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services import transaction_service
from app.crud import crud_transaction
from app.api.dependencies import RoleChecker
from app.models.user import User

router = APIRouter()

# Admin has FULL access (Create, Delete)
require_admin = RoleChecker(["Admin"])

# Analyst and Admin can access higher-level reads (Summaries/Dashboards - used in next step)
allow_admin_analyst = RoleChecker(["Admin", "Analyst"])

# Everyone can at least read their basic transaction records
allow_all_roles = RoleChecker(["Admin", "Analyst", "Viewer"])

# -----------------------------------------------------------------------------
# POST: Create a new transaction
# -----------------------------------------------------------------------------
@router.post(
    "/", 
    response_model=TransactionResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    # Strictly Admin only!
    current_user: User = Depends(require_admin) 
):
    """
    Create a new financial transaction.
    SECURITY FIX: Strictly accessible ONLY to the 'Admin' role as per requirements.
    """
    return transaction_service.add_new_transaction(
        db=db, 
        transaction_in=transaction_in, 
        user_id=current_user.id
    )

# -----------------------------------------------------------------------------
# GET: Fetch and filter transactions
# -----------------------------------------------------------------------------
@router.get(
    "/", 
    response_model=list[TransactionResponse],
    status_code=status.HTTP_200_OK
)
def get_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by 'income' or 'expense'"),
    category: Optional[str] = Query(None, description="Exact match filter for category"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
    # ALL roles can read basic records
    current_user: User = Depends(allow_all_roles) 
):
    """
    Fetch a list of transactions belonging to the authenticated user.
    SECURITY: Viewers, Analysts, and Admins can read records.
    """
    return crud_transaction.get_filtered_transactions(
        db=db,
        user_id=current_user.id,
        transaction_type=transaction_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

# -----------------------------------------------------------------------------
# DELETE: Remove a transaction
# -----------------------------------------------------------------------------
@router.delete(
    "/{transaction_id}", 
    status_code=status.HTTP_200_OK
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    # Strictly Admin only!
    current_user: User = Depends(require_admin) 
):
    """
    Permanently delete a transaction by its ID.
    SECURITY FIX: Accessible ONLY to the 'Admin' role.
    """
    return transaction_service.remove_transaction(
        db=db, 
        transaction_id=transaction_id, 
        user_id=current_user.id
    )