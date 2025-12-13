"""
BLT-NetGuardian Cloudflare Worker API (Python)

This worker handles backend API requests for the BLT-NetGuardian
security monitoring application.
"""

from datetime import datetime, timedelta
from js import Response, Headers, JSON
import json
import uuid

# CORS headers for cross-origin requests from GitHub Pages
# NOTE: Update the origin to match your GitHub Pages domain in production
# Example: 'https://owasp-blt.github.io'
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  # TODO: Restrict to specific domain in production
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}


def create_response(data, status=200):
    """Create a JSON response with CORS headers"""
    headers = Headers.new()
    headers.set('Content-Type', 'application/json')
    for key, value in CORS_HEADERS.items():
        headers.set(key, value)
    
    return Response.new(
        json.dumps(data),
        status=status,
        headers=headers
    )


def handle_options(request):
    """Handle CORS preflight requests"""
    headers = Headers.new()
    for key, value in CORS_HEADERS.items():
        headers.set(key, value)
    return Response.new(None, headers=headers)


def handle_health(request):
    """Health check endpoint"""
    return create_response({
        'status': 'ok',
        'message': 'BLT-NetGuardian API is running',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    })


def handle_get_alerts(request):
    """Get security alerts"""
    # In a real implementation, this would fetch from a database
    now = datetime.utcnow()
    mock_alerts = [
        {
            'id': 1,
            'severity': 'high',
            'type': 'suspicious_traffic',
            'message': 'Unusual traffic pattern detected from IP 192.168.1.100',
            'timestamp': (now - timedelta(hours=1)).isoformat() + 'Z'
        },
        {
            'id': 2,
            'severity': 'medium',
            'type': 'failed_auth',
            'message': 'Multiple failed authentication attempts',
            'timestamp': (now - timedelta(hours=2)).isoformat() + 'Z'
        }
    ]
    
    return create_response({
        'alerts': mock_alerts,
        'count': len(mock_alerts)
    })


async def handle_create_alert(request):
    """Create a new alert"""
    try:
        body_text = await request.text()
        body = json.loads(body_text)
        
        # Validate required fields
        if not body.get('type') or not body.get('message'):
            return create_response({
                'error': 'Missing required fields: type and message'
            }, 400)
        
        # In a real implementation, this would save to a database
        new_alert = {
            'id': str(uuid.uuid4()),
            'severity': body.get('severity', 'medium'),
            'type': body['type'],
            'message': body['message'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return create_response({
            'success': True,
            'alert': new_alert
        }, 201)
    except (json.JSONDecodeError, Exception):
        return create_response({
            'error': 'Invalid JSON body'
        }, 400)


def handle_get_stats(request):
    """Get system statistics"""
    # In a real implementation, this would fetch from a database or analytics service
    stats = {
        'total_alerts': 42,
        'alerts_today': 7,
        'critical_alerts': 3,
        'monitored_endpoints': 15,
        'uptime_percentage': 99.9,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }
    
    return create_response(stats)


async def handle_request(request):
    """Main request handler"""
    url = request.url
    # Parse URL to get pathname
    path = url.split('/', 3)[3] if len(url.split('/', 3)) > 3 else ''
    if path and not path.startswith('/'):
        path = '/' + path
    if not path:
        path = '/'
    
    method = request.method
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return handle_options(request)
    
    # Route handling
    if path == '/health' or path == '/':
        return handle_health(request)
    
    if path == '/alerts':
        if method == 'GET':
            return handle_get_alerts(request)
        elif method == 'POST':
            return await handle_create_alert(request)
    
    if path == '/stats':
        return handle_get_stats(request)
    
    # 404 for unknown routes
    return create_response({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }, 404)


async def on_fetch(request, env):
    """Cloudflare Worker entry point"""
    try:
        return await handle_request(request)
    except Exception as error:
        # Log error and return 500
        print(f'Worker error: {error}')
        return create_response({
            'error': 'Internal server error',
            'message': str(error)
        }, 500)
