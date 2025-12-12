# BLT-NetGuardian Cloudflare Worker

This directory contains the Cloudflare Worker backend for BLT-NetGuardian.

## Prerequisites

- Node.js (v16 or later)
- npm or yarn
- Cloudflare account
- Wrangler CLI

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Login to Cloudflare (if not already logged in):
   ```bash
   npx wrangler login
   ```

## Development

Run the worker locally:
```bash
npm run dev
```

This will start a local development server, typically at `http://localhost:8787`.

## Deployment

Deploy to Cloudflare Workers:
```bash
npm run deploy
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
npx wrangler secret put SECRET_NAME
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

For production, you should restrict this to your GitHub Pages domain:

```javascript
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://owasp-blt.github.io',
  // ...
};
```

## Monitoring

View real-time logs:
```bash
npm run tail
```

## Testing

Test the deployed worker:
```bash
curl https://your-worker-url.workers.dev/health
```

## Next Steps

1. Replace mock data with actual database integration (D1, KV, or Durable Objects)
2. Add authentication/authorization
3. Implement rate limiting
4. Add more sophisticated error handling
5. Set up monitoring and alerting
