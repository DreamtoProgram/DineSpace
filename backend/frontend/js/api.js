/**
 * DineSpace API Client
 */
const API_CONFIG = {
  // Determine API base URL dynamically
  baseUrl: (() => {
    if (typeof window !== 'undefined') {
      if (window.DINESPACE_API_URL) return window.DINESPACE_API_URL;
      const stored = localStorage.getItem('dinespace_api_url');
      if (stored) return stored;
      
      // If hosted on live domain or same origin as backend
      if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
        // If local development port that is not 8000 (e.g. 5500, 3000)
        if ((window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') && 
            window.location.port !== '8000' && window.location.port !== '') {
          return 'http://127.0.0.1:8000/api';
        }
        return '/api';
      }
    }
    return 'http://127.0.0.1:8000/api';
  })(),
  tokenKey: 'dinespace_jwt_token',
  userKey: 'dinespace_user_info'
};

const Auth = {
  getToken() {
    return localStorage.getItem(API_CONFIG.tokenKey);
  },
  setToken(token) {
    localStorage.setItem(API_CONFIG.tokenKey, token);
  },
  removeToken() {
    localStorage.removeItem(API_CONFIG.tokenKey);
    localStorage.removeItem(API_CONFIG.userKey);
  },
  getUser() {
    try {
      const data = localStorage.getItem(API_CONFIG.userKey);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  },
  setUser(user) {
    localStorage.setItem(API_CONFIG.userKey, JSON.stringify(user));
  },
  isAuthenticated() {
    return !!this.getToken();
  },
  logout() {
    this.removeToken();
    window.location.href = 'login.html';
  }
};

async function apiRequest(endpoint, options = {}) {
  const url = API_CONFIG.baseUrl + endpoint;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = Auth.getToken();
  if (token && !headers['Authorization']) {
    headers['Authorization'] = 'Bearer ' + token;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0]?.msg : 'An error occurred.');
      const error = new Error(errorMsg);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    
    return data;
  } catch (err) {
    if (err.status === 401) {
      // Unauthorized token - clear and redirect if on protected page
      if (!window.location.pathname.endsWith('login.html')) {
        Auth.logout();
      }
    }
    throw err;
  }
}

// API Methods
const API = {
  // Auth
  async login(studentId, password) {
    const res = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ studentId, password })
    });
    if (res.accessToken) {
      Auth.setToken(res.accessToken);
    }
    return res;
  },

  async getMe() {
    const res = await apiRequest('/auth/me');
    if (res.student) {
      Auth.setUser(res.student);
    } else if (res.studentId) {
      Auth.setUser(res);
    }
    return res;
  },

  // Health
  async checkHealth() {
    return apiRequest('/health');
  },

  // Status & Crowd
  async getStatus() {
    return apiRequest('/status');
  },

  // Menu
  async getMenuToday() {
    return apiRequest('/menu/today');
  },

  // Seats
  async getSeats() {
    return apiRequest('/seats');
  },

  // Visits
  async getCurrentVisit() {
    return apiRequest('/visits/current');
  },

  async getVisitHistory(limit = 20, offset = 0) {
    return apiRequest('/visits/history?limit=' + limit + '&offset=' + offset);
  },

  // Scans
  async scanEntry(studentId, passCode) {
    return apiRequest('/scan/entry', {
      method: 'POST',
      body: JSON.stringify({ studentId, passCode })
    });
  },

  async scanExit(scanType = 'tray_return') {
    return apiRequest('/scan/exit', {
      method: 'POST',
      body: JSON.stringify({ scanType: scanType || 'tray_return' })
    });
  },

  // Notifications
  async getNotifications(category, unreadOnly = false) {
    let url = '/notifications?';
    if (category && category !== 'All' && category !== 'all') {
      url += 'type=' + encodeURIComponent(category.toLowerCase()) + '&';
    }
    if (unreadOnly) {
      url += 'unreadOnly=true';
    }
    return apiRequest(url);
  },

  async markAllNotificationsRead() {
    return apiRequest('/notifications/read-all', { method: 'PATCH' });
  },

  // Settings
  async getSettings() {
    return apiRequest('/settings');
  },

  async updateSettings(preferences) {
    return apiRequest('/settings', {
      method: 'PATCH',
      body: JSON.stringify(preferences)
    });
  },

  async changePassword(currentPassword, newPassword) {
    return apiRequest('/settings/password', {
      method: 'PATCH',
      body: JSON.stringify({ currentPassword, newPassword })
    });
  }
};