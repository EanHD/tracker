"""Entry endpoints"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from tracker.api.dependencies import get_current_user
from tracker.core.database import get_db
from tracker.core.models import User
from tracker.core.schemas import EntryCreate, EntryUpdate, EntryResponse
from tracker.services.entry_service import EntryService

router = APIRouter()


@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry_data: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new daily entry
    
    Requires authentication. One entry per user per date.
    """
    service = EntryService(db)
    
    try:
        entry = service.create_entry(current_user.id, entry_data)
        return entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[EntryResponse])
def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List entries for current user
    
    Supports pagination and date range filtering
    """
    from tracker.core.models import DailyEntry
    
    # Build query for user's entries
    query = db.query(DailyEntry).filter(DailyEntry.user_id == current_user.id)
    
    # Apply date filters
    if start_date:
        query = query.filter(DailyEntry.date >= start_date)
    if end_date:
        query = query.filter(DailyEntry.date <= end_date)
    
    # Order by date descending (most recent first)
    query = query.order_by(DailyEntry.date.desc())
    
    # Pagination
    entries = query.offset(skip).limit(limit).all()
    
    return entries


@router.get("/{entry_date}", response_model=EntryResponse)
def get_entry(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get entry for a specific date
    
    Returns 404 if entry doesn't exist for that date
    """
    service = EntryService(db)
    
    entry = service.get_entry_by_date(current_user.id, entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry found for {entry_date}"
        )
    
    return entry


@router.patch("/{entry_date}", response_model=EntryResponse)
def update_entry(
    entry_date: date,
    entry_data: EntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update entry for a specific date
    
    Allows partial updates. Only provided fields will be changed.
    Returns 404 if entry doesn't exist.
    
    If substantial changes are made (stress_level, income, bills, hours, notes, priority),
    consider regenerating feedback via the feedback endpoint.
    """
    service = EntryService(db)
    
    # Get existing entry
    entry = service.get_entry_by_date(current_user.id, entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry found for {entry_date}"
        )
    
    # Update entry using service method with user authorization
    try:
        updated_entry = service.update_entry(entry.id, entry_data, user_id=current_user.id)
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry not found"
            )
        return updated_entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{entry_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete entry for a specific date
    
    Returns 404 if entry doesn't exist
    """
    service = EntryService(db)
    
    entry = service.get_entry_by_date(current_user.id, entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry found for {entry_date}"
        )
    
    success = service.delete_entry(entry.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete entry"
        )
    
    return None
