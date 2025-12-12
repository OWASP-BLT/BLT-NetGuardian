# 🛡️ BLT-NetGuardian

A network security monitoring and threat detection tool built with a GitHub Pages frontend and Cloudflare Worker backend.

## Architecture

This project uses a modern, serverless architecture:

- **Frontend**: Static website hosted on GitHub Pages (HTML, CSS, JavaScript)
- **Backend**: Cloudflare Worker handling API requests

## Features

- 🔍 Real-time network monitoring
- 🚨 Threat detection and alerting
- 📊 Security analytics dashboard
- ⚡ Fast, serverless backend with Cloudflare Workers
- 🌐 Static frontend hosted on GitHub Pages

## Quick Start

### Frontend (GitHub Pages)

The frontend is automatically deployed via GitHub Pages. To view it:

1. Go to repository Settings → Pages
2. Set Source to "Deploy from a branch"
3. Select branch: `main` (or your default branch)
4. Select folder: `/ (root)`
5. Save and wait for deployment

The site will be available at: `https://owasp-blt.github.io/BLT-NetGuardian/`

### Backend (Cloudflare Worker)

1. Navigate to the worker directory:
   ```bash
   cd worker
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Login to Cloudflare:
   ```bash
   npx wrangler login
   ```

4. Deploy the worker:
   ```bash
   npm run deploy
   ```

5. Copy the deployment URL (e.g., `https://blt-netguardian-api.your-subdomain.workers.dev`)

6. Update the frontend configuration:
   - Open `app.js`
   - Replace `API_ENDPOINT` with your worker URL

7. Commit and push the changes

## Development

### Local Development

**Frontend**: Simply open `index.html` in a browser or use a local server:
```bash
python -m http.server 8000
# or
npx serve
```

**Backend**: Run the worker locally:
```bash
cd worker
npm run dev
```

### API Endpoints

- `GET /health` - Health check
- `GET /alerts` - Retrieve security alerts
- `POST /alerts` - Create a new alert
- `GET /stats` - Get system statistics

See [worker/README.md](worker/README.md) for detailed API documentation.

## Configuration

### Frontend Configuration

Edit `app.js` to configure:
- API endpoint URL
- Timeout settings
- Feature flags

### Backend Configuration

Edit `worker/wrangler.toml` to configure:
- Worker name
- Custom domains
- Environment variables

## Deployment

### Automatic Deployment

1. **GitHub Pages**: Automatically deploys on push to main branch
2. **Cloudflare Worker**: Use `npm run deploy` in the worker directory

### Manual Deployment

**GitHub Pages**:
- Enabled in repository settings
- Deploys from root directory of main branch

**Cloudflare Worker**:
```bash
cd worker
npm run deploy
```

## Project Structure

```
BLT-NetGuardian/
├── index.html          # Main HTML page
├── styles.css          # Styling
├── app.js              # Frontend JavaScript
├── worker/             # Cloudflare Worker backend
│   ├── src/
│   │   └── index.js    # Worker code
│   ├── package.json    # Worker dependencies
│   ├── wrangler.toml   # Worker configuration
│   └── README.md       # Worker documentation
├── .gitignore
└── README.md           # This file
```

## Security Considerations

- The backend allows CORS from any origin by default. For production, restrict this to your GitHub Pages domain.
- Consider implementing authentication for API endpoints
- Add rate limiting to prevent abuse
- Use HTTPS for all communications (enforced by both platforms)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms specified in the LICENSE file.

## Part of OWASP BLT

BLT-NetGuardian is part of the [OWASP Bug Logging Tool (BLT)](https://owasp.org/www-project-bug-logging-tool/) project.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/OWASP-BLT/BLT-NetGuardian/issues) page.