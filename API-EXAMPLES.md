# API Examples

This document provides examples of using the BLT-NetGuardian API (Python Worker).

## Base URL

Replace `YOUR_WORKER_URL` with your deployed Cloudflare Python Worker URL:
```
https://blt-netguardian-api.your-subdomain.workers.dev
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Request:**
```bash
curl https://YOUR_WORKER_URL/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "BLT-NetGuardian API is running",
  "timestamp": "2025-12-12T07:15:37.474Z",
  "version": "1.0.0"
}
```

### 2. Get All Alerts

Retrieve all security alerts.

**Request:**
```bash
curl https://YOUR_WORKER_URL/alerts
```

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "severity": "high",
      "type": "suspicious_traffic",
      "message": "Unusual traffic pattern detected from IP 192.168.1.100",
      "timestamp": "2025-12-12T06:15:37.474Z"
    },
    {
      "id": 2,
      "severity": "medium",
      "type": "failed_auth",
      "message": "Multiple failed authentication attempts",
      "timestamp": "2025-12-12T05:15:37.474Z"
    }
  ],
  "count": 2
}
```

### 3. Create New Alert

Create a new security alert.

**Request:**
```bash
curl -X POST https://YOUR_WORKER_URL/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "malware_detected",
    "message": "Malicious file detected in upload directory",
    "severity": "critical"
  }'
```

**Response:**
```json
{
  "success": true,
  "alert": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "severity": "critical",
    "type": "malware_detected",
    "message": "Malicious file detected in upload directory",
    "timestamp": "2025-12-12T07:15:37.474Z"
  }
}
```

**Error Response (Missing Fields):**
```json
{
  "error": "Missing required fields: type and message"
}
```

### 4. Get Statistics

Retrieve system statistics.

**Request:**
```bash
curl https://YOUR_WORKER_URL/stats
```

**Response:**
```json
{
  "total_alerts": 42,
  "alerts_today": 7,
  "critical_alerts": 3,
  "monitored_endpoints": 15,
  "uptime_percentage": 99.9,
  "last_updated": "2025-12-12T07:15:37.474Z"
}
```

## JavaScript Examples

### Using Fetch API

```javascript
// Health check
async function checkHealth() {
  const response = await fetch('https://YOUR_WORKER_URL/health');
  const data = await response.json();
  console.log(data);
}

// Get alerts
async function getAlerts() {
  const response = await fetch('https://YOUR_WORKER_URL/alerts');
  const data = await response.json();
  console.log(data.alerts);
}

// Create alert
async function createAlert(type, message, severity = 'medium') {
  const response = await fetch('https://YOUR_WORKER_URL/alerts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ type, message, severity })
  });
  const data = await response.json();
  console.log(data);
}

// Get stats
async function getStats() {
  const response = await fetch('https://YOUR_WORKER_URL/stats');
  const data = await response.json();
  console.log(data);
}
```

### Using the Frontend Helper

The frontend includes a helper function in `app.js`:

```javascript
// Example: Call any endpoint
const data = await callAPI('/alerts', 'GET');

// Example: Create an alert
const newAlert = await callAPI('/alerts', 'POST', {
  type: 'port_scan',
  message: 'Port scan detected from 10.0.0.5',
  severity: 'high'
});
```

## Error Responses

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "The requested endpoint does not exist"
}
```

### 400 Bad Request
```json
{
  "error": "Invalid JSON body"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

## CORS Support

All endpoints support CORS with the following headers:
- `Access-Control-Allow-Origin: *` (update in production)
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## Authentication

Currently, no authentication is required. For production use, implement authentication using:
- API keys
- JWT tokens
- OAuth 2.0
- Cloudflare Access

## Testing with Postman

You can import these examples into Postman or use the collection below:

1. Create a new collection called "BLT-NetGuardian"
2. Add the base URL as a variable
3. Create requests for each endpoint above

## Next Steps

- Implement database storage (D1, KV, or Durable Objects)
- Add authentication
- Implement rate limiting
- Add more sophisticated alert filtering
- Create webhook support for real-time notifications
