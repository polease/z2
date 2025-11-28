"""
Statistics API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import StatsResponse
from ..services.job_service import JobService

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("", response_model=StatsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get platform statistics

    Returns counts of jobs by status and average duration
    """
    return JobService.get_statistics(db)
