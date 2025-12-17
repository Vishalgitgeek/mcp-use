/**
 * MCP Integrations - Frontend Application
 *
 * Sections:
 * 1. Configuration
 * 2. State Management
 * 3. API Calls
 * 4. UI Rendering
 * 5. Event Handlers
 * 6. Initialization
 */

// ============================================
// 1. CONFIGURATION
// ============================================
const CONFIG = {
    API_BASE: window.location.origin,
    INTEGRATIONS: [
        { id: 'gmail', name: 'Gmail', icon: '📧' },
        { id: 'slack', name: 'Slack', icon: '💬' }
    ]
};

// ============================================
// 2. STATE MANAGEMENT
// ============================================
const state = {
    user: null,
    token: localStorage.getItem('token'),
    integrations: [],
    pendingConnection: null,
    oauthError: null
};

// ============================================
// 3. API CALLS
// ============================================
const api = {
    // Get current user info
    async getUser() {
        const res = await fetch(`${CONFIG.API_BASE}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error('Not authenticated');
        return res.json();
    },

    // Get user's connected integrations
    async getIntegrations() {
        const res = await fetch(`${CONFIG.API_BASE}/api/integrations/connected`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error('Failed to fetch integrations');
        return res.json();
    },

    // Initiate OAuth connection
    async connect(provider, forceReauth = false) {
        const res = await fetch(`${CONFIG.API_BASE}/api/integrations/connect`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${state.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ provider, force_reauth: forceReauth })
        });
        if (!res.ok) throw new Error('Failed to initiate connection');
        return res.json();
    },

    // Disconnect integration
    async disconnect(provider) {
        const res = await fetch(`${CONFIG.API_BASE}/api/integrations/${provider}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error('Failed to disconnect');
        return res.json();
    }
};

// ============================================
// 4. UI RENDERING
// ============================================
const ui = {
    // Show specific page
    showPage(pageId) {
        document.querySelectorAll('#login-page, #dashboard, #loading')
            .forEach(el => el.classList.add('hidden'));
        document.getElementById(pageId)?.classList.remove('hidden');
    },

    // Update user email display
    updateUserDisplay() {
        const emailEl = document.getElementById('user-email');
        if (emailEl && state.user) {
            emailEl.textContent = state.user.email;
        }
    },

    // Render integrations list
    renderIntegrations() {
        const container = document.getElementById('integrations-list');
        if (!container) return;

        container.innerHTML = CONFIG.INTEGRATIONS.map(integration => {
            const connected = state.integrations.find(
                i => i.provider === integration.id && i.status === 'active'
            );
            const connectedEmail = connected?.connected_email || '';

            return `
                <div class="integration-card" data-provider="${integration.id}">
                    <div class="integration-info">
                        <span class="integration-icon">${integration.icon}</span>
                        <div>
                            <div class="integration-name">${integration.name}</div>
                            <div class="integration-status ${connected ? 'connected' : ''}">
                                ${connected ? `${connectedEmail || 'Connected'} ✓` : 'Not connected'}
                            </div>
                        </div>
                    </div>
                    ${connected
                        ? `<div class="btn-group">
                            <button class="btn-reconnect" onclick="handlers.reconnect('${integration.id}')">Reconnect</button>
                            <button class="btn-disconnect" onclick="handlers.disconnect('${integration.id}')">Disconnect</button>
                           </div>`
                        : `<button class="btn-connect" onclick="handlers.connect('${integration.id}')">Connect</button>`
                    }
                </div>
            `;
        }).join('');
    }
};

// ============================================
// 5. EVENT HANDLERS
// ============================================
const handlers = {
    // Google login
    login() {
        window.location.href = `${CONFIG.API_BASE}/api/auth/google`;
    },

    // Logout
    logout() {
        localStorage.removeItem('token');
        state.token = null;
        state.user = null;
        ui.showPage('login-page');
    },

    // Connect integration
    async connect(provider) {
        try {
            const result = await api.connect(provider);
            if (result.auth_url) {
                window.location.href = result.auth_url;
            } else if (result.status === 'already_connected') {
                // Already connected, just refresh the list
                await loadIntegrations();
            }
        } catch (error) {
            alert(`Failed to connect ${provider}: ${error.message}`);
        }
    },

    // Disconnect integration
    async disconnect(provider) {
        if (!confirm(`Disconnect ${provider}?`)) return;

        try {
            await api.disconnect(provider);
            await loadIntegrations();
        } catch (error) {
            alert(`Failed to disconnect: ${error.message}`);
        }
    },

    // Reconnect integration (force re-authentication)
    async reconnect(provider) {
        if (!confirm(`Re-authenticate ${provider}? This will require you to authorize access again.`)) return;

        try {
            const result = await api.connect(provider, true); // force_reauth = true
            if (result.auth_url) {
                window.location.href = result.auth_url;
            }
        } catch (error) {
            alert(`Failed to reconnect ${provider}: ${error.message}`);
        }
    },

    // Debug: Show all Composio connections
    async debugConnections() {
        try {
            const res = await fetch(`${CONFIG.API_BASE}/api/integrations/debug/connections`, {
                headers: { 'Authorization': `Bearer ${state.token}` }
            });
            const data = await res.json();
            console.log('DEBUG: All Composio connections:', data);
            alert(`Found ${data.count || 0} Composio connections. Check browser console (F12) for details.`);
        } catch (error) {
            console.error('Debug error:', error);
            alert(`Debug failed: ${error.message}`);
        }
    }
};

// ============================================
// 6. INITIALIZATION
// ============================================

// Load user integrations
async function loadIntegrations() {
    try {
        const data = await api.getIntegrations();
        state.integrations = data.integrations || [];
        ui.renderIntegrations();
    } catch (error) {
        console.error('Failed to load integrations:', error);
    }
}

// Check for OAuth callback parameters in URL
function checkOAuthCallback() {
    const params = new URLSearchParams(window.location.search);

    // Handle Google login token
    const token = params.get('token');
    if (token) {
        localStorage.setItem('token', token);
        state.token = token;
    }

    // Handle integration OAuth callback (connected=gmail)
    const connected = params.get('connected');
    if (connected) {
        state.pendingConnection = connected;
    }

    // Handle OAuth error
    const error = params.get('error');
    if (error) {
        state.oauthError = error;
    }

    // Clean URL
    if (token || connected || error) {
        window.history.replaceState({}, '', window.location.pathname);
    }
}

// Complete pending integration connection
async function completePendingConnection() {
    if (!state.pendingConnection || !state.token) return;

    const provider = state.pendingConnection;
    state.pendingConnection = null;

    try {
        // Call the complete endpoint to update MongoDB
        await fetch(`${CONFIG.API_BASE}/api/integrations/callback/complete?provider=${provider}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${state.token}`,
                'Content-Type': 'application/json'
            }
        });
        console.log(`Completed connection for ${provider}`);
    } catch (error) {
        console.error(`Failed to complete connection for ${provider}:`, error);
    }
}

// Initialize app
async function init() {
    checkOAuthCallback();

    // Setup event listeners
    document.getElementById('google-login-btn')?.addEventListener('click', handlers.login);
    document.getElementById('logout-btn')?.addEventListener('click', handlers.logout);

    // Check authentication
    if (!state.token) {
        ui.showPage('login-page');
        return;
    }

    try {
        state.user = await api.getUser();
        ui.updateUserDisplay();

        // Complete any pending OAuth connection before loading integrations
        await completePendingConnection();

        await loadIntegrations();
        ui.showPage('dashboard');

        // Show error if OAuth failed
        if (state.oauthError) {
            alert(`OAuth error: ${state.oauthError}`);
            state.oauthError = null;
        }
    } catch (error) {
        // Token invalid, show login
        localStorage.removeItem('token');
        ui.showPage('login-page');
    }
}

// Start app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
