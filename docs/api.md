# API Documentation

## Endpoints

### Generate Budget Tip
Generate a personalized budget breakdown and advice.

**URL**: `/api/tip`
**Method**: `POST`
**Content-Type**: `application/json`

#### Request Body
```json
{
    "budget": "1000",       // Required: Budget amount as string or number
    "duration": "daily"     // Optional: "daily" (default), "weekly", or "monthly"
}
```

#### Success Response
**Code**: `200 OK`
```json
{
    "tip": "Title: Smart Saver's Guide\n\nBreakdown:\n- Food: ₱500\n- Transport: ₱200\n- Utilities: ₱200\n- Others: ₱100\n\nAdvice: Consider bringing baon to work and using water refill stations."
}
```

#### Error Responses

**Invalid Budget**
**Code**: `400 Bad Request`
```json
{
    "tip": "⚠️ Invalid budget value."
}
```

**Server Error**
**Code**: `500 Internal Server Error`
```json
{
    "tip": "⚠️ Something went wrong. Please try again later."
}
```

## Rate Limiting
- IP-based rate limiting: 100 requests per hour
- Enforced per client IP address
- Headers include remaining rate limit information

## Response Format
The tip response is formatted as a Markdown string with the following structure:
```
Title: [Catchy Title]

Breakdown:
- Food: ₱[amount]
- Transport: ₱[amount]
- Utilities: ₱[amount]
- Others: ₱[amount]

Advice: [Practical Filipino-context advice]
```
