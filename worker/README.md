# BLT-NetGuardian Cloudflare Worker (Python)

This directory contains the Cloudflare Python Worker backend for BLT-NetGuardian.

## Prerequisites

- Python 3.7+ (for local development)
- Cloudflare account
- Wrangler CLI (v3.0+)

## About Python Workers

This worker uses Cloudflare's Python Workers, which run on the Pyodide runtime. The Python code is executed directly on Cloudflare's edge network.

## Setup

1. Install Wrangler CLI globally:
   ```bash
   npm install -g wrangler
   ```

2. Login to Cloudflare (if not already logged in):
   ```bash
   wrangler login
   ```

## Development

Run the worker locally:
```bash
wrangler dev
```

This will start a local development server, typically at `http://localhost:8787`.

## Deployment

Deploy to Cloudflare Workers:
```bash
wrangler deploy
```

After deployment, you'll receive a URL like:
```
https://blt-netguardian-api.your-subdomain.workers.dev
```

Update this URL in the frontend's `app.js` file (CONFIG.API_ENDPOINT).

## API Endpoints

### Health Check
- **GET** `/health`
- Returns the API status and version

### Alerts
- **GET** `/alerts` - Get all security alerts
- **POST** `/alerts` - Create a new alert
  ```json
  {
    "type": "string",
    "message": "string",
    "severity": "low|medium|high|critical"
  }
  ```

### Statistics
- **GET** `/stats` - Get system statistics

## Configuration

### Environment Variables

You can set environment variables in the Cloudflare dashboard or using wrangler secrets:

```bash
wrangler secret put SECRET_NAME
```

### Custom Domain

To use a custom domain, uncomment and configure the routes in `wrangler.toml`:

```toml
routes = [
  { pattern = "api.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

## CORS Configuration

The worker is configured to allow cross-origin requests from any origin (`*`). 

For production, you should restrict this to your GitHub Pages domain by editing `src/index.py`:

```python
CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://owasp-blt.github.io',
    # ...
}
```

## Monitoring

View real-time logs:
```bash
wrangler tail
```

## Testing

Test the deployed worker:
```bash
curl https://your-worker-url.workers.dev/health
```

## Python Workers Limitations

- Limited to Pyodide-compatible packages
- No access to native C extensions
- File system access is restricted
- Network requests use the Fetch API

## Next Steps

1. Replace mock data with actual database integration (D1, KV, or Durable Objects)
2. Add authentication/authorization
3. Implement rate limiting
4. Add more sophisticated error handling
5. Set up monitoring and alerting

## Local Development with Python

For local testing of the Python logic (not the full worker):

```bash
python3 src/index.py
```

Note: This will not run the full Cloudflare Worker environment. Use `wrangler dev` for proper testing.
