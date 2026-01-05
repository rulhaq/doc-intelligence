# CustomerLLM API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

### Local Login
```http
POST /auth/local/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "changeme"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

## Conversations

### List Conversations
```http
GET /conversations
Authorization: Bearer <token>
```

### Create Conversation
```http
POST /conversations
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Contract Analysis"
}
```

### Get Conversation
```http
GET /conversations/{conversation_id}
Authorization: Bearer <token>
```

### Send Message
```http
POST /conversations/{conversation_id}/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "user",
  "text": "Find termination clauses",
  "context_filters": {
    "source": ["contracts"]
  }
}
```

### WebSocket Chat (Streaming)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/conversations/{id}/ws?token=<jwt>');

ws.onopen = () => {
  ws.send(JSON.stringify({ text: 'Your question here' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: "token" | "card" | "done"
  // data.content: token text (for type="token")
  // data.card: card object (for type="card")
};
```

## Admin - Documents

### Upload Document
```http
POST /admin/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <PDF file>
```

### Process OCR
```http
POST /admin/documents/{document_id}/process-ocr
Authorization: Bearer <token>
```

### Get Document Preview
```http
GET /admin/documents/{document_id}/preview
Authorization: Bearer <token>
```

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "contract.pdf",
  "total_pages": 10,
  "status": "OCR_COMPLETED",
  "pages": [
    {
      "page_number": 1,
      "image_url": "https://...",
      "ocr_text": "Raw OCR text...",
      "corrected_text": "LLM corrected text...",
      "corrections": [
        {
          "from": "Th1s",
          "to": "This",
          "confidence": 0.98,
          "explain": "digit 1 -> letter i"
        }
      ],
      "is_edited": false
    }
  ]
}
```

### Update Preview (Manual Edits)
```http
PUT /admin/documents/{document_id}/preview
Authorization: Bearer <token>
Content-Type: application/json

[
  {
    "page_number": 1,
    "edited_text": "Manually corrected text..."
  }
]
```

### Commit Document
```http
POST /admin/documents/{document_id}/commit
Authorization: Bearer <token>
```

### List Documents
```http
GET /admin/documents?page=1&page_size=50
Authorization: Bearer <token>
```

### Delete Document
```http
DELETE /admin/documents/{document_id}
Authorization: Bearer <token>
```

## Search

### Semantic Search
```http
POST /search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "termination clauses",
  "limit": 10,
  "score_threshold": 0.5,
  "filters": {
    "source": "contracts"
  }
}
```

## Agents

### Create Agent
```http
POST /agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Web Scraper",
  "agent_type": "web_scraper",
  "description": "Scrapes company websites",
  "config": {
    "max_depth": 3,
    "allowed_domains": ["example.com"]
  }
}
```

### Run Agent Task
```http
POST /agents/{agent_id}/run
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_type": "scrape_url",
  "parameters": {
    "url": "https://example.com/page"
  }
}
```

### Get Agent Status
```http
GET /agents/{agent_id}/status
Authorization: Bearer <token>
```

## Error Responses

All endpoints may return errors in the following format:

```json
{
  "detail": "Error message",
  "type": "ErrorType"
}
```

Common HTTP status codes:
- `400` - Bad Request / Validation Error
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

