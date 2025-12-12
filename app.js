// Configuration
const CONFIG = {
    // Update this with your Cloudflare Worker URL after deployment
    API_ENDPOINT: 'https://your-worker-name.your-subdomain.workers.dev'
};

// Check if we're in development mode (local file or localhost)
const isDevelopment = window.location.protocol === 'file:' || window.location.hostname === 'localhost';

// DOM Elements
const checkStatusBtn = document.getElementById('checkStatus');
const statusResult = document.getElementById('statusResult');

// Event Listeners
checkStatusBtn.addEventListener('click', checkBackendStatus);

/**
 * Check the backend API status
 */
async function checkBackendStatus() {
    try {
        // Disable button and show loading state
        checkStatusBtn.disabled = true;
        statusResult.className = 'status-result loading';
        statusResult.textContent = 'Checking backend status...';

        // Make API request
        const response = await fetch(`${CONFIG.API_ENDPOINT}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display success
        statusResult.className = 'status-result success';
        statusResult.innerHTML = `
            <strong>✅ Backend is online!</strong><br>
            Status: ${data.status || 'OK'}<br>
            Timestamp: ${data.timestamp || new Date().toISOString()}
        `;
    } catch (error) {
        // Display error
        statusResult.className = 'status-result error';
        
        if (isDevelopment && CONFIG.API_ENDPOINT.includes('your-worker-name')) {
            statusResult.innerHTML = `
                <strong>⚙️ Configuration Needed</strong><br>
                Please update the API_ENDPOINT in app.js with your deployed Cloudflare Worker URL.<br>
                <small>Error: ${error.message}</small>
            `;
        } else {
            statusResult.innerHTML = `
                <strong>❌ Backend connection failed</strong><br>
                ${error.message}<br>
                <small>Please check that the Cloudflare Worker is deployed and the URL is correct.</small>
            `;
        }
    } finally {
        // Re-enable button
        checkStatusBtn.disabled = false;
    }
}

/**
 * Example function for future API calls
 */
async function callAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${CONFIG.API_ENDPOINT}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('BLT-NetGuardian initialized');
    
    if (isDevelopment && CONFIG.API_ENDPOINT.includes('your-worker-name')) {
        console.warn('⚠️ Please configure your Cloudflare Worker URL in app.js');
    }
});
