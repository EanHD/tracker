# Data Model

**Feature**: Daily Logging App with AI Agent Integration  
**Date**: 2025-10-21  
**Storage**: SQLite (SQLAlchemy ORM)

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │
│ username        │
│ email           │
│ password_hash   │
│ created_at      │
│ api_key_hash    │
└────────┬────────┘
         │ 1
         │
         │ *
┌────────┴────────┐
│  DailyEntry     │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ date (UNIQUE)   │
│ cash_on_hand    │◄─── Encrypted
│ bank_balance    │◄─── Encrypted
│ income_today    │
│ bills_due_today │
│ debts_total     │◄─── Encrypted
│ hours_worked    │
│ side_income     │
│ food_spent      │
│ gas_spent       │
│ notes           │
│ stress_level    │
│ priority        │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1
         │
         │ 0..1
┌────────┴────────┐
│   AIFeedback    │
│─────────────────│
│ id (PK)         │
│ entry_id (FK)   │
│ content         │
│ status          │
│ provider        │
│ model           │
│ tokens_used     │
│ generation_time │
│ error_message   │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │
┌────────┴────────┐
│ ConversationLog │
│─────────────────│
│ id (PK)         │
│ feedback_id(FK) │
│ role            │
│ content         │
│ timestamp       │
└─────────────────┘
```

## Entities

### User

Represents an individual user of the application. Initially single-user (default user auto-created), but designed for future multi-user expansion.

**Fields**:
- `id`: Integer, primary key, auto-increment
- `username`: String(100), unique, indexed - user identifier
- `email`: String(255), unique, indexed - for notifications (future)
- `password_hash`: String(255) - bcrypt hashed password
- `created_at`: DateTime, default=now - account creation timestamp
- `api_key_hash`: String(255), nullable - hashed API key for token generation
- `settings`: JSON - user preferences (notification times, AI provider, etc.)

**Validation**:
- Username: 3-100 characters, alphanumeric + underscore
- Email: Valid email format (if provided)
- Password: Min 8 characters (only for multi-user mode)

**Relationships**:
- One-to-many with DailyEntry
- Cascade delete: All entries deleted when user deleted

**Indexes**:
- Primary: `id`
- Unique: `username`, `email`
- Index: `api_key_hash` (for token lookup)

---

### DailyEntry

Represents a single day's financial and wellbeing snapshot. Core entity of the application.

**Fields**:
- `id`: Integer, primary key, auto-increment
- `user_id`: Integer, foreign key → User.id, indexed
- `date`: Date, unique per user - the day this entry represents (ISO 8601)
- `cash_on_hand`: Decimal(10,2), encrypted - liquid cash available
- `bank_balance`: Decimal(10,2), encrypted - checking/current account balance
- `income_today`: Decimal(10,2), not null, default=0 - earnings for this day
- `bills_due_today`: Decimal(10,2), not null, default=0 - payments due/made
- `debts_total`: Decimal(10,2), encrypted - total outstanding debt
- `hours_worked`: Decimal(4,1), not null, default=0 - job hours (0-24)
- `side_income`: Decimal(10,2), not null, default=0 - gig/side work earnings
- `food_spent`: Decimal(10,2), not null, default=0 - food/grocery spending
- `gas_spent`: Decimal(10,2), not null, default=0 - transportation/gas cost
- `notes`: Text, nullable - free-form notes about the day
- `stress_level`: Integer, not null, check(1-10) - mental load rating
- `priority`: String(255), nullable - what's top of mind
- `created_at`: DateTime, default=now - when entry was created
- `updated_at`: DateTime, default=now, onupdate=now - last modification

**Validation**:
- `date`: Valid date, not future date (configurable)
- `stress_level`: Integer 1-10 inclusive
- Decimal fields: Max 2 decimal places
- `hours_worked`: 0-24 range
- Negative values allowed for cash_on_hand, bank_balance (overdraft)

**Relationships**:
- Many-to-one with User
- One-to-one with AIFeedback (optional)

**Indexes**:
- Primary: `id`
- Unique: `(user_id, date)` - enforce one entry per user per day
- Index: `user_id`, `date` separately for efficient queries
- Index: `created_at` for recent entries query

**Encryption**:
- Encrypted fields: `cash_on_hand`, `bank_balance`, `debts_total`
- Method: Fernet symmetric encryption before storage
- Key: Stored in OS keychain or environment variable

---

### AIFeedback

Represents motivational and analytical AI-generated content for a daily entry. One feedback per entry, with regeneration creating new record.

**Fields**:
- `id`: Integer, primary key, auto-increment
- `entry_id`: Integer, foreign key → DailyEntry.id, unique, indexed
- `content`: Text, not null - the AI-generated feedback message
- `status`: Enum('pending', 'completed', 'failed'), default='pending'
- `provider`: String(50), nullable - AI provider used (openai, anthropic)
- `model`: String(100), nullable - specific model (gpt-4, claude-3-opus)
- `tokens_used`: Integer, nullable - token count for cost tracking
- `generation_time`: Float, nullable - seconds taken to generate
- `error_message`: Text, nullable - error details if status=failed
- `created_at`: DateTime, default=now - when generation started
- `updated_at`: DateTime, default=now, onupdate=now - when status changed

**Validation**:
- `status`: Must be one of enum values
- `tokens_used`: Non-negative integer
- `generation_time`: Non-negative float

**Relationships**:
- One-to-one with DailyEntry (each entry has at most one current feedback)
- One-to-many with ConversationLog

**Indexes**:
- Primary: `id`
- Unique: `entry_id` - only one feedback per entry
- Index: `status` - for pending feedback queries
- Index: `created_at` - for recent feedback queries

**State Transitions**:
```
pending → completed (success)
pending → failed (error)
completed → pending (regeneration requested)
failed → pending (retry)
```

---

### ConversationLog

Represents the full conversation history for extended AI interactions. Stores the back-and-forth dialogue for "chat mode" feature.

**Fields**:
- `id`: Integer, primary key, auto-increment
- `feedback_id`: Integer, foreign key → AIFeedback.id, indexed
- `role`: Enum('system', 'user', 'assistant'), not null - message sender
- `content`: Text, not null - message content
- `timestamp`: DateTime, default=now - when message was sent/received

**Validation**:
- `role`: Must be one of enum values
- `content`: Non-empty string

**Relationships**:
- Many-to-one with AIFeedback

**Indexes**:
- Primary: `id`
- Index: `feedback_id` - for conversation retrieval
- Index: `(feedback_id, timestamp)` - chronological ordering

**Purpose**:
- Enables future "chat mode" where users can have extended conversations with AI about their entry
- Initial implementation stores only the single feedback generation prompt/response
- Future: Support multi-turn conversations

---

## Database Constraints

### Unique Constraints
- `users.username` - no duplicate usernames
- `users.email` - no duplicate emails
- `daily_entries.user_id + daily_entries.date` - one entry per user per day
- `ai_feedback.entry_id` - one feedback per entry

### Foreign Key Constraints
- `daily_entries.user_id` → `users.id` (ON DELETE CASCADE)
- `ai_feedback.entry_id` → `daily_entries.id` (ON DELETE CASCADE)
- `conversation_log.feedback_id` → `ai_feedback.id` (ON DELETE CASCADE)

### Check Constraints
- `daily_entries.stress_level` BETWEEN 1 AND 10
- `daily_entries.hours_worked` BETWEEN 0 AND 24
- `ai_feedback.tokens_used` >= 0
- `ai_feedback.generation_time` >= 0

### Not Null Constraints
- All primary keys and foreign keys
- `daily_entries.date`, `stress_level`, `income_today`, `bills_due_today`, `hours_worked`, `side_income`, `food_spent`, `gas_spent`
- `ai_feedback.content`, `status`
- `conversation_log.role`, `content`

## Migrations Strategy

Using Alembic for schema migrations.

**Migration Sequence**:
1. `001_initial_schema.py` - Create all tables
2. `002_add_encryption.py` - Add encryption to sensitive fields
3. `003_add_conversation_log.py` - Add conversation log table (future)
4. Future: Add multi-user features, user settings, etc.

**Migration Best Practices**:
- Never drop columns without deprecation period
- Always provide default values for new required columns
- Use batch operations for SQLite (no ALTER COLUMN support)
- Test migrations with real data

## Query Patterns

### Common Queries

**Get user's entries for date range:**
```sql
SELECT * FROM daily_entries 
WHERE user_id = ? 
  AND date BETWEEN ? AND ?
