/**
 * DineSpace Real-Time WebSockets & Server-Sent Events (SSE) Client
 * Provides instant bi-directional updates with zero-delay fallback
 */
(function (global) {
  'use strict';

  const subscribers = new Set();
  let socket = null;
  let eventSource = null;
  let isConnected = false;
  let reconnectTimer = null;
  let reconnectAttempts = 0;
  let lastEventData = null;

  function getBaseUrls() {
    let wsHost = '127.0.0.1:8000';
    let isHttps = false;

    if (typeof window !== 'undefined' && window.location) {
      isHttps = window.location.protocol === 'https:';
      if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        if (window.location.port === '8000' || window.location.port === '') {
          wsHost = window.location.host;
        } else {
          wsHost = window.location.hostname + ':8000';
        }
      } else {
        wsHost = window.location.host;
      }
    }

    const wsProto = isHttps ? 'wss://' : 'ws://';
    const httpProto = isHttps ? 'https://' : 'http://';

    return {
      ws: `${wsProto}${wsHost}/api/ws/occupancy`,
      sse: `${httpProto}${wsHost}/api/sse/occupancy`
    };
  }

  function notifySubscribers(payload) {
    if (!payload) return;
    lastEventData = payload;

    // Notify registered JS callbacks
    subscribers.forEach(cb => {
      try {
        cb(payload);
      } catch (err) {
        console.error('Realtime subscriber error:', err);
      }
    });

    // Default DOM integrations across pages
    applyRealtimeUpdateToDOM(payload);
  }

  function applyRealtimeUpdateToDOM(payload) {
    if (!payload || payload.event !== 'occupancy_update') return;
    const occ = payload.occupancy;
    if (!occ) return;

    // --- 1. Home Page Donut Ring & Crowd Badge ---
    const pctEl = document.getElementById('crowd-percent') || document.getElementById('occupancy-percentage');
    const occSeatsEl = document.getElementById('seats-occupied') || document.getElementById('occupied-seats-text');
    const availSeatsEl = document.getElementById('seats-available') || document.getElementById('available-seats-text');
    const crowdBadgeEl = document.getElementById('crowd-level-badge') || document.getElementById('crowd-badge');
    const progressCircle = document.getElementById('gauge-circle') || document.getElementById('occupancy-progress-circle');
    const updatedAtEl = document.getElementById('updated-at-text');

    const rate = occ.occupancyRate ?? occ.occupancyPercentage ?? 0;
    const occupied = occ.occupancyCount ?? occ.occupiedSeats ?? 0;
    const available = occ.availableSeats ?? Math.max(0, 100 - occupied);

    if (pctEl) pctEl.textContent = rate + '%';
    if (occSeatsEl) occSeatsEl.textContent = occSeatsEl.id === 'seats-occupied' ? occupied : occupied + ' Occupied';
    if (availSeatsEl) availSeatsEl.textContent = availSeatsEl.id === 'seats-available' ? available : available + ' Available';

    if (crowdBadgeEl) {
      const level = occ.crowdLevel || (rate > 80 ? 'Peak Rush' : (rate >= 50 ? 'Moderate' : 'Low'));
      if (crowdBadgeEl.id === 'crowd-level-badge') {
        if (level === 'Low') {
          crowdBadgeEl.textContent = 'Low Crowd';
          crowdBadgeEl.className = 'text-base font-bold text-emerald-400';
        } else if (level === 'Peak Rush' || level === 'High' || level === 'Peak') {
          crowdBadgeEl.textContent = 'Peak Rush';
          crowdBadgeEl.className = 'text-base font-bold text-red-400';
        } else {
          crowdBadgeEl.textContent = 'Moderate Crowd';
          crowdBadgeEl.className = 'text-base font-bold text-[#FFA048]';
        }
      } else {
        crowdBadgeEl.textContent = level;
        if (level === 'Low') {
          crowdBadgeEl.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
        } else if (level === 'Peak Rush' || level === 'Peak') {
          crowdBadgeEl.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20';
        } else {
          crowdBadgeEl.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-orange-500/10 text-orange-400 border border-orange-500/20';
        }
      }
    }

    if (progressCircle) {
      const radius = progressCircle.r ? progressCircle.r.baseVal.value : 52;
      const circumference = 2 * Math.PI * radius;
      const offset = circumference - (rate / 100) * circumference;
      progressCircle.style.strokeDashoffset = offset;
    }

    if (updatedAtEl) {
      const d = new Date();
      updatedAtEl.textContent = 'Updated ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // --- 2. Seats Page Real-Time Flipping ---
    if (payload.seatNumber) {
      const seatTile = document.querySelector(`[data-seat-number="${payload.seatNumber}"], [data-seat="${payload.seatNumber}"]`);
      if (seatTile) {
        seatTile.classList.remove('seat-available', 'seat-occupied', 'seat-maintenance', 'seat-reserved');
        if (payload.seatStatus === 'occupied') seatTile.classList.add('seat-occupied');
        else if (payload.seatStatus === 'maintenance') seatTile.classList.add('seat-maintenance');
        else if (payload.seatStatus === 'reserved') seatTile.classList.add('seat-reserved');
        else seatTile.classList.add('seat-available');
      }
    }

    // --- 3. Live Indicator Pill (if present on page) ---
    const liveIndicator = document.getElementById('live-stream-status');
    if (liveIndicator) {
      liveIndicator.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Real-Time Stream Active</span>
      `;
      liveIndicator.className = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-[10px] font-semibold tracking-wide';
    }
  }

  // --- WebSocket Connection ---
  function connectWebSocket() {
    const urls = getBaseUrls();
    try {
      socket = new WebSocket(urls.ws);

      socket.onopen = () => {
        isConnected = true;
        reconnectAttempts = 0;
        logger('WebSocket connection established to', urls.ws);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          notifySubscribers(data);
        } catch (e) {
          logger('Invalid WebSocket payload:', event.data);
        }
      };

      socket.onerror = () => {
        logger('WebSocket error, falling back to SSE');
        socket.close();
      };

      socket.onclose = () => {
        isConnected = false;
        // Fallback to SSE if WebSockets not supported or failed
        if (reconnectAttempts < 2) {
          reconnectAttempts++;
          connectSSE();
        } else {
          scheduleReconnect();
        }
      };
    } catch (err) {
      logger('WebSocket constructor error, falling back to SSE:', err);
      connectSSE();
    }
  }

  // --- SSE Fallback Connection ---
  function connectSSE() {
    if (typeof EventSource === 'undefined') return;
    const urls = getBaseUrls();

    try {
      if (eventSource) eventSource.close();
      eventSource = new EventSource(urls.sse);

      eventSource.onopen = () => {
        isConnected = true;
        reconnectAttempts = 0;
        logger('SSE connection established to', urls.sse);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          notifySubscribers(data);
        } catch (e) {
          logger('Invalid SSE payload:', event.data);
        }
      };

      eventSource.onerror = () => {
        logger('SSE connection error');
        eventSource.close();
        scheduleReconnect();
      };
    } catch (err) {
      logger('SSE constructor error:', err);
      scheduleReconnect();
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    const delay = Math.min(30000, 2000 * Math.pow(1.5, reconnectAttempts));
    reconnectTimer = setTimeout(() => {
      logger('Attempting real-time reconnect...');
      connectWebSocket();
    }, delay);
  }

  function logger(...args) {
    // Silent in production or debug mode
    if (window.DINESPACE_DEBUG) {
      console.log('[DineSpace Realtime]', ...args);
    }
  }

  // Public Interface
  const DineSpaceRealtime = {
    subscribe(callback) {
      if (typeof callback === 'function') {
        subscribers.add(callback);
        if (lastEventData) callback(lastEventData);
      }
    },
    unsubscribe(callback) {
      subscribers.delete(callback);
    },
    isConnected() {
      return isConnected;
    },
    getLastEvent() {
      return lastEventData;
    },
    init() {
      connectWebSocket();
    }
  };

  global.DineSpaceRealtime = DineSpaceRealtime;

  // Auto-start on DOMContentLoaded
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => DineSpaceRealtime.init());
    } else {
      DineSpaceRealtime.init();
    }
  }

})(typeof window !== 'undefined' ? window : this);
