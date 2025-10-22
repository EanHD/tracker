"""Export API endpoints"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from tracker.api.dependencies import get_current_user
from tracker.core.database import get_db
from tracker.core.models import User
from tracker.services.export_service import ExportService

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/csv")
def export_csv(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export entries to CSV format
    
    Returns CSV file with all entry data. Suitable for Excel, Google Sheets, etc.
    """
    service = ExportService(db)
    
    csv_content = service.export_to_csv(
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Return as downloadable file
    filename = f"tracker_export_{date.today().isoformat()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/json")
def export_json(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    pretty: bool = Query(True, description="Pretty-print JSON"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export entries to JSON format
    
    Returns structured JSON with entry data. Suitable for backup and data portability.
    """
    service = ExportService(db)
    
    json_content = service.export_to_json(
        current_user.id,
        start_date=start_date,
        end_date=end_date,
        pretty=pretty
    )
    
    # Return as downloadable file
    filename = f"tracker_export_{date.today().isoformat()}.json"
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stats")
def export_stats(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about what would be exported
    
    Useful for checking export size before downloading.
    """
    service = ExportService(db)
    
    stats = service.get_export_stats(
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats
