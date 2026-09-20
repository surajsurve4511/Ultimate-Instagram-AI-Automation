/**
 * InstaAutomate — Frontend Application
 * Vanilla JS SPA with client-side routing
 */

const API_BASE = window.location.origin;

// ========== State ==========
const state = {
    token: localStorage.getItem('auth_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    currentPage: 'dashboard',
};

// ========== API Client ==========
async function api(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const headers = {
        'Content-Type': 'application/json',
        ...(state.token ? { 'Authorization': `Bearer ${state.token}` } : {}),
        ...options.headers,
    };

    try {
        const res = await fetch(url, { ...options, headers });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
        return data;
    } catch (e) {
        console.error(`API Error [${path}]:`, e);
        throw e;
    }
}

// ========== Toast Notifications ==========
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✓', error: '✗', info: 'ℹ', warning: '⚠' };
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ========== Routing ==========
const routes = {
    login: renderLogin,
    dashboard: renderDashboard,
    content: renderContent,
    calendar: renderCalendar,
    campaigns: renderCampaigns,
};

function navigate(page) {
    state.currentPage = page;
    window.location.hash = page;
    render();
}

function render() {
    const page = window.location.hash.slice(1) || 'dashboard';
    state.currentPage = page;

    if (page === 'login') {
        document.getElementById('app').innerHTML = '';
        routes.login();
        return;
    }

    renderAppShell();
    const pageContent = document.getElementById('page-content');
    if (pageContent && routes[page]) {
        routes[page]();
    }
}

// ========== App Shell (Sidebar + Header) ==========
function renderAppShell() {
    const app = document.getElementById('app');
    app.innerHTML = `
    <div class="app-layout">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-logo">
                <div class="logo-icon">🚀</div>
                <h1>InstaAutomate</h1>
            </div>
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <div class="nav-section-title">Main</div>
                    <a class="nav-item ${state.currentPage === 'dashboard' ? 'active' : ''}" onclick="navigate('dashboard')">
                        <span class="nav-icon">📊</span> Dashboard
                    </a>
                    <a class="nav-item ${state.currentPage === 'content' ? 'active' : ''}" onclick="navigate('content')">
                        <span class="nav-icon">✨</span> Content Studio
                    </a>
                    <a class="nav-item ${state.currentPage === 'calendar' ? 'active' : ''}" onclick="navigate('calendar')">
                        <span class="nav-icon">📅</span> Calendar
                    </a>
                    <a class="nav-item ${state.currentPage === 'campaigns' ? 'active' : ''}" onclick="navigate('campaigns')">
                        <span class="nav-icon">🎯</span> Campaigns
                    </a>
                </div>
                <div class="nav-section">
                    <div class="nav-section-title">System</div>
                    <a class="nav-item" onclick="checkHealth()">
                        <span class="nav-icon">💚</span> System Health
                    </a>
                    <a class="nav-item" onclick="navigate('login')">
                        <span class="nav-icon">🚪</span> Logout
                    </a>
                </div>
            </nav>
            <div class="sidebar-footer">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="status-dot online"></span>
                    <span style="font-size:var(--font-size-xs);color:var(--text-secondary)">System Online</span>
                </div>
            </div>
        </aside>

        <main class="main-content">
            <header class="main-header">
                <h2 id="page-title">${getPageTitle()}</h2>
                <div class="header-actions">
                    <button class="btn btn-ghost btn-icon" onclick="checkHealth()" title="System Health">💚</button>
                    <button class="btn btn-primary btn-sm" onclick="navigate('content')">+ Create</button>
                </div>
            </header>
            <div class="page-content" id="page-content">
            </div>
        </main>
    </div>`;
}

function getPageTitle() {
    const titles = {
        dashboard: 'Dashboard',
        content: 'Content Studio',
        calendar: 'Content Calendar',
        campaigns: 'Campaigns',
    };
    return titles[state.currentPage] || 'Dashboard';
}

// ========== Login Page ==========
function renderLogin() {
    document.getElementById('app').innerHTML = `
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-logo">
                <h1>🚀 InstaAutomate</h1>
                <p>AI-Powered Instagram Automation</p>
            </div>
            <form id="login-form" onsubmit="handleLogin(event)">
                <div class="input-group">
                    <label>Email</label>
                    <input class="input" type="email" id="login-email" placeholder="you@example.com" required>
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input class="input" type="password" id="login-password" placeholder="••••••••" required>
                </div>
                <button class="btn btn-primary btn-lg" type="submit" style="width:100%;justify-content:center;margin-top:var(--space-md)">
                    Sign In
                </button>
            </form>
            <div style="text-align:center;margin-top:var(--space-lg);">
                <span style="color:var(--text-tertiary);font-size:var(--font-size-sm)">
                    Don't have an account? 
                </span>
                <a href="#" onclick="showRegister()" style="font-size:var(--font-size-sm)">Sign Up</a>
            </div>
            <div style="margin-top:var(--space-xl);padding-top:var(--space-lg);border-top:1px solid var(--border-color);text-align:center;">
                <button class="btn btn-ghost btn-sm" onclick="navigate('dashboard')" style="color:var(--text-tertiary)">
                    Skip → Enter Dashboard
                </button>
            </div>
        </div>
    </div>`;
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const data = await api('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        state.token = data.access_token;
        localStorage.setItem('auth_token', data.access_token);
        showToast('Welcome back!', 'success');
        navigate('dashboard');
    } catch (e) {
        showToast('Login failed: ' + e.message, 'error');
    }
}

function showRegister() {
    document.querySelector('.auth-card').innerHTML = `
        <div class="auth-logo">
            <h1>🚀 InstaAutomate</h1>
            <p>Create your account</p>
        </div>
        <form onsubmit="handleRegister(event)">
            <div class="input-group">
                <label>Email</label>
                <input class="input" type="email" id="reg-email" placeholder="you@example.com" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input class="input" type="password" id="reg-password" placeholder="••••••••" required minlength="8">
            </div>
            <div class="input-group">
                <label>Confirm Password</label>
                <input class="input" type="password" id="reg-confirm" placeholder="••••••••" required>
            </div>
            <button class="btn btn-primary btn-lg" type="submit" style="width:100%;justify-content:center;margin-top:var(--space-md)">
                Create Account
            </button>
        </form>
        <div style="text-align:center;margin-top:var(--space-lg);">
            <a href="#" onclick="renderLogin()" style="font-size:var(--font-size-sm)">← Back to login</a>
        </div>`;
}

async function handleRegister(e) {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;

    if (password !== confirm) {
        showToast('Passwords do not match', 'error');
        return;
    }

    try {
        await api('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        showToast('Account created! Please login.', 'success');
        renderLogin();
    } catch (e) {
        showToast('Registration failed: ' + e.message, 'error');
    }
}

// ========== Dashboard Page ==========
async function renderDashboard() {
    const pc = document.getElementById('page-content');
    pc.innerHTML = `
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-label">System Status</div>
            <div class="stat-value" id="stat-status">...</div>
            <div class="stat-change up" id="stat-uptime">Loading...</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">AI Engine</div>
            <div class="stat-value" id="stat-ai">...</div>
            <div class="stat-change" id="stat-ai-model">—</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Scheduler Jobs</div>
            <div class="stat-value" id="stat-jobs">...</div>
            <div class="stat-change" id="stat-next-run">—</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Error Count</div>
            <div class="stat-value" id="stat-errors">...</div>
            <div class="stat-change" id="stat-error-detail">—</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Quick Actions</div>
                    <div class="card-subtitle">Jump into your most common tasks</div>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:var(--space-sm);">
                <button class="btn btn-secondary" onclick="navigate('content')" style="justify-content:flex-start;">
                    ✨ Generate Content
                </button>
                <button class="btn btn-secondary" onclick="navigate('campaigns')" style="justify-content:flex-start;">
                    🎯 Create Campaign
                </button>
                <button class="btn btn-secondary" onclick="navigate('calendar')" style="justify-content:flex-start;">
                    📅 View Calendar
                </button>
                <button class="btn btn-secondary" onclick="checkHealth()" style="justify-content:flex-start;">
                    💚 Check System Health
                </button>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Recent Errors</div>
                    <div class="card-subtitle">Last reported issues</div>
                </div>
                <span class="badge badge-success" id="error-badge">All Clear</span>
            </div>
            <div id="error-list" style="font-size:var(--font-size-sm);color:var(--text-secondary);">
                Loading...
            </div>
        </div>
    </div>`;

    // Fetch health data
    try {
        const health = await api('/health');
        document.getElementById('stat-status').textContent = health.status === 'healthy' ? '✓ OK' : '⚠ Issue';
        document.getElementById('stat-uptime').textContent = 'System: ' + health.status;

        if (health.ai) {
            document.getElementById('stat-ai').textContent = health.ai.reasoning ? '✓ Ready' : '✗ Down';
            document.getElementById('stat-ai-model').textContent = 'Gemini 2.5 Flash';
        }

        if (health.scheduler) {
            const jobCount = health.scheduler.jobs ? health.scheduler.jobs.length : 0;
            document.getElementById('stat-jobs').textContent = jobCount;
            document.getElementById('stat-next-run').textContent = health.scheduler.running ? 'Running' : 'Stopped';
        }

        if (health.errors !== undefined) {
            const errCount = typeof health.errors === 'object' ? health.errors.total : health.errors;
            document.getElementById('stat-errors').textContent = errCount || 0;
            document.getElementById('stat-error-detail').textContent = errCount === 0 ? 'All clear' : errCount + ' tracked';
        }
    } catch (e) {
        document.getElementById('stat-status').textContent = '✗ Error';
        document.getElementById('stat-uptime').textContent = e.message;
    }

    // Fetch errors
    try {
        const errors = await api('/debug/errors');
        const errorList = document.getElementById('error-list');
        if (errors.recent && errors.recent.length > 0) {
            document.getElementById('error-badge').className = 'badge badge-error';
            document.getElementById('error-badge').textContent = errors.recent.length + ' errors';
            errorList.innerHTML = errors.recent.slice(0, 5).map(err => `
                <div style="padding:8px 0;border-bottom:1px solid var(--border-color);">
                    <div style="color:var(--error);font-weight:500;">${err.component || 'unknown'}.${err.operation || ''}</div>
                    <div style="color:var(--text-tertiary);font-size:var(--font-size-xs);">${err.error || err.message || 'Unknown error'}</div>
                </div>
            `).join('');
        } else {
            errorList.innerHTML = '<div style="color:var(--success);">No recent errors ✓</div>';
        }
    } catch (e) {
        document.getElementById('error-list').innerHTML = '<div>Could not fetch errors</div>';
    }
}

// ========== Content Studio ==========
function renderContent() {
    const pc = document.getElementById('page-content');
    pc.innerHTML = `
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Generate Content</div>
                    <div class="card-subtitle">AI-powered post creation</div>
                </div>
            </div>
            <div class="input-group">
                <label>Topic</label>
                <input class="input" id="gen-topic" placeholder="e.g., Top 5 AI tools for students">
            </div>
            <div class="input-group">
                <label>Content Type</label>
                <select class="input" id="gen-type">
                    <option value="IMAGE">Single Image Post</option>
                    <option value="CAROUSEL">Carousel</option>
                    <option value="REELS">Reel Script</option>
                    <option value="STORIES">Story</option>
                </select>
            </div>
            <div class="input-group">
                <label>Niche</label>
                <input class="input" id="gen-niche" placeholder="e.g., AI education" value="technology">
            </div>
            <div class="input-group">
                <label>Target Audience</label>
                <input class="input" id="gen-audience" placeholder="e.g., aspiring AI engineers" value="tech enthusiasts">
            </div>
            <div class="input-group">
                <label>Brand Voice</label>
                <input class="input" id="gen-voice" placeholder="e.g., Friendly educator" value="professional and engaging">
            </div>
            <div class="input-group">
                <label>Funnel Stage</label>
                <select class="input" id="gen-funnel">
                    <option value="TOFU">TOFU — Awareness & Reach</option>
                    <option value="MOFU">MOFU — Educational & Trust</option>
                    <option value="BOFU">BOFU — Conversion & CTA</option>
                    <option value="RETENTION">RETENTION — Community</option>
                </select>
            </div>
            <div style="display:flex;gap:var(--space-md);margin-top:var(--space-lg);">
                <button class="btn btn-primary" onclick="generateContent()" id="gen-btn">
                    ✨ Generate
                </button>
                <button class="btn btn-secondary" onclick="suggestTopics()">
                    💡 Suggest Topics
                </button>
            </div>
            <div id="topic-suggestions" style="margin-top:var(--space-md);display:none;"></div>
        </div>

        <div class="card" id="content-result">
            <div class="card-header">
                <div>
                    <div class="card-title">Preview</div>
                    <div class="card-subtitle">Generated content will appear here</div>
                </div>
            </div>
            <div id="preview-area" style="color:var(--text-secondary);text-align:center;padding:var(--space-2xl);">
                <div style="font-size:48px;margin-bottom:var(--space-md);">✨</div>
                <div>Enter a topic and click Generate</div>
            </div>
        </div>
    </div>`;
}

async function generateContent() {
    const btn = document.getElementById('gen-btn');
    btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Generating...';
    btn.disabled = true;

    try {
        const data = await api('/api/content/generate', {
            method: 'POST',
            body: JSON.stringify({
                topic: document.getElementById('gen-topic').value,
                content_type: document.getElementById('gen-type').value,
                niche: document.getElementById('gen-niche').value,
                target_audience: document.getElementById('gen-audience').value,
                brand_voice: document.getElementById('gen-voice').value,
                funnel_stage: document.getElementById('gen-funnel').value,
            }),
        });

        const preview = document.getElementById('preview-area');
        const plan = data.plan || data;

        preview.innerHTML = `
            <div class="content-preview">
                <div class="content-preview-header">
                    <span class="badge badge-primary">${data.content_type || 'IMAGE'}</span>
                    <span class="badge badge-info">${data.funnel_stage || 'TOFU'}</span>
                    ${data.quality_score ? `<span class="badge ${data.quality_score >= 0.7 ? 'badge-success' : 'badge-warning'}">Quality: ${(data.quality_score * 100).toFixed(0)}%</span>` : ''}
                </div>
                <div class="content-preview-body">
                    <div class="caption">${plan.caption || 'No caption generated'}</div>
                    <div class="hashtags">${(plan.hashtags || []).map(h => '#' + h).join(' ')}</div>
                    ${plan.call_to_action ? `<div style="margin-top:var(--space-md);padding:var(--space-md);background:rgba(139,92,246,0.1);border-radius:var(--radius-md);font-size:var(--font-size-sm);"><strong>CTA:</strong> ${plan.call_to_action}</div>` : ''}
                    ${plan.alt_text ? `<div style="margin-top:var(--space-sm);font-size:var(--font-size-xs);color:var(--text-tertiary);">Alt: ${plan.alt_text}</div>` : ''}
                </div>
            </div>`;

        showToast('Content generated successfully!', 'success');
    } catch (e) {
        showToast('Generation failed: ' + e.message, 'error');
    } finally {
        btn.innerHTML = '✨ Generate';
        btn.disabled = false;
    }
}

async function suggestTopics() {
    const container = document.getElementById('topic-suggestions');
    container.style.display = 'block';
    container.innerHTML = '<div class="spinner"></div>';

    try {
        const data = await api('/api/content/suggest-topics', {
            method: 'POST',
            body: JSON.stringify({
                niche: document.getElementById('gen-niche').value,
                target_audience: document.getElementById('gen-audience').value,
                content_pillars: ['tutorials', 'news', 'insights'],
            }),
        });

        const topics = data.topics || data;
        container.innerHTML = `
            <div style="font-size:var(--font-size-sm);font-weight:600;margin-bottom:var(--space-sm);">
                💡 Suggested Topics
            </div>
            ${(Array.isArray(topics) ? topics : [topics]).map(t => `
                <div class="calendar-slot" onclick="document.getElementById('gen-topic').value='${String(t).replace(/'/g, "\\'")}'">
                    ${t}
                </div>
            `).join('')}`;
    } catch (e) {
        container.innerHTML = '<div style="color:var(--error);">Could not suggest topics</div>';
    }
}

// ========== Calendar ==========
function renderCalendar() {
    const pc = document.getElementById('page-content');
    const today = new Date();
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // Generate 4 weeks
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());

    let days = [];
    for (let i = 0; i < 28; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        days.push(d);
    }

    pc.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-lg);">
        <div>
            <h3 style="font-size:var(--font-size-xl);">${today.toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>
        </div>
        <div style="display:flex;gap:var(--space-sm);">
            <button class="btn btn-secondary btn-sm" onclick="planWeek()">📅 Auto-Plan Week</button>
        </div>
    </div>

    <div class="calendar-grid">
        ${dayNames.map(d => `<div class="calendar-day-header">${d}</div>`).join('')}
        ${days.map(d => {
        const isToday = d.toDateString() === today.toDateString();
        return `
            <div class="calendar-day" style="${isToday ? 'border:1px solid var(--accent-primary);' : ''}">
                <div class="day-number" style="${isToday ? 'color:var(--accent-primary);font-weight:700;' : ''}">${d.getDate()}</div>
                <div id="cal-${d.toISOString().split('T')[0]}"></div>
            </div>`;
    }).join('')}
    </div>

    <div id="week-plan" style="margin-top:var(--space-xl);"></div>`;
}

async function planWeek() {
    showToast('Planning week...', 'info');
    try {
        const data = await api('/api/campaigns/plan-week?posts_per_day=2&days=7');
        const plan = data.plan || [];

        const weekPlan = document.getElementById('week-plan');
        weekPlan.innerHTML = `
        <div class="card">
            <div class="card-header">
                <div class="card-title">AI-Planned Week (${plan.length} slots)</div>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Slot</th>
                            <th>Funnel Stage</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${plan.map(p => `
                        <tr>
                            <td>Day ${p.day}</td>
                            <td>Slot ${p.slot}</td>
                            <td><span class="badge badge-primary">${p.funnel_stage}</span></td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>`;

        showToast(`Week planned: ${plan.length} slots`, 'success');
    } catch (e) {
        showToast('Planning failed: ' + e.message, 'error');
    }
}

// ========== Campaigns ==========
function renderCampaigns() {
    const pc = document.getElementById('page-content');
    pc.innerHTML = `
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Create Campaign</div>
                    <div class="card-subtitle">Multi-day coordinated content</div>
                </div>
            </div>
            <div class="input-group">
                <label>Campaign Name</label>
                <input class="input" id="camp-name" placeholder="e.g., AI Week">
            </div>
            <div class="input-group">
                <label>Theme</label>
                <input class="input" id="camp-theme" placeholder="e.g., The future of AI in everyday life">
            </div>
            <div class="input-group">
                <label>Goal</label>
                <input class="input" id="camp-goal" placeholder="e.g., Increase engagement by 20%">
            </div>
            <div style="display:flex;gap:var(--space-md);">
                <div class="input-group" style="flex:1;">
                    <label>Duration (days)</label>
                    <input class="input" type="number" id="camp-days" value="7" min="1" max="30">
                </div>
                <div class="input-group" style="flex:1;">
                    <label>Posts / Day</label>
                    <input class="input" type="number" id="camp-ppd" value="1" min="1" max="5">
                </div>
            </div>
            <div class="input-group">
                <label>Niche</label>
                <input class="input" id="camp-niche" value="technology">
            </div>
            <button class="btn btn-primary" onclick="createCampaign()" id="camp-btn" style="margin-top:var(--space-md);">
                🎯 Create & Plan Campaign
            </button>
        </div>

        <div class="card" id="campaign-result">
            <div class="card-header">
                <div>
                    <div class="card-title">Campaign Plan</div>
                    <div class="card-subtitle">AI-generated content plan will appear here</div>
                </div>
            </div>
            <div id="campaign-plan" style="color:var(--text-secondary);text-align:center;padding:var(--space-2xl);">
                <div style="font-size:48px;margin-bottom:var(--space-md);">🎯</div>
                <div>Create a campaign to see the plan</div>
            </div>
        </div>
    </div>`;
}

async function createCampaign() {
    const btn = document.getElementById('camp-btn');
    btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Planning...';
    btn.disabled = true;

    try {
        const data = await api('/api/campaigns/create', {
            method: 'POST',
            body: JSON.stringify({
                name: document.getElementById('camp-name').value,
                theme: document.getElementById('camp-theme').value,
                goal: document.getElementById('camp-goal').value,
                duration_days: parseInt(document.getElementById('camp-days').value),
                posts_per_day: parseInt(document.getElementById('camp-ppd').value),
                niche: document.getElementById('camp-niche').value,
            }),
        });

        const planDiv = document.getElementById('campaign-plan');
        planDiv.innerHTML = `
            <div style="text-align:left;">
                <div style="display:flex;align-items:center;gap:var(--space-md);margin-bottom:var(--space-lg);">
                    <span class="badge badge-success">${data.campaign.status}</span>
                    <span style="font-weight:600;">${data.campaign.name}</span>
                    <span style="color:var(--text-secondary);font-size:var(--font-size-sm);">
                        ${data.total_posts} posts over ${data.campaign.duration_days} days
                    </span>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Day</th>
                                <th>Topic</th>
                                <th>Type</th>
                                <th>Stage</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${(data.plan || []).map(p => `
                            <tr>
                                <td>${p.day}</td>
                                <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;">${p.topic}</td>
                                <td><span class="badge badge-info">${p.content_type}</span></td>
                                <td><span class="badge badge-primary">${p.funnel_stage}</span></td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>`;

        showToast(`Campaign "${data.campaign.name}" planned!`, 'success');
    } catch (e) {
        showToast('Campaign creation failed: ' + e.message, 'error');
    } finally {
        btn.innerHTML = '🎯 Create & Plan Campaign';
        btn.disabled = false;
    }
}

// ========== Health Check ==========
async function checkHealth() {
    try {
        const health = await api('/health');
        let msg = `Status: ${health.status}`;
        if (health.ai) msg += ` | AI: ${health.ai.reasoning ? '✓' : '✗'}`;
        if (health.scheduler) msg += ` | Scheduler: ${health.scheduler.running ? 'Running' : 'Stopped'}`;
        showToast(msg, health.status === 'healthy' ? 'success' : 'warning');
    } catch (e) {
        showToast('Health check failed: ' + e.message, 'error');
    }
}

// ========== Init ==========
window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);