ORDER BY date DESC;
```

**Get latest N entries:**
```sql
SELECT * FROM daily_entries 
WHERE user_id = ?
ORDER BY date DESC 
LIMIT ?;
```

**Get entry with feedback:**
```sql
SELECT de.*, af.content, af.status
FROM daily_entries de
LEFT JOIN ai_feedback af ON af.entry_id = de.id
WHERE de.user_id = ? AND de.date = ?;
```

**Get pending feedback tasks:**
```sql
SELECT af.*, de.date
FROM ai_feedback af
JOIN daily_entries de ON de.id = af.entry_id
WHERE af.status = 'pending'
ORDER BY af.created_at ASC;
```

**Calculate average stress level for period:**
```sql
SELECT AVG(stress_level) as avg_stress,
       COUNT(*) as entry_count
FROM daily_entries
WHERE user_id = ?
  AND date BETWEEN ? AND ?;
```

## Performance Considerations

**Indexes for Performance**:
- Date-based queries: Index on `daily_entries.date`
- User filtering: Index on `daily_entries.user_id`
- Pending feedback: Index on `ai_feedback.status`
- Recent queries: Indexes on `created_at` fields

**Optimization Strategies**:
- Use SQLite WAL mode for better concurrent access
- Regular VACUUM to reclaim space and optimize
- Limit result sets (pagination for large date ranges)
- Cache frequently accessed data (current entry, recent entries)

**Expected Data Volume**:
- Single user: ~365 entries/year = 3,650 entries over 10 years
- With feedback: ~7,300 records total (entries + feedback)
- With conversation logs: Variable, depends on chat usage
- Database size estimate: <10MB over 10 years (without conversation logs)

## Backup Strategy

**Local Backup**:
- Daily automated backup to `~/.config/tracker/backups/`
- Keep last 30 days of backups
- Encrypted backup files using same encryption key

**Export Format**:
- JSON export for human readability
- CSV export for spreadsheet analysis
- Encrypted exports include encryption metadata

**Restore Process**:
- `tracker backup restore <file>` command
- Validates backup integrity before restore
- Option to merge or replace existing data
