"""AI client abstraction for multiple providers"""

import time
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from tracker.core.models import DailyEntry

if TYPE_CHECKING:
    from tracker.core.character_sheet import CharacterSheet


class AIClient(ABC):
    """Abstract base class for AI clients"""

    @abstractmethod
    def generate_feedback(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> tuple[str, dict]:
        """
        Generate motivational feedback for an entry
        
        Args:
            entry: DailyEntry to generate feedback for
            character_sheet: Optional character profile for personalized feedback
            profile_context: Optional user profile context for richer personalization
            philosophy_context: Optional philosophy section with guiding principles
            
        Returns:
            Tuple of (feedback_content, metadata_dict)
            metadata includes: model, tokens_used, generation_time
        """
        pass
    
    @abstractmethod
    def generate_chat_response(self, messages: list[dict]) -> tuple[str, dict]:
        """
        Generate a chat response based on message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Tuple of (response_content, metadata_dict)
        """
        pass

    def _build_prompt(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> str:
        """Build motivational feedback prompt from entry data"""
        
        prompt = ""
        
        # Add philosophy context first (sets the wisdom foundation)
        if philosophy_context:
            prompt += philosophy_context + "\n\n---\n\n"
        
        # Add profile context if available (richer than character sheet)
        if profile_context:
            prompt += "# User Profile\n\n"
            
            # Basic preferences
            nickname = profile_context.get("nickname", "friend")
            if nickname:
                prompt += f"Preferred name: {nickname}\n"
            prompt += f"Preferred tone: {profile_context.get('preferred_tone', 'casual')}\n"
            prompt += f"Baseline energy: {profile_context.get('baseline_energy', 5)}/10\n"
            prompt += f"Baseline stress: {profile_context.get('baseline_stress', 5)}/10\n"
            
            # Entry stats
            total_entries = profile_context.get('total_entries', 0)
            streak = profile_context.get('entry_streak', 0)
            if total_entries > 0:
                prompt += f"\nUser has logged {total_entries} entries with a {streak}-day current streak"
                longest = profile_context.get('longest_streak', 0)
                if longest > streak:
                    prompt += f" (best: {longest} days)"
                prompt += ".\n"
            
            # Emotional context
            if profile_context.get('stress_triggers'):
                prompt += f"\nKnown stress triggers: {', '.join(profile_context['stress_triggers'])}\n"
            if profile_context.get('calming_activities'):
                prompt += f"Calming activities: {', '.join(profile_context['calming_activities'])}\n"
            
            # Work & financial context (if personal/deep mode)
            work_info = profile_context.get('work_info')
            if work_info:
                prompt += f"\nWork: {work_info.get('job_title', 'N/A')}"
                if work_info.get('employment_type'):
                    prompt += f" ({work_info['employment_type']})"
                prompt += "\n"
            
            financial_info = profile_context.get('financial_info')
            if financial_info:
                monthly_income = financial_info.get('monthly_income', 0)
                if monthly_income:
                    prompt += f"Monthly income: ~${monthly_income:.2f}\n"
                
                bills = financial_info.get('recurring_bills', [])
                if bills:
                    total_bills = sum(b.get('amount', 0) for b in bills)
                    prompt += f"Recurring bills: ${total_bills:.2f}/month ({len(bills)} bills)\n"
                
                debts = financial_info.get('debts', [])
                if debts:
                    total_debt = sum(d.get('balance', 0) for d in debts)
                    prompt += f"Total debt tracking: ${total_debt:.2f} across {len(debts)} accounts\n"
            
            # Goals
            goals = profile_context.get('goals')
            if goals:
                short_term = goals.get('short_term', [])
                long_term = goals.get('long_term', [])
                if short_term or long_term:
                    prompt += f"\nActive goals: {len(short_term)} short-term, {len(long_term)} long-term\n"
                    if short_term:
                        prompt += "  Recent goals: " + ", ".join([g['goal'] for g in short_term[:2]]) + "\n"
            
            prompt += "\n---\n\n"
        
        # Add character context if available
        elif character_sheet:
            prompt += "# User Character Profile\n\n"
            prompt += character_sheet.to_ai_context()
            prompt += "\n\n---\n\n"
        
        prompt += f"""# Today's Entry

Date: {entry.date}

Financial snapshot:
  - Cash on hand: ${entry.cash_on_hand or 'N/A'}
  - Bank balance: ${entry.bank_balance or 'N/A'}
  - Income today: ${entry.income_today}
  - Bills due: ${entry.bills_due_today}
  - Total debt: ${entry.debts_total or 'N/A'}
  - Side income: ${entry.side_income}

Spending:
  - Food: ${entry.food_spent}
  - Gas: ${entry.gas_spent}

Work:
  - Hours worked: {entry.hours_worked}

Wellbeing:
  - Stress level: {entry.stress_level}/10
  - Priority: {entry.priority or 'N/A'}
"""

        if entry.notes:
            prompt += f"\nJournal: {entry.notes}"

        prompt += """

# Your Task

Generate supportive, empathetic motivational feedback for this daily entry.

## Content Guidelines:
- Be warm, supportive, and genuinely encouraging
- Acknowledge challenges without toxic positivity
- Celebrate wins, even small ones
- Provide perspective on their financial progress
- Keep tone empathetic and non-judgmental
- Focus on effort and resilience, not just outcomes
- End with something uplifting or actionable

## Structure & Formatting:
- Write in 2-4 well-structured paragraphs
- Start each paragraph on a new line for readability
- Use natural paragraph breaks—don't run thoughts together
- Keep paragraphs focused: one main idea per paragraph
- Use **bold** sparingly for key encouragement (1-2 times max)
- Write complete, flowing sentences—avoid bullet points or lists
- Use conversational tone with occasional em-dashes for emphasis

## Suggested Structure:
1. **Acknowledge & Validate** - Reflect on what they did today (good and hard)
2. **Perspective & Insight** - Connect to patterns, progress, or character
3. **Forward Looking** - Encouragement with actionable insight or gentle reminder

## Voice & Tone:
- Sound like a wise, supportive friend who knows their journey
- Be real—don't minimize struggles, but help them see their strength
- Balance honesty with hope
- Use "you" language to make it personal
"""

        if character_sheet:
            prompt += """
## Using Character Profile:
- Reference their known patterns (work style, stress triggers, money wins)
- Acknowledge progress toward stated goals
- Make connections between today's entry and their larger journey
- Show you remember their context (e.g., "You mentioned wanting to...")
"""

        prompt += "\n\nGenerate the motivational feedback now (plain text, no markdown formatting):"

        return prompt


class AnthropicClient(AIClient):
    """Anthropic Claude AI client"""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "claude-3-sonnet-20240229"
        self._client = None

    def _get_client(self):
        """Lazy load Anthropic client"""
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    def generate_feedback(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> tuple[str, dict]:
        """Generate feedback using Claude"""
        
        start_time = time.time()
        
        client = self._get_client()
        prompt = self._build_prompt(entry, character_sheet, profile_context, philosophy_context)
        
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            generation_time = time.time() - start_time
            
            content = response.content[0].text
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
    
    def generate_chat_response(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate chat response using Claude"""
        
        start_time = time.time()
        
        client = self._get_client()
        
        # Convert messages to Anthropic format (system separate from messages)
        system_content = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)
        
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_content,
                messages=chat_messages
            )
            
            generation_time = time.time() - start_time
            
            content = response.content[0].text
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")


class OpenAIClient(AIClient):
    """OpenAI GPT client"""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "gpt-4"
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_feedback(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> tuple[str, dict]:
        """Generate feedback using GPT"""
        
        start_time = time.time()
        
        client = self._get_client()
        prompt = self._build_prompt(entry, character_sheet, profile_context, philosophy_context)
        
        # Determine which parameters to use based on model
        # Newer models (GPT-4, GPT-5, O1, O3) use max_completion_tokens
        # Some models (like O1, O3, reasoning models) don't support temperature or system messages
        
        # Check if this is a reasoning model that doesn't support system messages
        # GPT-5 models appear to have issues with system messages
        is_reasoning_model = self.model and any(x in self.model.lower() for x in ['o1', 'o3', 'reasoning', 'gpt-5'])
        
        # Build messages - reasoning models need user message only
        if is_reasoning_model:
            messages = [
                {
                    "role": "user",
                    "content": f"""You are a supportive financial wellness coach who provides empathetic, non-judgmental encouragement to people tracking their daily finances.

{prompt}"""
                }
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": "You are a supportive financial wellness coach who provides empathetic, non-judgmental encouragement to people tracking their daily finances."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        
        params = {
            "model": self.model,
            "messages": messages,
        }
        
        # Add token limit parameter based on model
        if self.model and any(x in self.model.lower() for x in ['gpt-4', 'gpt-5', 'o1', 'o3']):
            params["max_completion_tokens"] = 500
        else:
            params["max_tokens"] = 500
        
        # Add temperature only for models that support it (not O1/O3/reasoning/nano/mini models)
        if not (self.model and any(x in self.model.lower() for x in ['o1', 'o3', 'reasoning', 'nano', 'mini', 'gpt-5'])):
            params["temperature"] = 0.7
        
        try:
            response = client.chat.completions.create(**params)
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            # Handle None/empty responses
            if not content:
                content = "No feedback generated. Please try again or use a different model."
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def generate_chat_response(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate chat response using GPT"""
        
        start_time = time.time()
        
        client = self._get_client()
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            if not content:
                content = "No response generated."
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")


class OpenRouterClient(AIClient):
    """OpenRouter client (100+ models via unified API)"""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "anthropic/claude-3.5-sonnet"
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client with OpenRouter base URL"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        return self._client

    def generate_feedback(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> tuple[str, dict]:
        """Generate feedback using OpenRouter"""
        
        start_time = time.time()
        
        client = self._get_client()
        prompt = self._build_prompt(entry, character_sheet, profile_context, philosophy_context)
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a supportive financial wellness coach who provides empathetic, non-judgmental encouragement to people tracking their daily finances."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}")
    
    def generate_chat_response(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate chat response using OpenRouter"""
        
        start_time = time.time()
        
        client = self._get_client()
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}")


class LocalClient(AIClient):
    """Local AI client (Ollama, LM Studio, llama.cpp)"""

    def __init__(self, base_url: str = "http://localhost:1234/v1", model: Optional[str] = None):
        self.base_url = base_url
        self.model = model or "local-model"
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client with local base URL"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key="not-needed",
                base_url=self.base_url
            )
        return self._client

    def generate_feedback(
        self, 
        entry: DailyEntry, 
        character_sheet: Optional["CharacterSheet"] = None,
        profile_context: Optional[dict] = None,
        philosophy_context: Optional[str] = None
    ) -> tuple[str, dict]:
        """Generate feedback using local AI server"""
        
        start_time = time.time()
        
        client = self._get_client()
        prompt = self._build_prompt(entry, character_sheet, profile_context, philosophy_context)
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a supportive financial wellness coach who provides empathetic, non-judgmental encouragement to people tracking their daily finances."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"Local AI server error: {e}")
    
    def generate_chat_response(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate chat response using local AI server"""
        
        start_time = time.time()
        
        client = self._get_client()
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            
            generation_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "generation_time": generation_time,
            }
            
            return content, metadata
            
        except Exception as e:
            raise RuntimeError(f"Local AI server error: {e}")


def create_ai_client(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    local_api_url: Optional[str] = None
) -> AIClient:
    """
    Factory function to create AI client
    
    Args:
        provider: 'openai', 'anthropic', 'openrouter', or 'local'
        api_key: API key for the provider (not needed for local)
        model: Optional model name override
        local_api_url: Base URL for local provider (default: http://localhost:1234/v1)
        
    Returns:
        AIClient instance
        
    Raises:
        ValueError: If provider is not supported or required parameters missing
    """
    
    provider = provider.lower()
    
    if provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic API key is required")
        return AnthropicClient(api_key, model)
    
    elif provider == "openai":
        if not api_key:
            raise ValueError("OpenAI API key is required")
        return OpenAIClient(api_key, model)
    
    elif provider == "openrouter":
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        return OpenRouterClient(api_key, model)
    
    elif provider == "local":
        base_url = local_api_url or "http://localhost:1234/v1"
        return LocalClient(base_url, model)
    
    else:
        raise ValueError(
            f"Unsupported AI provider: {provider}. "
            f"Supported providers: openai, anthropic, openrouter, local"
        )
