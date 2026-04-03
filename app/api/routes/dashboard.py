from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.services import transaction_service
from app.api.dependencies import RoleChecker
from app.models.user import User

# Initialize the router for dashboard-related endpoints
router = APIRouter()

# Analysts can access summaries. Admins have full access.
# Viewers are explicitly blocked from accessing this high-level aggregated data.
allow_admin_analyst = RoleChecker(["Admin", "Analyst"])

# -----------------------------------------------------------------------------
# GET: Fetch Dashboard Summary (Backend For Frontend Pattern)
# -----------------------------------------------------------------------------
@router.get(
    "/summary", 
    status_code=status.HTTP_200_OK
)
def get_dashboard_summary(
    start_date: Optional[date] = Query(None, description="Filter summary from this date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter summary up to this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_analyst)
):
    """
    Fetch a complete, aggregated dashboard summary for the authenticated user.
    SECURITY: Restricted to Admin and Analyst roles only.
    This endpoint implements the Backend-For-Frontend (BFF) pattern by returning
    a single, highly optimized JSON payload containing multiple data points.
    """
    # Delegate the request to the service layer which handles date validation 
    # and multiple optimized database queries.
    return transaction_service.get_dashboard_data(
        db=db, 
        user_id=current_user.id, 
        start_date=start_date, 
        end_date=end_date
    )