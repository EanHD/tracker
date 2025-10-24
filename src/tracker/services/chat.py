"""Chat service for managing AI conversations"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from tracker.core.models import Chat, ChatMessage, DailyEntry, UserProfile
from tracker.services.ai_client import create_ai_client
from tracker.config import settings


class ChatService:
    """Service for managing chat conversations"""
    
    def __init__(self, session: Session, user_id: int):
        self.session = session
        self.user_id = user_id
        
        # Get the correct model based on provider
        model = settings.ai_model
        if settings.ai_provider == "local":
            model = settings.local_model or model
        elif settings.ai_provider == "anthropic":
            model = settings.anthropic_model or model
        elif settings.ai_provider == "openai":
            model = settings.openai_model or model
        elif settings.ai_provider == "openrouter":
            model = settings.openrouter_model or model
        
        self.ai_client = create_ai_client(
            provider=settings.ai_provider,
            api_key=settings.get_ai_api_key(),
            model=model,
            local_api_url=settings.local_api_url
        )
    
    def create_chat(self, title: str, entry_id: Optional[int] = None) -> Chat:
        """Create a new chat conversation"""
        chat = Chat(
            user_id=self.user_id,
            entry_id=entry_id,
            title=title
        )
        self.session.add(chat)
        self.session.commit()
        return chat
    
    def get_or_create_entry_chat(self, entry_id: int) -> Chat:
        """Get existing chat for entry or create new one"""
        # Check if chat exists for this entry
        existing_chat = self.session.query(Chat).filter_by(
            user_id=self.user_id,
            entry_id=entry_id
        ).first()
        
        if existing_chat:
            return existing_chat
        
        # Get entry to generate title
        entry = self.session.query(DailyEntry).filter_by(id=entry_id).first()
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        
        title = f"Chat: {entry.date.strftime('%B %d, %Y')}"
        return self.create_chat(title=title, entry_id=entry_id)
    
    def list_chats(self, limit: int = 50, entry_linked: Optional[bool] = None) -> List[Chat]:
        """List user's chats, optionally filtered by entry linkage"""
        query = self.session.query(Chat).filter_by(user_id=self.user_id)
        
        if entry_linked is True:
            query = query.filter(Chat.entry_id.isnot(None))
        elif entry_linked is False:
            query = query.filter(Chat.entry_id.is_(None))
        
        return query.order_by(desc(Chat.updated_at)).limit(limit).all()
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get a specific chat with messages"""
        return self.session.query(Chat).options(
            joinedload(Chat.messages)
        ).filter_by(
            id=chat_id,
            user_id=self.user_id
        ).first()
    
    def add_message(self, chat_id: int, role: str, content: str) -> ChatMessage:
        """Add a message to a chat"""
        message = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content
        )
        self.session.add(message)
        
        # Update chat's updated_at
        chat = self.session.query(Chat).filter_by(id=chat_id).first()
        if chat:
            chat.updated_at = datetime.utcnow()
        
        self.session.commit()
        return message
    
    def delete_chat(self, chat_id: int) -> bool:
        """Delete a chat and all its messages"""
        chat = self.session.query(Chat).filter_by(
            id=chat_id,
            user_id=self.user_id
        ).first()
        
        if not chat:
            return False
        
        self.session.delete(chat)
        self.session.commit()
        return True
    
    def get_context_for_chat(self, chat: Chat) -> str:
        """Build context string from user profile, recent entries, and current entry if linked"""
        from datetime import date, timedelta
        
        context_parts = []
        
        # Get user profile
        profile = self.session.query(UserProfile).filter_by(user_id=self.user_id).first()
        if profile:
            context_parts.append("# User Profile")
            if profile.nickname:
                context_parts.append(f"Name: {profile.nickname}")
            if profile.preferred_tone:
                context_parts.append(f"Preferred Tone: {profile.preferred_tone}")
            if profile.context_depth:
                context_parts.append(f"Context Depth: {profile.context_depth}")
            if profile.stress_triggers:
                context_parts.append(f"Stress Triggers: {profile.stress_triggers}")
            if profile.calming_activities:
                context_parts.append(f"Calming Activities: {profile.calming_activities}")
            context_parts.append("")
        
        # Get recent entries (last 7 days) for pattern context
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        recent_entries = self.session.query(DailyEntry).filter(
            DailyEntry.user_id == self.user_id,
            DailyEntry.date >= start_date,
            DailyEntry.date <= end_date
        ).order_by(DailyEntry.date.desc()).limit(7).all()
        
        if recent_entries and not chat.entry_id:  # Only add summary if not entry-specific
            context_parts.append("# Recent Activity (Last 7 Days)")
            avg_stress = sum(e.stress_level for e in recent_entries) / len(recent_entries)
            total_income = sum(e.income_today + e.side_income for e in recent_entries)
            total_expenses = sum(e.bills_due_today + e.food_spent + e.gas_spent for e in recent_entries)
            
            context_parts.append(f"Entries logged: {len(recent_entries)}")
            context_parts.append(f"Average stress: {avg_stress:.1f}/10")
            context_parts.append(f"Total income: ${total_income:.2f}")
            context_parts.append(f"Total expenses: ${total_expenses:.2f}")
            context_parts.append(f"Net: ${total_income - total_expenses:.2f}")
            context_parts.append("")
        
        # If chat is linked to an entry, include detailed entry context
        if chat.entry_id:
            entry = self.session.query(DailyEntry).filter_by(id=chat.entry_id).first()
            if entry:
                context_parts.append(f"# Today's Journal Entry: {entry.date.strftime('%B %d, %Y')}")
                context_parts.append("")
                context_parts.append("## Financial")
                context_parts.append(f"Income Today: ${entry.income_today:.2f}")
                context_parts.append(f"Side Income: ${entry.side_income:.2f}")
                context_parts.append(f"Bills Due: ${entry.bills_due_today:.2f}")
                context_parts.append(f"Food Spending: ${entry.food_spent:.2f}")
                context_parts.append(f"Gas Spending: ${entry.gas_spent:.2f}")
                total_income = entry.income_today + entry.side_income
                total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
                context_parts.append(f"Net Balance: ${total_income - total_expenses:.2f}")
                context_parts.append("")
                context_parts.append("## Work & Wellbeing")
                context_parts.append(f"Hours Worked: {entry.hours_worked}")
                context_parts.append(f"Stress Level: {entry.stress_level}/10")
                if entry.priority:
                    context_parts.append(f"Priority Task: {entry.priority}")
                if entry.notes:
                    context_parts.append(f"\nJournal Notes:\n{entry.notes}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def send_message(self, chat_id: int, user_message: str) -> str:
        """Send a message and get AI response"""
        chat = self.get_chat(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")
        
        # Add user message
        self.add_message(chat_id, "user", user_message)
        
        # Build conversation history
        messages = []
        
        # Add system context
        context = self.get_context_for_chat(chat)
        system_message = "You are Tracker, a supportive AI companion helping the user with their daily reflections, wellbeing, and personal growth. Be empathetic, insightful, and encouraging. Use the provided context about their profile and journal entries to personalize your responses."
        
        if context:
            messages.append({
                "role": "system",
                "content": f"{context}\n\n{system_message}"
            })
        else:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add chat history
        for msg in chat.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Get AI response
        response_content, metadata = self.ai_client.generate_chat_response(messages)
        
        # Add AI response to chat
        self.add_message(chat_id, "assistant", response_content)
        
        return response_content
    
    def update_chat_title(self, chat_id: int, new_title: str) -> bool:
        """Update a chat's title"""
        chat = self.session.query(Chat).filter_by(
            id=chat_id,
            user_id=self.user_id
        ).first()
        
        if not chat:
            return False
        
        chat.title = new_title
        self.session.commit()
        return True
    
    def generate_chat_title(self, chat_id: int) -> str:
        """Auto-generate a descriptive title based on chat content"""
        chat = self.get_chat(chat_id)
        if not chat or not chat.messages:
            return "New Conversation"
        
        # Get first few messages for context
        first_messages = chat.messages[:3]
        content_summary = " ".join([msg.content[:100] for msg in first_messages])
        
        messages = [
            {"role": "user", "content": f"Generate a short, descriptive title (max 6 words) for this conversation:\n{content_summary}"}
        ]
        
        title, _ = self.ai_client.generate_chat_response(messages)
        return title.strip().strip('"\'')
