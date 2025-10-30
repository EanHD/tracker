"""Natural language financial command parser

Safely interprets financial changes from natural language without AI branding.
Uses pattern matching and entity resolution.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from tracker.config import get_config_dir
from tracker.core.models import User, UserProfile
from tracker.services.cashflow_config import (
    CashFlowConfig,
    Installment,
    RecurringWeeklyRule,
    load_config,
    save_config,
)


# Entity aliases for fuzzy matching
ACCOUNT_ALIASES = {
    "slate": "Chase Slate",
    "chase slate": "Chase Slate",
    "freedom": "Chase Freedom",
    "chase freedom": "Chase Freedom",
    "flex": "Chase Flex",
    "chase flex": "Chase Flex",
    "bestbuy": "Best Buy",
    "best buy": "Best Buy",
    "creditone": "Credit One",
    "credit one": "Credit One",
    "westlake": "WestLake",
    "carecredit": "Care Credit",
    "care credit": "Care Credit",
    "snapon": "Snap-On",
    "snap-on": "Snap-On",
    "snap on": "Snap-On",
    "carmax": "CarMax",
    "essex": "Essex",
    "bestegg": "BestEgg",
    "best egg": "BestEgg",
}

RECURRING_ALIASES = {
    "earnin": "EarnIn",
    "earn in": "EarnIn",
    "snapon": "SnapOn",
    "snap-on": "SnapOn",
    "snap on": "SnapOn",
    "chase transfer": "ChaseTransfer",
    "netflix": "Netflix",
    "disney": "Disney+",
    "disney+": "Disney+",
    "paramount": "Paramount+",
    "paramount+": "Paramount+",
    "spotify": "Spotify",
    "youtube": "YouTube",
    "tmobile": "T-Mobile",
    "t-mobile": "T-Mobile",
    "verizon": "Verizon",
}

PROVIDER_ALIASES = {
    "affirm": "affirm",
    "klarna": "klarna",
    "autozone": "autozone",
    "auto zone": "autozone",
    "oreilly": "oreilly",
    "o'reilly": "oreilly",
}


@dataclass
class ParsedIntent:
    """Parsed intent from natural language"""
    action: str  # payoff, close, change_amount, defer, add_installment, cancel
    entity_type: str  # debt, recurring, installment, subscription
    entity_name: str  # Resolved name
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    ambiguous: bool = False
    alternatives: list[str] = field(default_factory=list)


@dataclass
class AdjustmentDiff:
    """Diff preview of proposed changes"""
    intent: ParsedIntent
    before: dict[str, Any]
    after: dict[str, Any]
    changes: list[str]  # Human-readable change descriptions
    warnings: list[str] = field(default_factory=list)
    safe: bool = True


@dataclass
class AuditRecord:
    """Audit log of applied adjustment"""
    timestamp: str
    user_text: str
    parsed_intent: dict
    resolved_entities: dict
    before_snapshot: dict
    after_snapshot: dict
    changes_applied: list[str]
    audit_id: str


def normalize_text(text: str) -> str:
    """Normalize text for matching"""
    return text.lower().strip()


def resolve_entity(text: str, entity_type: str) -> tuple[Optional[str], list[str]]:
    """Resolve entity name from text with fuzzy matching
    
    Args:
        text: Input text containing entity reference
        entity_type: Type of entity (debt, recurring, provider)
    
    Returns:
        Tuple of (resolved_name, alternatives)
    """
    normalized = normalize_text(text)
    
    if entity_type == "debt":
        aliases = ACCOUNT_ALIASES
    elif entity_type == "recurring":
        aliases = RECURRING_ALIASES
    elif entity_type == "provider":
        aliases = PROVIDER_ALIASES
    else:
        return None, []
    
    # Exact match
    if normalized in aliases:
        return aliases[normalized], []
    
    # Partial match
    matches = []
    for alias, canonical in aliases.items():
        if alias in normalized or normalized in alias:
            matches.append(canonical)
    
    if len(matches) == 1:
        return matches[0], []
    elif len(matches) > 1:
        return matches[0], matches[1:]  # Return best match + alternatives
    
    return None, []


def extract_amount(text: str) -> Optional[Decimal]:
    """Extract dollar amount from text"""
    # Match patterns like: $150, 150, 150.00, $150.00
    patterns = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd)',  # 1234.56 dollars
        r'\b(\d+(?:\.\d{2})?)\b',  # 150.00
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return Decimal(amount_str)
            except:
                continue
    
    return None


def extract_date(text: str) -> Optional[date]:
    """Extract date from text"""
    # Match YYYY-MM-DD
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except:
            pass
    
    # Match relative dates
    if "next week" in normalize_text(text):
        return date.today() + timedelta(days=7)
    elif "tomorrow" in normalize_text(text):
        return date.today() + timedelta(days=1)
    
    return None


def parse_command(text: str) -> ParsedIntent:
    """Parse natural language financial command
    
    Args:
        text: User's natural language command
    
    Returns:
        ParsedIntent with action, entity, and parameters
    """
    normalized = normalize_text(text)
    
    # Pattern: "paid off X" or "pay off X" or "close X"
    if any(phrase in normalized for phrase in ["paid off", "pay off", "close", "closed"]):
        # Extract entity
        for debt_alias in ACCOUNT_ALIASES.keys():
            if debt_alias in normalized:
                resolved, alternatives = resolve_entity(debt_alias, "debt")
                if resolved:
                    return ParsedIntent(
                        action="payoff",
                        entity_type="debt",
                        entity_name=resolved,
                        parameters={"set_balance": 0, "mark_closed": True},
                        ambiguous=len(alternatives) > 0,
                        alternatives=alternatives,
                    )
    
    # Pattern: "lower X to Y" or "change X to Y" or "set X to Y"
    if any(phrase in normalized for phrase in ["lower", "change", "set", "update"]):
        amount = extract_amount(text)
        if amount:
            effective_date = extract_date(text) or date.today()
            # Check for recurring bills
            for alias in RECURRING_ALIASES.keys():
                if alias in normalized:
                    resolved, alternatives = resolve_entity(alias, "recurring")
                    if resolved:
                        return ParsedIntent(
                            action="change_amount",
                            entity_type="recurring",
                            entity_name=resolved,
                            parameters={
                                "new_amount": float(amount),
                                "effective_date": effective_date.isoformat(),
                            },
                            ambiguous=len(alternatives) > 0,
                            alternatives=alternatives,
                        )
    
    # Pattern: "defer X" or "postpone X"
    if any(phrase in normalized for phrase in ["defer", "postpone", "delay"]):
        # Extract duration
        days = 7  # Default to one week
        if "one week" in normalized or "1 week" in normalized:
            days = 7
        elif "two week" in normalized or "2 week" in normalized:
            days = 14
        
        # Find entity
        for alias in ACCOUNT_ALIASES.keys():
            if alias in normalized:
                resolved, alternatives = resolve_entity(alias, "debt")
                if resolved:
                    return ParsedIntent(
                        action="defer",
                        entity_type="debt",
                        entity_name=resolved,
                        parameters={"delay_days": days},
                        ambiguous=len(alternatives) > 0,
                        alternatives=alternatives,
                    )
    
    # Pattern: "add installment" or "add klarna"
    if "add" in normalized and any(p in normalized for p in ["installment", "klarna", "affirm"]):
        amount = extract_amount(text)
        payment_date = extract_date(text)
        
        # Find provider
        provider = "klarna"  # Default
        for alias in PROVIDER_ALIASES.keys():
            if alias in normalized:
                resolved_provider, _ = resolve_entity(alias, "provider")
                if resolved_provider:
                    provider = resolved_provider
                break
        
        # Extract name (e.g., "AutoZone", "O'Reilly")
        name = None
        for word in text.split():
            if word.lower() in ["autozone", "oreilly", "o'reilly"]:
                name = word.title()
                break
        
        if amount and payment_date:
            return ParsedIntent(
                action="add_installment",
                entity_type="installment",
                entity_name=name or "New Installment",
                parameters={
                    "amount": float(amount),
                    "date": payment_date.isoformat(),
                    "provider": provider,
                    "category": "auto_parts",  # Default
                },
            )
    
    # Pattern: "cancel X" or "stop X"
    if any(phrase in normalized for phrase in ["cancel", "stop", "end"]):
        for alias in RECURRING_ALIASES.keys():
            if alias in normalized:
                resolved, alternatives = resolve_entity(alias, "recurring")
                if resolved:
                    return ParsedIntent(
                        action="cancel",
                        entity_type="recurring",
                        entity_name=resolved,
                        parameters={"mark_inactive": True},
                        ambiguous=len(alternatives) > 0,
                        alternatives=alternatives,
                    )
    
    # Unable to parse
    return ParsedIntent(
        action="unknown",
        entity_type="unknown",
        entity_name="",
        parameters={},
        confidence=0.0,
    )


def create_diff(
    db: Session,
    user_id: int,
    intent: ParsedIntent,
) -> AdjustmentDiff:
    """Create diff preview of proposed changes
    
    Args:
        db: Database session
        user_id: User ID
        intent: Parsed intent
    
    Returns:
        AdjustmentDiff with before/after snapshots
    """
    user = db.query(User).filter_by(id=user_id).first()
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    config = load_config()
    
    before = {}
    after = {}
    changes = []
    warnings = []
    
    if intent.action == "payoff":
        # Find debt in profile
        if profile and profile.financial_info:
            fi = profile.financial_info
            debt = next(
                (d for d in fi.get("debts_breakdown", []) if d["name"] == intent.entity_name),
                None
            )
            
            if debt:
                before["debt"] = debt.copy()
                after["debt"] = debt.copy()
                after["debt"]["balance"] = 0
                after["debt"]["closed"] = True
                
                changes.append(f"Set {intent.entity_name} balance to $0.00")
                changes.append(f"Mark {intent.entity_name} as closed")
                changes.append(f"Remove future minimum payments")
            else:
                warnings.append(f"Debt '{intent.entity_name}' not found in profile")
                return AdjustmentDiff(intent=intent, before=before, after=after, changes=changes, warnings=warnings, safe=False)
    
    elif intent.action == "change_amount":
        if intent.entity_type == "recurring":
            # Get current amount
            recurring_attr = intent.entity_name
            if hasattr(config.recurring_weekly, recurring_attr):
                current = getattr(config.recurring_weekly, recurring_attr)
                new_amount = intent.parameters["new_amount"]
                
                before["recurring"] = {recurring_attr: current}
                after["recurring"] = {recurring_attr: new_amount}
                
                changes.append(f"Change {intent.entity_name} from ${current:.2f} to ${new_amount:.2f}")
                
                effective = intent.parameters.get("effective_date")
                if effective:
                    changes.append(f"Effective date: {effective}")
                
                # Warning for SnapOn
                if recurring_attr == "SnapOn" and new_amount != 400.00:
                    warnings.append("Note: Snap-On has special reserve-then-clear rules on Thu/Fri")
            else:
                warnings.append(f"Recurring bill '{intent.entity_name}' not found")
                return AdjustmentDiff(intent=intent, before=before, after=after, changes=changes, warnings=warnings, safe=False)
    
    elif intent.action == "defer":
        changes.append(f"Defer {intent.entity_name} by {intent.parameters['delay_days']} days")
        warnings.append("Deferral will shift next due date only")
    
    elif intent.action == "add_installment":
        new_installment = {
            "amount_usd": intent.parameters["amount"],
            "date": intent.parameters["date"],
            "provider": intent.parameters["provider"],
            "category": intent.parameters.get("category", "misc"),
        }
        
        after["installment"] = new_installment
        
        changes.append(f"Add installment: {intent.entity_name}")
        changes.append(f"  Amount: ${intent.parameters['amount']:.2f}")
        changes.append(f"  Date: {intent.parameters['date']}")
        changes.append(f"  Provider: {intent.parameters['provider']}")
    
    elif intent.action == "cancel":
        if intent.entity_type == "recurring":
            changes.append(f"Cancel {intent.entity_name} subscription")
            changes.append(f"Mark as inactive from today")
    
    return AdjustmentDiff(
        intent=intent,
        before=before,
        after=after,
        changes=changes,
        warnings=warnings,
        safe=True,
    )


def apply_adjustment(
    db: Session,
    user_id: int,
    diff: AdjustmentDiff,
) -> bool:
    """Apply the adjustment and create audit record
    
    Args:
        db: Database session
        user_id: User ID
        diff: Approved diff
    
    Returns:
        True if successful
    """
    if not diff.safe:
        return False
    
    intent = diff.intent
    user = db.query(User).filter_by(id=user_id).first()
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    config = load_config()
    
    if intent.action == "payoff":
        # Update profile
        if profile and profile.financial_info:
            fi = profile.financial_info
            for debt in fi.get("debts_breakdown", []):
                if debt["name"] == intent.entity_name:
                    debt["balance"] = 0
                    debt["closed"] = True
                    debt["closed_date"] = date.today().isoformat()
            
            profile.financial_info = fi
            db.commit()
            return True
    
    elif intent.action == "change_amount":
        if intent.entity_type == "recurring":
            recurring_attr = intent.entity_name
            new_amount = intent.parameters["new_amount"]
            
            setattr(config.recurring_weekly, recurring_attr, new_amount)
            save_config(config)
            return True
    
    elif intent.action == "add_installment":
        # Add to config
        inst_name = f"{intent.entity_name}_{intent.parameters['date']}"
        config.installments[inst_name] = Installment(
            amount_usd=intent.parameters["amount"],
            date=intent.parameters["date"],
            provider=intent.parameters["provider"],
            category=intent.parameters.get("category", "misc"),
        )
        save_config(config)
        return True
    
    return False


def save_audit(
    user_text: str,
    diff: AdjustmentDiff,
    user_id: int,
) -> str:
    """Save audit record
    
    Args:
        user_text: Original user command
        diff: Applied diff
        user_id: User ID
    
    Returns:
        Audit ID
    """
    audit_dir = get_config_dir() / "audits"
    audit_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    audit_id = f"{date.today().isoformat()}-{datetime.now().strftime('%H%M%S')}"
    
    audit = AuditRecord(
        timestamp=timestamp,
        user_text=user_text,
        parsed_intent=asdict(diff.intent),
        resolved_entities={"entity_name": diff.intent.entity_name},
        before_snapshot=diff.before,
        after_snapshot=diff.after,
        changes_applied=diff.changes,
        audit_id=audit_id,
    )
    
    audit_file = audit_dir / f"{audit_id}.json"
    audit_file.write_text(json.dumps(asdict(audit), indent=2))
    
    return audit_id


def scan_entry_text(text: str) -> list[ParsedIntent]:
    """Scan entry text for potential financial changes
    
    Args:
        text: Entry text to scan
    
    Returns:
        List of detected intents
    """
    intents = []
    normalized = normalize_text(text)
    
    # Detect payoff mentions
    payoff_patterns = [
        r'paid off (\w+)',
        r'closed (\w+)',
        r'finished paying (\w+)',
    ]
    
    for pattern in payoff_patterns:
        matches = re.findall(pattern, normalized)
        for match in matches:
            resolved, alternatives = resolve_entity(match, "debt")
            if resolved:
                intent = ParsedIntent(
                    action="payoff",
                    entity_type="debt",
                    entity_name=resolved,
                    parameters={"set_balance": 0},
                    confidence=0.8,
                )
                intents.append(intent)
    
    return intents
