"""Feedback endpoints"""

from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from tracker.api.dependencies import get_current_user
from tracker.config import settings
from tracker.core.database import get_db
from tracker.core.models import User
from tracker.core.schemas import FeedbackResponse
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Request to generate feedback"""
    entry_date: date
    regenerate: bool = False


@router.post("/generate", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def generate_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI feedback for an entry
    
    Creates feedback record in 'pending' status and generates in background
    """
    # Check AI is configured
    api_key = settings.get_ai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider not configured"
        )
    
    # Get entry
    entry_service = EntryService(db)
    entry = entry_service.get_entry_by_date(current_user.id, request.entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry found for {request.entry_date}"
        )
    
    # Check if feedback already exists
    feedback_service = FeedbackService(db)
    existing = feedback_service.get_feedback_by_entry(entry.id)
    
    if existing and not request.regenerate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feedback already exists. Set regenerate=true to regenerate."
        )
    
    # Create feedback record
    feedback = feedback_service.create_feedback(
        entry.id,
        settings.ai_provider,
        api_key,
        settings.ai_model
    )
    
    # Generate in background (synchronously for now, async in future)
    try:
        feedback = feedback_service.generate_feedback_sync(
            feedback.id,
            settings.ai_provider,
            api_key,
            settings.ai_model
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )
    
    return feedback


@router.get("/{entry_date}", response_model=FeedbackResponse)
def get_feedback(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback for a specific entry
    
    Returns 404 if feedback doesn't exist
    """
    # Get entry
    entry_service = EntryService(db)
    entry = entry_service.get_entry_by_date(current_user.id, entry_date)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry found for {entry_date}"
        )
    
    # Get feedback
    feedback_service = FeedbackService(db)
    feedback = feedback_service.get_feedback_by_entry(entry.id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for entry on {entry_date}"
        )
    
    return feedback
