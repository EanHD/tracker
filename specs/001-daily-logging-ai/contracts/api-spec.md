# API Contracts

**Version**: 1.0.0  
**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: Bearer JWT token in `Authorization` header

## Response Format

All API responses follow a standard envelope:

### Success Response
```json
{
  "success": true,
  "data": { /* response payload */ },
  "meta": {
    "timestamp": "2025-10-21T18:45:00Z",
    "request_id": "uuid"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": { /* field-specific errors */ }
  },
  "meta": {
    "timestamp": "2025-10-21T18:45:00Z",
    "request_id": "uuid"
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | Token valid but lacks required scope |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Resource already exists (e.g., duplicate entry for date) |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | AI service temporarily unavailable |

---

## Authentication Endpoints

### POST /auth/token

Generate a JWT access token.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 7776000,
    "scopes": ["entries:read", "entries:write", "feedback:generate"]
  }
}
```

**Errors**:
- `401 UNAUTHORIZED`: Invalid credentials

---

### POST /auth/refresh

Refresh an expired token (future feature).

**Headers**:
- `Authorization: Bearer <expired_token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 7776000
  }
}
```

---

## Entry Endpoints

### POST /entries

Create a new daily entry.

**Required Scopes**: `entries:write`

**Request Body**:
```json
{
  "date": "2025-10-21",
  "cash_on_hand": 142.35,
  "bank_balance": -53.21,
  "income_today": 420.00,
  "bills_due_today": 275.00,
  "debts_total": 18600.00,
  "hours_worked": 8.0,
  "side_income": 80.00,
  "food_spent": 22.17,
  "gas_spent": 38.55,
  "notes": "Paid Snap-On min. late. Worked overtime.",
  "stress_level": 6,
  "priority": "clear card debt"
}
```

**Field Validations**:
- `date`: ISO 8601 date (YYYY-MM-DD), not future date
- `stress_level`: Integer 1-10
- `hours_worked`: Decimal 0-24
- All monetary fields: Decimal with max 2 decimal places
- `notes`: Optional, max 5000 characters
- `priority`: Optional, max 255 characters

**Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 123,
    "date": "2025-10-21",
    "cash_on_hand": 142.35,
    "bank_balance": -53.21,
    "income_today": 420.00,
    "bills_due_today": 275.00,
    "debts_total": 18600.00,
    "hours_worked": 8.0,
    "side_income": 80.00,
    "food_spent": 22.17,
    "gas_spent": 38.55,
    "notes": "Paid Snap-On min. late. Worked overtime.",
    "stress_level": 6,
    "priority": "clear card debt",
    "created_at": "2025-10-21T18:30:00Z",
    "updated_at": "2025-10-21T18:30:00Z",
    "feedback": {
      "status": "pending",
      "id": 456
    }
  }
}
```

**Errors**:
- `409 CONFLICT`: Entry already exists for this date
- `422 VALIDATION_ERROR`: Invalid field values

---

### GET /entries

List entries with optional filtering.

**Required Scopes**: `entries:read`

**Query Parameters**:
- `start_date`: ISO date (optional) - filter from this date
- `end_date`: ISO date (optional) - filter until this date
- `limit`: Integer (default=30, max=100) - number of results
- `offset`: Integer (default=0) - pagination offset
- `order`: String (default=desc) - `asc` or `desc` by date

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 123,
        "date": "2025-10-21",
        "stress_level": 6,
        "income_today": 420.00,
        "priority": "clear card debt",
        "has_feedback": true,
        "created_at": "2025-10-21T18:30:00Z"
      }
    ],
    "pagination": {
      "total": 365,
      "limit": 30,
      "offset": 0,
      "has_more": true
    }
  }
}
```

---

### GET /entries/:date

Get a specific entry by date.

**Required Scopes**: `entries:read`

