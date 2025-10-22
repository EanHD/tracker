# Daily Tracker - API Documentation

**Ve### Base URLs

```
Development: http://localhost:5703/api/v1
Production: https://your-domain.com/api/v1:** 1.0.0  
**Last Updated:** October 21, 2025  
**Base URL:** `http://localhost:5703/api/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Authentication](#authentication-endpoints)
   - [Entries](#entries-endpoints)
   - [Feedback](#feedback-endpoints)
   - [Statistics](#statistics-endpoints)
   - [Export](#export-endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## Overview

The Daily Tracker REST API provides programmatic access to all tracking functionality. Built with FastAPI, it offers:

- **RESTful design** - Standard HTTP methods (GET, POST, PATCH, DELETE)
- **JSON responses** - All data in JSON format
- **JWT authentication** - Secure token-based auth
- **OpenAPI documentation** - Interactive docs at `/docs`
- **Type safety** - Pydantic validation on all requests

### Technology Stack

- **Framework:** FastAPI 0.109.0
- **Database:** SQLite (via SQLAlchemy 2.0)
- **Authentication:** JWT (JSON Web Tokens)
- **Validation:** Pydantic v2

### Base URL

```
Development: http://localhost:5703/api/v1
Production:  https://your-domain.com/api/v1
```

### Content Types

- **Request:** `application/json`
- **Response:** `application/json`
- **File Downloads:** `text/csv` or `application/json`

---

## Authentication

### Overview

The API uses **JWT (JSON Web Token)** authentication with Bearer tokens.

### Token Lifecycle

1. **Obtain token** - POST credentials to `/auth/login`
2. **Use token** - Include in `Authorization` header
3. **Token expires** - After 90 days (configurable)
4. **Refresh** - Login again to get new token

### Authentication Flow

```
Client                          Server
  |                               |
  |  POST /auth/login             |
  |  {username, password}         |
  |------------------------------>|
  |                               |
  |  200 OK                       |
  |  {access_token, token_type}   |
  |<------------------------------|
  |                               |
  |  GET /entries/                |
  |  Authorization: Bearer <token>|
  |------------------------------>|
  |                               |
  |  200 OK                       |
  |  [entries...]                 |
  |<------------------------------|
```

### Security Best Practices

- ✅ Store tokens securely (environment variables, keyring)
- ✅ Use HTTPS in production
- ✅ Rotate tokens regularly
- ✅ Never commit tokens to version control
- ❌ Don't log tokens
- ❌ Don't include tokens in URLs

---

## Endpoints

### Authentication Endpoints

#### POST `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-10-21T10:30:00Z"
}
```

**Validation Rules:**
- `username`: 3-50 characters, alphanumeric + underscore
- `email`: Valid email format
- `password`: Minimum 8 characters

**Errors:**
- `400` - Validation error (invalid format)
- `409` - Username or email already exists

---

#### POST `/auth/login`

Authenticate and receive access token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7776000
}
```

**Token Usage:**
```bash
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:5703/api/v1/entries/
```

**Errors:**
- `401` - Invalid credentials
- `422` - Missing required fields

---

### Entries Endpoints

#### GET `/entries/`

List all entries for the authenticated user.

**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional) - Number of entries to skip (default: 0)
- `limit` (int, optional) - Max entries to return (default: 100, max: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": 123,
    "user_id": 1,
    "date": "2025-10-21",
    "income": "150.00",
    "bills": "50.00",
    "food": "25.00",
    "hours_worked": 8,
    "stress_level": 4,
    "hours_exercise": 1,
    "hours_sleep": 7,
    "hours_social": 2,
    "priority_note": "Completed project milestone",
    "general_note": "Good productive day",
    "created_at": "2025-10-21T18:00:00Z",
    "updated_at": "2025-10-21T18:00:00Z"
  }
]
```

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5703/api/v1/entries/?limit=10"
```

---

#### GET `/entries/{date}`

Retrieve a specific entry by date.

**Authentication:** Required

**Path Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Response:** `200 OK`
```json
{
  "id": 123,
  "user_id": 1,
  "date": "2025-10-21",
  "income": "150.00",
  "bills": "50.00",
  "food": "25.00",
  "hours_worked": 8,
  "stress_level": 4,
  "hours_exercise": 1,
  "hours_sleep": 7,
  "hours_social": 2,
  "priority_note": "Completed project milestone",
  "general_note": "Good productive day",
  "created_at": "2025-10-21T18:00:00Z",
  "updated_at": "2025-10-21T18:00:00Z"
}
```

**Errors:**
- `404` - Entry not found for that date
- `422` - Invalid date format

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/entries/2025-10-21
```

---

#### POST `/entries/`

Create a new entry.

**Authentication:** Required

**Request Body:**
```json
{
  "date": "2025-10-21",
  "income": "150.00",
  "bills": "50.00",
  "food": "25.00",
  "hours_worked": 8,
  "stress_level": 4,
  "hours_exercise": 1,
  "hours_sleep": 7,
  "hours_social": 2,
  "priority_note": "Completed project milestone",
  "general_note": "Good productive day"
}
```

**Validation Rules:**
- `date`: YYYY-MM-DD format, required
- `income`, `bills`, `food`: Decimal, >= 0, optional
- `hours_worked`: Integer 0-24, optional
- `stress_level`: Integer 1-10, optional
- `hours_exercise`, `hours_sleep`, `hours_social`: Integer >= 0, optional
- `priority_note`, `general_note`: String, max 1000 chars, optional

**Response:** `201 Created`
```json
{
  "id": 124,
  "user_id": 1,
  "date": "2025-10-21",
  "income": "150.00",
  "bills": "50.00",
  "food": "25.00",
  "hours_worked": 8,
  "stress_level": 4,
  "hours_exercise": 1,
  "hours_sleep": 7,
  "hours_social": 2,
  "priority_note": "Completed project milestone",
  "general_note": "Good productive day",
  "created_at": "2025-10-21T18:30:00Z",
  "updated_at": "2025-10-21T18:30:00Z"
}
```

**Errors:**
- `400` - Validation error
- `409` - Entry already exists for that date

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-10-21","stress_level":3}' \
  http://localhost:5703/api/v1/entries/
```

---

#### PATCH `/entries/{date}`

Update an existing entry (partial updates supported).

**Authentication:** Required

**Path Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Request Body:** (all fields optional)
```json
{
  "stress_level": 5,
  "general_note": "Updated reflection after evening review"
}
```

**Response:** `200 OK`
```json
{
  "id": 123,
  "user_id": 1,
  "date": "2025-10-21",
  "income": "150.00",
  "bills": "50.00",
  "food": "25.00",
  "hours_worked": 8,
  "stress_level": 5,
  "hours_exercise": 1,
  "hours_sleep": 7,
  "hours_social": 2,
  "priority_note": "Completed project milestone",
  "general_note": "Updated reflection after evening review",
  "created_at": "2025-10-21T18:00:00Z",
  "updated_at": "2025-10-21T22:15:00Z"
}
```

**Errors:**
- `404` - Entry not found
- `403` - Not authorized to edit this entry
- `400` - Validation error

**Example:**
```bash
curl -X PATCH \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stress_level":6}' \
  http://localhost:5703/api/v1/entries/2025-10-21
```

---

#### DELETE `/entries/{date}`

Delete an entry.

**Authentication:** Required

**Path Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Response:** `204 No Content`

**Errors:**
- `404` - Entry not found
- `403` - Not authorized to delete this entry

**Example:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/entries/2025-10-21
```

---

### Feedback Endpoints

#### GET `/feedback/{date}`

Retrieve AI-generated feedback for an entry.

**Authentication:** Required

**Path Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Response:** `200 OK`
```json
{
  "id": 45,
  "entry_id": 123,
  "feedback_text": "Great job maintaining work-life balance today! Your stress level of 4 is manageable, and getting 7 hours of sleep shows good self-care. The positive cash flow ($150 income - $75 expenses = $75 net) is excellent. Consider increasing exercise slightly to help manage stress even better. Keep up the momentum on that project milestone!",
  "ai_provider": "openai",
  "ai_model": "gpt-4",
  "created_at": "2025-10-21T18:00:30Z"
}
```

**Errors:**
- `404` - Entry or feedback not found

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/feedback/2025-10-21
```

---

#### POST `/feedback/{date}/regenerate`

Request new AI feedback for an entry.

**Authentication:** Required

**Path Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Response:** `200 OK`
```json
{
  "id": 46,
  "entry_id": 123,
  "feedback_text": "Your work metrics show strong productivity with 8 hours logged at a moderate stress level. The financial picture is healthy with net positive of $75. Sleep at 7 hours is good, though you might benefit from 8. Your priority focus on the project milestone demonstrates clear goal-setting. Well done!",
  "ai_provider": "openai",
  "ai_model": "gpt-4",
  "created_at": "2025-10-21T22:30:00Z"
}
```

**Errors:**
- `404` - Entry not found
- `500` - AI provider error

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/feedback/2025-10-21/regenerate
```

---

### Statistics Endpoints

#### GET `/stats/`

Get aggregated statistics for the authenticated user.

**Authentication:** Required

**Query Parameters:**
- `days` (int, optional) - Number of recent days to analyze (default: 7, max: 365)

**Response:** `200 OK`
```json
{
  "total_entries": 87,
  "date_range": {
    "start": "2025-10-14",
    "end": "2025-10-21",
    "days": 7
  },
  "financials": {
    "total_income": "1050.00",
    "total_bills": "350.00",
    "total_food": "175.00",
    "net_total": "525.00",
    "avg_daily_income": "150.00",
    "avg_daily_expenses": "75.00"
  },
  "work": {
    "avg_hours_worked": 7.8,
    "avg_stress_level": 4.2,
    "stress_trend": "stable",
    "total_hours": 54.6
  },
  "wellbeing": {
    "avg_hours_sleep": 7.1,
    "avg_hours_exercise": 0.9,
    "avg_hours_social": 2.3
  },
  "streaks": {
    "current_streak": 12,
    "longest_streak": 45,
    "streak_active": true
  },
  "achievements_unlocked": 5,
  "total_achievements": 9
}
```

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5703/api/v1/stats/?days=30"
```

---

### Export Endpoints

#### GET `/export/csv`

Export entries as CSV file.

**Authentication:** Required

**Query Parameters:**
- `start_date` (string, optional) - Start date YYYY-MM-DD
- `end_date` (string, optional) - End date YYYY-MM-DD

**Response:** `200 OK`
```
Content-Type: text/csv
Content-Disposition: attachment; filename="tracker_export_20251021.csv"

date,income,bills,food,hours_worked,stress_level,hours_exercise,hours_sleep,hours_social,priority_note,general_note
2025-10-21,150.00,50.00,25.00,8,4,1,7,2,"Completed project milestone","Good productive day"
2025-10-20,120.00,0.00,30.00,7,5,0,6,1,"Client meeting prep","Busy day, felt tired"
```

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5703/api/v1/export/csv?start_date=2025-10-01" \
  -o tracker_data.csv
```

---

#### GET `/export/json`

Export entries as JSON file.

**Authentication:** Required

**Query Parameters:**
- `start_date` (string, optional) - Start date YYYY-MM-DD
- `end_date` (string, optional) - End date YYYY-MM-DD

**Response:** `200 OK`
```json
{
  "export_date": "2025-10-21T22:45:00Z",
  "user_id": 1,
  "entry_count": 87,
  "entries": [
    {
      "date": "2025-10-21",
      "financials": {
        "income": "150.00",
        "bills": "50.00",
        "food": "25.00",
        "net": "75.00"
      },
      "work": {
        "hours_worked": 8,
        "stress_level": 4
      },
      "wellbeing": {
        "hours_exercise": 1,
        "hours_sleep": 7,
        "hours_social": 2
      },
      "notes": {
        "priority": "Completed project milestone",
        "general": "Good productive day"
      },
      "metadata": {
        "created_at": "2025-10-21T18:00:00Z",
        "updated_at": "2025-10-21T18:00:00Z"
      }
    }
  ]
}
```

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/export/json \
  -o tracker_backup.json
```

---

#### GET `/export/stats`

Get export statistics and preview.

**Authentication:** Required

**Query Parameters:**
- `start_date` (string, optional) - Start date YYYY-MM-DD
- `end_date` (string, optional) - End date YYYY-MM-DD

**Response:** `200 OK`
```json
{
  "entry_count": 87,
  "date_range": {
    "start": "2025-08-01",
    "end": "2025-10-21"
  },
  "estimated_sizes": {
    "csv_bytes": 15420,
    "json_bytes": 42380
  },
  "preview": {
    "first_entry_date": "2025-08-01",
    "last_entry_date": "2025-10-21",
    "total_days_tracked": 82
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5703/api/v1/export/stats
```

---

## Error Handling

### Standard Error Response

All errors return a consistent JSON structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Validation error or malformed request |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed (Pydantic) |
| 500 | Internal Server Error | Server error (check logs) |

### Error Examples

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Entry not found for date: 2025-10-21"
}
```

**400 Bad Request:**
```json
{
  "detail": [
    {
      "loc": ["body", "stress_level"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**409 Conflict:**
```json
{
  "detail": "Entry already exists for date: 2025-10-21"
}
```

---

## Rate Limiting

### Current Limits

No rate limiting is currently enforced in the application layer. However, consider:

- **AI Provider Limits**: OpenAI, Anthropic, etc. have their own rate limits
- **Database Limits**: SQLite can handle ~100,000 requests/sec for reads
- **Network Limits**: Depends on your deployment

### Recommended Production Limits

For production deployment, consider implementing:

```python
# Example: 100 requests per minute per user
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/entries/")
@limiter.limit("100/minute")
async def list_entries(...):
    ...
```

---

## Examples

### Python Client

```python
import requests
from typing import Optional

class TrackerClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def create_entry(self, date: str, **kwargs):
        """Create a new entry"""
        data = {"date": date, **kwargs}
        response = requests.post(
            f"{self.base_url}/entries/",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_entry(self, date: str):
        """Get entry by date"""
        response = requests.get(
            f"{self.base_url}/entries/{date}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_entry(self, date: str, **kwargs):
        """Update entry"""
        response = requests.patch(
            f"{self.base_url}/entries/{date}",
            json=kwargs,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_entries(self, limit: int = 10):
        """List recent entries"""
        response = requests.get(
            f"{self.base_url}/entries/",
            params={"limit": limit},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self, days: int = 7):
        """Get statistics"""
        response = requests.get(
            f"{self.base_url}/stats/",
            params={"days": days},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def export_data(self, format: str = "json", output_file: str = None):
        """Export all data"""
        response = requests.get(
            f"{self.base_url}/export/{format}",
            headers=self.headers
        )
        response.raise_for_status()
        
        if output_file:
            with open(output_file, "wb") as f:
                f.write(response.content)
        
        return response.content

# Usage
client = TrackerClient("http://localhost:5703/api/v1", "your-token-here")

# Create entry
entry = client.create_entry(
    date="2025-10-21",
    income=150.00,
    stress_level=4,
    hours_worked=8
)

# Get statistics
stats = client.get_stats(days=30)
print(f"Average stress: {stats['work']['avg_stress_level']}")

# Export data
client.export_data(format="csv", output_file="backup.csv")
```

### JavaScript Client

```javascript
class TrackerClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async createEntry(date, data) {
    const response = await fetch(`${this.baseUrl}/entries/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ date, ...data })
    });
    return response.json();
  }

  async getEntry(date) {
    const response = await fetch(`${this.baseUrl}/entries/${date}`, {
      headers: this.headers
    });
    return response.json();
  }

  async updateEntry(date, updates) {
    const response = await fetch(`${this.baseUrl}/entries/${date}`, {
      method: 'PATCH',
      headers: this.headers,
      body: JSON.stringify(updates)
    });
    return response.json();
  }

  async listEntries(limit = 10) {
    const response = await fetch(
      `${this.baseUrl}/entries/?limit=${limit}`,
      { headers: this.headers }
    );
    return response.json();
  }

  async getStats(days = 7) {
    const response = await fetch(
      `${this.baseUrl}/stats/?days=${days}`,
      { headers: this.headers }
    );
    return response.json();
  }
}

