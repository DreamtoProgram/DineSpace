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
  userKey: 'dinespace_user_info',
  hallKey: 'dinespace_selected_hall'
};

const Auth = {
  getToken() {
    return localStorage.getItem(API_CONFIG.tokenKey) || localStorage.getItem('dinespace_token');
  },
  setToken(token) {
    localStorage.setItem(API_CONFIG.tokenKey, token);
    localStorage.setItem('dinespace_token', token);
  },
  removeToken() {
    localStorage.removeItem(API_CONFIG.tokenKey);
    localStorage.removeItem('dinespace_token');
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
  getSelectedHall() {
    return localStorage.getItem(API_CONFIG.hallKey) || 'Central Mess';
  },
  setSelectedHall(hallName) {
    if (!hallName) return;
    localStorage.setItem(API_CONFIG.hallKey, hallName);
    try {
      window.dispatchEvent(new CustomEvent('dinespace_hall_changed', { detail: { hallName } }));
    } catch (e) {}
  },
  isAuthenticated() {
    return !!this.getToken();
  },
  isDemoSession() {
    const token = this.getToken();
    return !!(token && (token.startsWith('demo_') || token.startsWith('demo_token_')));
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

  // Network timeout to prevent hung requests
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 4000);

  const config = {
    ...options,
    headers,
    signal: controller.signal
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);
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
    clearTimeout(timeoutId);
    // Never auto-logout if in demo/offline session or if request was aborted
    if (err.status === 401 && !Auth.isDemoSession()) {
      // Only logout if the primary profile endpoint explicitly rejected an expired token
      if (endpoint === '/auth/me' && !window.location.pathname.endsWith('login.html')) {
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

  async loginSSO(provider, token = null, email = null, name = null) {
    const res = await apiRequest('/auth/sso/login', {
      method: 'POST',
      body: JSON.stringify({ provider, token, email, name })
    });
    if (res.accessToken) {
      Auth.setToken(res.accessToken);
    }
    if (res.student) {
      Auth.setUser(res.student);
    }
    return res;
  },

  async loginRFID(cardUid, diningHall = null) {
    const res = await apiRequest('/auth/rfid/tap', {
      method: 'POST',
      body: JSON.stringify({ cardUid, diningHall })
    });
    if (res.accessToken) {
      Auth.setToken(res.accessToken);
    }
    if (res.student) {
      Auth.setUser(res.student);
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

  // Dining Facilities
  async getDiningHalls() {
    return apiRequest('/halls');
  },

  // Status & Crowd
  async getStatus(diningHall = null) {
    const hall = diningHall || Auth.getSelectedHall();
    const query = hall ? '?diningHall=' + encodeURIComponent(hall) : '';
    return apiRequest('/status' + query);
  },

  // Menu
  async getMenuToday(diningHall = null) {
    const hall = diningHall || Auth.getSelectedHall();
    const query = hall ? '?diningHall=' + encodeURIComponent(hall) : '';
    return apiRequest('/menu/today' + query);
  },

  // Seats
  async getSeats(diningHall = null) {
    const hall = diningHall || Auth.getSelectedHall();
    const query = hall ? '?diningHall=' + encodeURIComponent(hall) : '';
    return apiRequest('/seats' + query);
  },

  // Visits
  async getCurrentVisit() {
    return apiRequest('/visits/current');
  },

  async getVisitHistory(limit = 20, offset = 0) {
    return apiRequest('/visits/history?limit=' + limit + '&offset=' + offset);
  },

  // Scans
  async scanEntry(studentId, passCode, diningHall = null) {
    return apiRequest('/scan/entry', {
      method: 'POST',
      body: JSON.stringify({ studentId, passCode, diningHall })
    });
  },

  async scanNFCEntry(cardUid, diningHall = null) {
    return apiRequest('/scan/nfc-entry', {
      method: 'POST',
      body: JSON.stringify({ cardUid, diningHall })
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
  },

  // --- Admin Portal Methods ---
  async getAdminAnalytics(diningHall = 'Central Mess') {
    return apiRequest('/admin/analytics?diningHall=' + encodeURIComponent(diningHall));
  },

  async getAdminSeats(diningHall = 'Central Mess') {
    return apiRequest('/admin/seats?diningHall=' + encodeURIComponent(diningHall));
  },

  async setAdminSeatStatus(seatNumber, status, note = '', diningHall = 'Central Mess') {
    return apiRequest('/admin/seats/status', {
      method: 'POST',
      body: JSON.stringify({ seatNumber, status, note, diningHall })
    });
  },

  async releaseAdminSeat(seatNumber, reason = 'Manager override', diningHall = 'Central Mess') {
    return apiRequest('/admin/seats/release', {
      method: 'POST',
      body: JSON.stringify({ seatNumber, reason, diningHall })
    });
  },

  async addAdminMenuItem(mealType, item, date = null) {
    return apiRequest('/admin/menu/item', {
      method: 'POST',
      body: JSON.stringify({ mealType, item, date })
    });
  },

  async updateAdminMenuItem(mealType, itemName, item, date = null) {
    return apiRequest('/admin/menu/item', {
      method: 'PUT',
      body: JSON.stringify({ mealType, itemName, item, date })
    });
  },

  async deleteAdminMenuItem(mealType, itemName, date = null) {
    return apiRequest('/admin/menu/item', {
      method: 'DELETE',
      body: JSON.stringify({ mealType, itemName, date })
    });
  }
};