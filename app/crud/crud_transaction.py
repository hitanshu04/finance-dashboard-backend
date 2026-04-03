from sqlalchemy.orm import Session
from sqlalchemy import func 

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from datetime import date
from typing import Optional

def create_transaction(db: Session, obj_in: TransactionCreate, user_id: int) -> Transaction:
    """
    Create a new financial transaction securely linked to a specific user.
    """
    db_obj = Transaction(**obj_in.model_dump(), user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_transaction(db: Session, transaction_id: int) -> Transaction | None:
    """
    Fetch a single transaction by its primary key.
    """
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[Transaction]:
    """
    Fetch transactions for a specific user with pagination.
    """
    return db.query(Transaction).filter(Transaction.user_id == user_id).offset(skip).limit(limit).all()

def delete_transaction(db: Session, transaction_id: int) -> bool:
    """
    Permanently remove a transaction from the database.
    """
    db_obj = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_obj:
        return False
        
    db.delete(db_obj)
    db.commit()
    return True

def get_filtered_transactions(
    db: Session, 
    user_id: int, 
    transaction_type: Optional[str] = None, 
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 50
) -> list[Transaction]:
    """
    Dynamically build a query to filter transactions based on provided criteria.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    return query.offset(skip).limit(limit).all()

# ==========================================
# DASHBOARD AGGREGATORS 
# Complex Analytics Operations
# ==========================================

def get_dashboard_totals(
    db: Session, 
    user_id: int, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> dict:
    """
    Calculate total income, total expense, and net balance directly at the database level.
    This prevents loading thousands of records into application memory.
    """
    # Call SQL level sum() & group_by() 
    query = db.query(
        Transaction.type, 
        func.sum(Transaction.amount).label("total_amount")
    ).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
        
    result = query.group_by(Transaction.type).all()
    
    totals = {"income": 0.0, "expense": 0.0, "net_balance": 0.0}
    
    for row in result:
        txn_type = row[0].lower()
        amount = float(row[1] or 0)
        
        if txn_type == "income":
            totals["income"] = amount
        elif txn_type == "expense":
            totals["expense"] = amount
            
    totals["net_balance"] = totals["income"] - totals["expense"]
    return totals

def get_category_wise_totals(
    db: Session, 
    user_id: int, 
    transaction_type: str,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> list[dict]:
    """
    Calculate total amounts grouped by category (e.g., Food: 500, Rent: 2000).
    Utilizes SQL GROUP BY for maximum performance.
    """
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total_amount")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == transaction_type
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
        
    result = query.group_by(Transaction.category).all()
    
    return [{"category": row[0], "total": float(row[1] or 0)} for row in result]