// Usage
const client = new TrackerClient('http://localhost:5703/api/v1', 'your-token');

// Create entry
const entry = await client.createEntry('2025-10-21', {
  income: 150.00,
  stress_level: 4,
  hours_worked: 8
});

// Get stats
const stats = await client.getStats(30);
console.log(`Average stress: ${stats.work.avg_stress_level}`);
```

### cURL Examples

**Complete Workflow:**

```bash
#!/bin/bash
BASE_URL="http://localhost:5703/api/v1"

# 1. Login
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Create entry
curl -X POST "$BASE_URL/entries/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-21",
    "income": "150.00",
    "bills": "50.00",
    "food": "25.00",
    "hours_worked": 8,
    "stress_level": 4,
    "hours_sleep": 7
  }'

# 3. Get feedback
curl "$BASE_URL/feedback/2025-10-21" \
  -H "Authorization: Bearer $TOKEN"

# 4. Update entry
curl -X PATCH "$BASE_URL/entries/2025-10-21" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stress_level": 3}'

# 5. Get statistics
curl "$BASE_URL/stats/?days=7" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.work.avg_stress_level'

# 6. Export data
curl "$BASE_URL/export/csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o backup.csv
```

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:5703/docs`
- **ReDoc**: `http://localhost:5703/redoc`

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly in the browser
- View request/response schemas
- Authenticate and save tokens

---

## OpenAPI Specification

The OpenAPI (Swagger) specification is available at:

```
GET /openapi.json
```

Use this to generate client libraries in any language using tools like:
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger Codegen](https://swagger.io/tools/swagger-codegen/)

---

**Need Help?** Check the [User Guide](USER_GUIDE.md) or [Deployment Guide](DEPLOYMENT.md).
