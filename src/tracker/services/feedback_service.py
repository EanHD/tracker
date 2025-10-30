"""Feedback service - AI feedback generation and management"""

import asyncio
import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from tracker.core.models import AIFeedback, DailyEntry
from tracker.services.ai_client import create_ai_client
from tracker.services.character_service import CharacterSheetService
from tracker.services.profile_service import ProfileService
from tracker.services.philosophy_context_service import PhilosophyContextService


class FeedbackService:
    """Service for managing AI feedback generation"""

    def __init__(self, db: Session):
        self.db = db

    def create_feedback(
        self,
        entry_id: int,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        local_api_url: Optional[str] = None
    ) -> AIFeedback:
        """
        Create a feedback record and initiate generation
        
        Args:
            entry_id: ID of the entry to generate feedback for
            provider: AI provider ('openai', 'anthropic', 'openrouter', or 'local')
            api_key: API key for the provider (not needed for local)
            model: Optional model name override
            local_api_url: Base URL for local provider
            
        Returns:
            AIFeedback record with status='pending'
        """
        
        # Check if feedback already exists
        existing = self.db.query(AIFeedback).filter(
            AIFeedback.entry_id == entry_id
        ).first()
        
        if existing:
            # Update existing feedback to pending for regeneration
            existing.status = "pending"
            existing.provider = provider
            existing.model = model
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        
        # Create new feedback record
        feedback = AIFeedback(
            entry_id=entry_id,
            content="",  # Will be updated when generation completes
            status="pending",
            provider=provider,
            model=model,
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return feedback

    def generate_feedback_sync(
        self,
        feedback_id: int,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        local_api_url: Optional[str] = None,
        max_retries: int = 3
    ) -> AIFeedback:
        """
        Generate feedback synchronously with retries
        
        Args:
            feedback_id: ID of the feedback record
            provider: AI provider name ('openai', 'anthropic', 'openrouter', 'local')
            api_key: API key (not needed for local)
            model: Optional model override
            local_api_url: Base URL for local provider
            max_retries: Maximum number of retry attempts
            
        Returns:
            Updated AIFeedback record
        """
        
        feedback = self.db.query(AIFeedback).filter(AIFeedback.id == feedback_id).first()
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")
        
        # Get the entry
        entry = self.db.query(DailyEntry).filter(DailyEntry.id == feedback.entry_id).first()
        if not entry:
            feedback.status = "failed"
            feedback.error_message = "Entry not found"
            self.db.commit()
            raise ValueError(f"Entry {feedback.entry_id} not found")
        
        # Try to generate with retries
        for attempt in range(max_retries):
            try:
                # Create AI client
                ai_client = create_ai_client(
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    local_api_url=local_api_url
                )
                
                # Load character sheet for personalized feedback
                character_service = CharacterSheetService(self.db)
                try:
                    character_sheet = character_service.analyze_and_update_profile(
                        user_id=entry.user_id,
                        lookback_days=30
                    )
                except Exception as e:
                    # If character sheet fails, continue without it
                    # (allows system to work before profile is built)
                    character_sheet = None
                
                # Load user profile for rich context
                profile_service = ProfileService(self.db)
                try:
                    profile_context = profile_service.get_ai_context(entry.user_id)
                    # Update entry stats
                    profile_service.update_entry_stats(entry.user_id, entry.date)
                    
                    # ADD ALL NEW MEMORY LAYERS
                    profile_context["recent_summary"] = profile_service.get_recent_entry_summary(entry.user_id, days=7)
                    profile_context["recent_wins"] = profile_service.get_recent_wins(entry.user_id, days=30)
                    profile_context["weekly_patterns"] = profile_service.get_weekly_patterns(entry.user_id, lookback_days=42)
                    profile_context["momentum"] = profile_service.get_momentum_context(entry.user_id, entry)
                    profile_context["milestones"] = profile_service.get_milestone_context(entry.user_id, days=30)
                    profile_context["field_consistency"] = profile_service.get_field_consistency(entry.user_id, days=30)
                    profile_context["journal_sentiment"] = profile_service.get_journal_sentiment(entry.user_id, days=30)
                    
                except Exception:
                    profile_context = {}
                
                # Load philosophy context for wisdom-based guidance
                philosophy_service = PhilosophyContextService(self.db)
                try:
                    philosophy_context = philosophy_service.generate_philosophy_prompt_section(
                        entry.user_id,
                        current_entry=entry
                    )
                except Exception:
                    philosophy_context = ""
                
                # Generate feedback with character context, profile, and philosophy
                content, metadata = ai_client.generate_feedback(
                    entry, 
                    character_sheet,
                    profile_context=profile_context,
                    philosophy_context=philosophy_context
                )
                
                # Update feedback record
                feedback.content = content
                feedback.status = "completed"
                feedback.provider = provider
                feedback.model = metadata.get("model")
                feedback.tokens_used = metadata.get("tokens_used")
                feedback.generation_time = metadata.get("generation_time")
                feedback.error_message = None
                feedback.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(feedback)
                
                return feedback
                
            except Exception as e:
                # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 16)  # Cap at 16 seconds
                    time.sleep(wait_time)
                    continue
                
                # Final attempt failed
                feedback.status = "failed"
                feedback.error_message = str(e)
                feedback.updated_at = datetime.utcnow()
                self.db.commit()
                
                raise RuntimeError(f"Failed to generate feedback after {max_retries} attempts: {e}")
        
        return feedback

    def get_feedback_by_entry(self, entry_id: int) -> Optional[AIFeedback]:
        """Get feedback for an entry"""
        return self.db.query(AIFeedback).filter(AIFeedback.entry_id == entry_id).first()

    def get_feedback_by_id(self, feedback_id: int) -> Optional[AIFeedback]:
        """Get feedback by ID"""
        return self.db.query(AIFeedback).filter(AIFeedback.id == feedback_id).first()

    def delete_feedback(self, feedback_id: int) -> bool:
        """Delete feedback"""
        feedback = self.get_feedback_by_id(feedback_id)
        if not feedback:
            return False
        
        self.db.delete(feedback)
        self.db.commit()
        return True

    def regenerate_feedback(
        self,
        entry_id: int,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        local_api_url: Optional[str] = None
    ) -> AIFeedback:
        """
        Regenerate feedback for an entry
        
        Args:
            entry_id: ID of the entry
            provider: AI provider ('openai', 'anthropic', 'openrouter', 'local')
            api_key: API key (not needed for local)
            model: Optional model override
            local_api_url: Base URL for local provider
            
        Returns:
            Updated AIFeedback record
        """
        
        # Create or update feedback record
        feedback = self.create_feedback(entry_id, provider, api_key, model, local_api_url)
        
        # Generate synchronously
        return self.generate_feedback_sync(
            feedback.id,
            provider,
            api_key,
            model,
            local_api_url
        )

    def generate_feedback(
        self,
        entry_id: int,
        regenerate: bool = False,
    ) -> AIFeedback:
        """
        Convenience method to generate feedback using config from environment
        
        Args:
            entry_id: ID of the entry
            regenerate: Whether to regenerate existing feedback
            
        Returns:
            AIFeedback record
            
        Raises:
            ValueError: If AI configuration is missing or invalid
        """
        from tracker.config import settings
        
        # Validate config
        provider = settings.ai_provider or "local"
        
        # Check API key for non-local providers
        if provider != "local":
            api_key = settings.get_ai_api_key()
            if not api_key:
                raise ValueError(
                    f"API key required for provider '{provider}'.\n"
                    f"Set {provider.upper()}_API_KEY in your .env file or run: tracker config setup"
                )
        else:
            api_key = None
        
        # Get model - check provider-specific env vars first, then fallback to ai_model
        model = settings.ai_model
        if provider == "local":
            model = settings.local_model or model
            if not model:
                raise ValueError(
                    "LOCAL_MODEL not configured.\n"
                    "Set LOCAL_MODEL in your .env file or run: tracker config setup"
                )
        elif provider == "anthropic":
            model = settings.anthropic_model or model
        elif provider == "openai":
            model = settings.openai_model or model
        elif provider == "openrouter":
            model = settings.openrouter_model or model
        
        local_api_url = settings.local_api_url or "http://localhost:11434/v1"
        
        # Check if feedback exists
        if not regenerate:
            existing = self.get_feedback_by_entry(entry_id)
            if existing and existing.status == "completed":
                return existing
        
        # Generate or regenerate
        try:
            return self.regenerate_feedback(
                entry_id=entry_id,
                provider=provider,
                api_key=api_key,
                model=model,
                local_api_url=local_api_url
            )
        except ValueError:
            # Re-raise configuration errors
            raise
        except Exception as e:
            # Wrap other errors with helpful context
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg:
                raise ValueError(
                    f"Model '{model}' not found for provider '{provider}'.\n"
                    f"Check your model name or run: tracker config setup"
                )
            elif "401" in error_msg or "authentication" in error_msg.lower():
                raise ValueError(
                    f"Authentication failed for provider '{provider}'.\n"
                    f"Check your API key or run: tracker config setup"
                )
            else:
                # Re-raise original exception
                raise

