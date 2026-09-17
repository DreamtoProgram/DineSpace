/**
 * Page 2: Home Dashboard Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Elements
  const greetingText = document.getElementById('greeting-text');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');

  const crowdPercentEl = document.getElementById('crowd-percent');
  const gaugeCircle = document.getElementById('gauge-circle');
  const crowdLevelBadge = document.getElementById('crowd-level-badge');
  const crowdSubtitle = document.getElementById('crowd-subtitle');
  const seatsAvailableEl = document.getElementById('seats-available');
  const seatsOccupiedEl = document.getElementById('seats-occupied');
  const updatedAtText = document.getElementById('updated-at-text');
  const refreshStatusBtn = document.getElementById('refresh-status-btn');

  const visitEmptyState = document.getElementById('visit-empty-state');
  const visitActiveState = document.getElementById('visit-active-state');
  const activeSeatNumber = document.getElementById('active-seat-number');
  const activeDuration = document.getElementById('active-duration');

  // Gauge circumference for r=52: 2 * PI * 52 = 326.73
  const CIRCUMFERENCE = 326.73;

  // Event Listeners attached immediately
  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', () => {
      userDropdown.classList.add('hidden');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      Auth.logout();
    });
  }

  // Helper: Greeting by hour
  function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  // Helper: Time Formatter
  function formatTime(date) {
    let hours = date.getHours();
    let minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const strMinutes = minutes < 10 ? '0' + minutes : minutes;
    return `${hours}:${strMinutes} ${ampm}`;
  }

  function getDefaultStatus() {
    return {
      occupancyRate: 42,
      occupancyCount: 42,
      availableSeats: 58,
      crowdLevel: 'Low'
    };
  }

  function renderUserProfile(student) {
    if (!student) return;
    const firstName = student.name ? student.name.split(' ')[0] : 'Student';
    const greeting = getGreeting();
    if (greetingText) greetingText.textContent = `${greeting}, ${firstName}`;
    if (userNameEl) userNameEl.textContent = student.name || 'Student';
    if (userRoleEl) userRoleEl.textContent = `${student.studentId || 'STU1042'} | Central Mess`;
  }

  function renderStatusUI(status) {
    if (!status) return;
    const rate = status.occupancyRate ?? status.occupancyPercentage ?? 42;
    const occupied = status.occupancyCount ?? status.occupiedSeats ?? 42;
    const available = status.availableSeats ?? Math.max(0, 100 - occupied);
    const level = status.crowdLevel || (rate > 80 ? 'Peak Rush' : (rate >= 50 ? 'Moderate' : 'Low'));

    if (crowdPercentEl) crowdPercentEl.textContent = `${rate}%`;
    if (gaugeCircle) {
      const offset = CIRCUMFERENCE - (rate / 100) * CIRCUMFERENCE;
      gaugeCircle.style.strokeDashoffset = offset;
    }

    if (seatsAvailableEl) seatsAvailableEl.textContent = available;
    if (seatsOccupiedEl) seatsOccupiedEl.textContent = occupied;

    if (crowdLevelBadge && crowdSubtitle) {
      if (level === 'Low') {
        crowdLevelBadge.textContent = 'Low Crowd';
        crowdLevelBadge.className = 'text-base font-bold text-emerald-400';
        crowdSubtitle.textContent = 'Plenty of seats available, ideal time to dine!';
      } else if (level === 'Peak Rush' || level === 'High') {
        crowdLevelBadge.textContent = 'Peak Rush';
        crowdLevelBadge.className = 'text-base font-bold text-red-400';
        crowdSubtitle.textContent = 'Heavy rush! Expect brief waiting at entrance.';
      } else {
        crowdLevelBadge.textContent = 'Moderate Crowd';
        crowdLevelBadge.className = 'text-base font-bold text-[#FFA048]';
        crowdSubtitle.textContent = "Some rush, but you'll find a seat!";
      }
    }

    if (updatedAtText) {
      updatedAtText.textContent = `Updated ${formatTime(new Date())}`;
    }
  }

  // 1. Instant Paint: Render local state immediately (0ms visual latency)
  const cachedUser = Auth.getUser();
  if (cachedUser) {
    renderUserProfile(cachedUser);
  } else if (!Auth.isAuthenticated() && !window.location.protocol.startsWith('file')) {
    window.location.href = 'login.html';
    return;
  }

  const cachedStatusStr = localStorage.getItem('dinespace_cached_status');
  if (cachedStatusStr) {
    try {
      renderStatusUI(JSON.parse(cachedStatusStr));
    } catch (e) {
      renderStatusUI(getDefaultStatus());
    }
  } else {
    renderStatusUI(getDefaultStatus());
  }

  // 2. Fetchers for Parallel Synchronization
  async function fetchUserProfile() {
    if (!Auth.isAuthenticated()) return;
    try {
      const me = await API.getMe();
      const student = me.student || (me.studentId ? me : null);
      if (student) {
        Auth.setUser(student);
        renderUserProfile(student);
      }
    } catch (e) {
      // Keep cached profile, never disrupt user session
    }
  }

  async function updateStatus() {
    try {
      const status = await API.getStatus();
      if (status) {
        localStorage.setItem('dinespace_cached_status', JSON.stringify(status));
        renderStatusUI(status);
      }
    } catch (err) {
      // Keep existing render or fallback
    }
  }

  async function checkActiveVisit() {
    if (!Auth.isAuthenticated()) return;
    try {
      const res = await API.getCurrentVisit();
      if (res && (res.hasActiveVisit || res.active) && res.visit) {
        if (visitEmptyState) visitEmptyState.classList.add('hidden');
        if (visitActiveState) visitActiveState.classList.remove('hidden');
        if (activeSeatNumber) activeSeatNumber.textContent = `#${res.visit.seatNumber}`;
        const mins = res.visit.elapsedMinutes ?? res.visit.durationMinutes ?? 0;
        if (activeDuration) activeDuration.textContent = `${mins.toString().padStart(2, '0')} min`;
      } else {
        if (visitEmptyState) visitEmptyState.classList.remove('hidden');
        if (visitActiveState) visitActiveState.classList.add('hidden');
      }
    } catch (e) {
      if (visitEmptyState) visitEmptyState.classList.remove('hidden');
      if (visitActiveState) visitActiveState.classList.add('hidden');
    }
  }

  // Refresh button click
  if (refreshStatusBtn) {
    refreshStatusBtn.addEventListener('click', () => {
      refreshStatusBtn.classList.add('animate-spin');
      updateStatus().finally(() => {
        setTimeout(() => refreshStatusBtn.classList.remove('animate-spin'), 600);
      });
    });
  }

  // 3. Parallel Background Initial Fetch
  Promise.allSettled([
    fetchUserProfile(),
    updateStatus(),
    checkActiveVisit()
  ]);

  // Periodic Background Polling
  setInterval(updateStatus, 5000);
  setInterval(checkActiveVisit, 12000);
});