**Path Parameters**:
- `date`: ISO date (YYYY-MM-DD)

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 123,
    "date": "2025-10-21",
    "cash_on_hand": 142.35,
    "bank_balance": -53.21,
    "income_today": 420.00,
    "bills_due_today": 275.00,
    "debts_total": 18600.00,
    "hours_worked": 8.0,
    "side_income": 80.00,
    "food_spent": 22.17,
    "gas_spent": 38.55,
    "notes": "Paid Snap-On min. late. Worked overtime.",
    "stress_level": 6,
    "priority": "clear card debt",
    "created_at": "2025-10-21T18:30:00Z",
    "updated_at": "2025-10-21T18:30:00Z",
    "feedback": {
      "id": 456,
      "content": "You're doing amazing work! That overtime...",
      "status": "completed",
      "provider": "anthropic",
      "model": "claude-3-sonnet",
      "created_at": "2025-10-21T18:30:15Z"
    }
  }
}
```

**Errors**:
- `404 NOT_FOUND`: No entry exists for this date

---

### PATCH /entries/:date

Update an existing entry.

**Required Scopes**: `entries:write`

**Path Parameters**:
- `date`: ISO date (YYYY-MM-DD)

**Request Body** (all fields optional):
```json
{
  "cash_on_hand": 150.00,
  "notes": "Updated note",
  "stress_level": 5
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    /* Updated entry object */
    "updated_at": "2025-10-21T19:00:00Z"
  }
}
```

**Notes**:
- Triggers feedback regeneration if entry substantially changed
- Original `created_at` preserved, `updated_at` refreshed

**Errors**:
- `404 NOT_FOUND`: No entry exists for this date
- `422 VALIDATION_ERROR`: Invalid field values

---

### DELETE /entries/:date

Delete an entry (soft delete, archived).

**Required Scopes**: `entries:write`

**Path Parameters**:
- `date`: ISO date (YYYY-MM-DD)

**Response**: `204 No Content`

**Errors**:
- `404 NOT_FOUND`: No entry exists for this date

---

## Feedback Endpoints

### GET /feedback/:entry_id

Get AI feedback for a specific entry.

**Required Scopes**: `entries:read`

**Path Parameters**:
- `entry_id`: Integer - entry ID

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 456,
    "entry_id": 123,
    "content": "You're making incredible progress! Working overtime shows dedication...",
    "status": "completed",
    "provider": "anthropic",
    "model": "claude-3-sonnet",
    "tokens_used": 350,
    "generation_time": 2.3,
    "created_at": "2025-10-21T18:30:15Z",
    "updated_at": "2025-10-21T18:30:17Z"
  }
}
```

**Errors**:
- `404 NOT_FOUND`: No feedback exists for this entry

---

### POST /feedback/:entry_id/regenerate

Regenerate AI feedback for an entry.

**Required Scopes**: `feedback:generate`

**Path Parameters**:
- `entry_id`: Integer - entry ID

**Request Body** (optional):
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "custom_prompt": "Focus on budgeting advice"
}
```

**Response**: `202 Accepted`
```json
{
  "success": true,
  "data": {
    "feedback_id": 457,
    "status": "pending",
    "message": "Feedback generation started"
  }
}
```

**Errors**:
- `404 NOT_FOUND`: Entry does not exist
- `503 SERVICE_UNAVAILABLE`: AI service not available

---

### GET /feedback/:entry_id/conversation

Get full conversation log for extended AI interactions (future feature).

**Required Scopes**: `entries:read`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "feedback_id": 456,
    "messages": [
      {
        "id": 1,
        "role": "system",
        "content": "You are a supportive financial coach...",
        "timestamp": "2025-10-21T18:30:15Z"
      },
      {
        "id": 2,
        "role": "user",
        "content": "Entry data: {...}",
        "timestamp": "2025-10-21T18:30:15Z"
      },
      {
        "id": 3,
        "role": "assistant",
        "content": "You're doing amazing work...",
        "timestamp": "2025-10-21T18:30:17Z"
      }
    ]
  }
}
```

---

## Statistics Endpoints

### GET /stats/summary

Get aggregate statistics for a date range.

**Required Scopes**: `entries:read`

**Query Parameters**:
- `start_date`: ISO date (required)
- `end_date`: ISO date (required)

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-21",
      "days_logged": 21,
      "days_in_period": 21,
      "completion_rate": 1.0
    },
    "financials": {
      "total_income": 8820.00,
      "total_bills": 5775.00,
      "total_side_income": 1680.00,
      "total_food_spent": 465.57,
      "total_gas_spent": 809.55,
      "avg_cash_on_hand": 138.45,
      "avg_bank_balance": -45.32,
      "debt_change": -200.00
    },
    "wellbeing": {
      "avg_stress_level": 5.8,
      "max_stress_level": 9,
      "min_stress_level": 3,
      "avg_hours_worked": 8.2,
      "overtime_days": 5
    },
    "trends": {
      "stress_trend": "decreasing",
      "income_trend": "stable",
      "spending_trend": "increasing"
    }
  }
}
```

---

## Health & Status Endpoints

### GET /health

Health check endpoint (no authentication required).

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-10-21T18:45:00Z",
    "version": "1.0.0",
    "services": {
      "database": "healthy",
      "ai_service": "healthy"
    }
  }
}
```

---

### GET /version

Get API version information (no authentication required).

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "api_version": "v1",
    "build": "20251021-1845"
  }
}
```

---

## Rate Limiting

API implements rate limiting to prevent abuse:

- **Authenticated requests**: 1000 requests/hour per user
- **Unauthenticated requests**: 100 requests/hour per IP
- **Feedback generation**: 10 requests/hour per user (AI cost control)

**Rate Limit Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1634856000
```

**Rate Limit Exceeded Response**: `429 Too Many Requests`
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 minutes.",
    "details": {
      "retry_after": 2700
    }
  }
}
```

---

## Webhook Events (Future Feature)

For automation and integrations, webhooks can be configured to receive events:

**Supported Events**:
- `entry.created` - New entry created
- `entry.updated` - Entry modified
- `entry.deleted` - Entry deleted
- `feedback.completed` - AI feedback generation completed
- `feedback.failed` - AI feedback generation failed

**Webhook Payload**:
```json
{
  "event": "entry.created",
  "timestamp": "2025-10-21T18:30:00Z",
  "data": { /* event-specific payload */ }
}
```
