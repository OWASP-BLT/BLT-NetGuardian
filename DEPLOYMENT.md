# Deployment Guide

This guide walks you through deploying BLT-NetGuardian's frontend and backend.

## Prerequisites

- GitHub account with repository access
- Cloudflare account (free tier is sufficient)
- Node.js v16+ installed locally (for Wrangler CLI)
- Git installed locally

## Part 1: Deploy the Backend (Cloudflare Python Worker)

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

This will open a browser window for authentication.

### Step 3: Deploy the Worker

```bash
cd worker
wrangler deploy
```

You'll see output like:
```
Published blt-netguardian-api (X.XX sec)
  https://blt-netguardian-api.your-subdomain.workers.dev
```

**Important**: Copy this URL! You'll need it for the frontend configuration.

### Step 4: Test the Worker

```bash
curl https://blt-netguardian-api.your-subdomain.workers.dev/health
```

You should receive a JSON response confirming the API is running.

## Part 2: Configure the Frontend

### Step 1: Update API Endpoint

1. Open `app.js` in your editor
2. Find the `CONFIG` object at the top
3. Replace the `API_ENDPOINT` value with your worker URL:

```javascript
const CONFIG = {
    API_ENDPOINT: 'https://blt-netguardian-api.your-subdomain.workers.dev'
};
```

### Step 2: Commit and Push Changes

```bash
git add app.js
git commit -m "Configure Cloudflare Worker endpoint"
git push origin main
```

## Part 3: Deploy the Frontend (GitHub Pages)

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Click **Pages** in the left sidebar
4. Under "Source":
   - Select branch: `main`
   - Select folder: `/ (root)`
5. Click **Save**

### Step 2: Wait for Deployment

GitHub will build and deploy your site. This usually takes 1-2 minutes.

You'll see a green success message with your site URL:
```
Your site is published at https://owasp-blt.github.io/BLT-NetGuardian/
```

### Step 3: Verify Deployment

1. Visit your GitHub Pages URL
2. Click the "Check Backend Status" button
3. You should see a success message if everything is configured correctly

## Part 4: Custom Domain (Optional)

### For GitHub Pages

1. In repository Settings → Pages
2. Add your custom domain under "Custom domain"
3. Configure DNS with your domain provider:
   ```
   Type: CNAME
   Name: www (or your subdomain)
   Value: owasp-blt.github.io
   ```

### For Cloudflare Python Worker

1. Edit `worker/wrangler.toml`
2. Uncomment and configure the routes section:
   ```toml
   routes = [
     { pattern = "api.yourdomain.com/*", zone_name = "yourdomain.com" }
   ]
   ```
3. Deploy again: `wrangler deploy`

## Troubleshooting

### Frontend Issues

**Problem**: "Configuration Needed" message appears
- **Solution**: Make sure you updated `API_ENDPOINT` in `app.js` with your actual worker URL

**Problem**: GitHub Pages not deploying
- **Solution**: Check Settings → Pages for any error messages. Ensure the branch and folder are correct.

### Backend Issues

**Problem**: Worker deployment fails
- **Solution**: Ensure you're logged in with `wrangler login`

**Problem**: CORS errors in browser console
- **Solution**: Verify the worker is deployed and the URL is correct. Check that CORS headers are properly set in `worker/src/index.py`

**Problem**: 404 errors on API calls
- **Solution**: Check that the endpoint paths match between frontend and backend

## Production Checklist

Before going to production:

- [ ] Update CORS settings in worker to restrict to your domain
- [ ] Add rate limiting to the worker
- [ ] Implement authentication if needed
- [ ] Set up monitoring and alerting
- [ ] Configure custom domains
- [ ] Enable HTTPS (automatic with both platforms)
- [ ] Review security settings
- [ ] Test all API endpoints
- [ ] Monitor worker usage and costs

## Monitoring

### Cloudflare Python Worker Logs

View real-time logs:
```bash
cd worker
wrangler tail
```

### GitHub Pages Status

Check deployment status:
- Go to repository → Actions tab
- Look for "pages build and deployment" workflows

## Updating

### Update Frontend

1. Make changes to HTML, CSS, or JS files
2. Commit and push to main branch
3. GitHub Pages will automatically redeploy

### Update Backend

1. Make changes to worker code in `worker/src/index.py`
2. Run `wrangler deploy` from the worker directory
3. No frontend changes needed (same URL)

## Cost Estimates

### GitHub Pages
- **Free** for public repositories
- Unlimited bandwidth
- No build limits for standard sites

### Cloudflare Workers
- **Free tier**: 100,000 requests/day
- **Paid tier**: $5/month for 10 million requests
- Additional requests: $0.50 per million

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review [worker/README.md](worker/README.md) for backend-specific help
3. Open an issue on GitHub
