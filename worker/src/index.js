/**
 * BLT-NetGuardian Cloudflare Worker API
 * 
 * This worker handles backend API requests for the BLT-NetGuardian
 * security monitoring application.
 */

// CORS headers for cross-origin requests from GitHub Pages
// NOTE: Update the origin to match your GitHub Pages domain in production
// Example: 'https://owasp-blt.github.io'
const corsHeaders = {
  'Access-Control-Allow-Origin': '*', // TODO: Restrict to specific domain in production
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

/**
 * Handle CORS preflight requests
 */
function handleOptions(request) {
  return new Response(null, {
    headers: corsHeaders
  });
}

/**
 * Create a JSON response with CORS headers
 */
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    }
  });
}

/**
 * Health check endpoint
 */
function handleHealth(request) {
  return jsonResponse({
    status: 'ok',
    message: 'BLT-NetGuardian API is running',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
}

/**
 * Get security alerts
 */
function handleGetAlerts(request) {
  // In a real implementation, this would fetch from a database
  const mockAlerts = [
    {
      id: 1,
      severity: 'high',
      type: 'suspicious_traffic',
      message: 'Unusual traffic pattern detected from IP 192.168.1.100',
      timestamp: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: 2,
      severity: 'medium',
      type: 'failed_auth',
      message: 'Multiple failed authentication attempts',
      timestamp: new Date(Date.now() - 7200000).toISOString()
    }
  ];

  return jsonResponse({
    alerts: mockAlerts,
    count: mockAlerts.length
  });
}

/**
 * Create a new alert
 */
async function handleCreateAlert(request) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.type || !body.message) {
      return jsonResponse({
        error: 'Missing required fields: type and message'
      }, 400);
    }

    // In a real implementation, this would save to a database
    const newAlert = {
      id: crypto.randomUUID(),
      severity: body.severity || 'medium',
      type: body.type,
      message: body.message,
      timestamp: new Date().toISOString()
    };

    return jsonResponse({
      success: true,
      alert: newAlert
    }, 201);
  } catch (error) {
    return jsonResponse({
      error: 'Invalid JSON body'
    }, 400);
  }
}

/**
 * Get system statistics
 */
function handleGetStats(request) {
  // In a real implementation, this would fetch from a database or analytics service
  const stats = {
    total_alerts: 42,
    alerts_today: 7,
    critical_alerts: 3,
    monitored_endpoints: 15,
    uptime_percentage: 99.9,
    last_updated: new Date().toISOString()
  };

  return jsonResponse(stats);
}

/**
 * Main request handler
 */
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  const method = request.method;

  // Handle CORS preflight
  if (method === 'OPTIONS') {
    return handleOptions(request);
  }

  // Route handling
  if (path === '/health' || path === '/') {
    return handleHealth(request);
  }

  if (path === '/alerts') {
    if (method === 'GET') {
      return handleGetAlerts(request);
    } else if (method === 'POST') {
      return handleCreateAlert(request);
    }
  }

  if (path === '/stats') {
    return handleGetStats(request);
  }

  // 404 for unknown routes
  return jsonResponse({
    error: 'Not found',
    message: 'The requested endpoint does not exist'
  }, 404);
}

/**
 * Cloudflare Worker entry point
 */
export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request);
    } catch (error) {
      // Log error and return 500
      console.error('Worker error:', error);
      return jsonResponse({
        error: 'Internal server error',
        message: error.message
      }, 500);
    }
  }
};
