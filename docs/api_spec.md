# API Documentation

## Endpoints

### WhatsApp Integration
- `POST /api/whatsapp/webhook`
  - Handles incoming WhatsApp messages
  - Requires authentication header
  - Returns message processing status

### SMS Integration
- `POST /api/sms/webhook`
  - Handles incoming SMS messages
  - Requires API key authentication
  - Returns message processing status

### Health API
- `GET /api/health/vaccines/{age}`
  - Get vaccination schedule for given age
  - Parameters:
    - age: float (in years)
  - Returns vaccination schedule

- `GET /api/health/outbreaks/{location}`
  - Get disease outbreaks for given location
  - Parameters:
    - location: string (city/district name)
  - Returns list of active outbreaks

## Authentication
All API endpoints require authentication using API keys passed in headers:
```
X-API-KEY: your_api_key_here
```

## Response Format
All responses follow the format:
```json
{
    "status": "success|error",
    "data": {},
    "message": "Response message"
}
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error