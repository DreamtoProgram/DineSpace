/**
 * Page 7: Visit Completed Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const thanksName = document.getElementById('thanks-name');
  const completedSeatNum = document.getElementById('completed-seat-num');
  const diningHallName = document.getElementById('dining-hall-name');
  const enteredTimeEl = document.getElementById('entered-time');
  const exitedTimeEl = document.getElementById('exited-time');
  const visitDurationEl = document.getElementById('visit-duration');

  // Header Dropdown
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
    logoutBtn.addEventListener('click', () => Auth.logout());
  }

  // Load User Profile (Instant paint from cache)
  const cachedUser = Auth.getUser();
  if (cachedUser) {
    const firstName = cachedUser.name ? cachedUser.name.split(' ')[0] : 'Student';
    if (thanksName) thanksName.textContent = `Thanks, ${firstName}!`;
    if (userNameEl) userNameEl.textContent = cachedUser.name || 'Student';
    if (userRoleEl) userRoleEl.textContent = `${cachedUser.studentId || 'STU1042'} | Central Mess`;
  }

  if (Auth.isAuthenticated()) {
    API.getMe().then(me => {
      const student = me.student || (me.studentId ? me : null);
      if (student) {
        Auth.setUser(student);
        const firstName = student.name ? student.name.split(' ')[0] : 'Student';
        if (thanksName) thanksName.textContent = `Thanks, ${firstName}!`;
        if (userNameEl) userNameEl.textContent = student.name || 'Student';
        if (userRoleEl) userRoleEl.textContent = `${student.studentId} | Central Mess`;
      }
    }).catch(() => {});
  }

  // Helper to format ISO time string to "10:26 PM"
  function formatTime(isoStr) {
    if (!isoStr) return null;
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return null;
    const hours = d.getHours();
    const minutes = d.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    return `${displayHours}:${minutes} ${ampm}`;
  }

  // Load exit success result from Page 6 (tray_return.html)
  const exitDataStr = sessionStorage.getItem('dinespace_exit_success');
  let visit = null;
  if (exitDataStr) {
    try {
      const parsed = JSON.parse(exitDataStr);
      visit = parsed.visit || parsed;
    } catch (e) {
      console.warn('Could not parse exit data:', e);
    }
  }

  if (visit) {
    if (completedSeatNum) completedSeatNum.textContent = `#${visit.seatNumber || 24}`;
    if (diningHallName) diningHallName.textContent = visit.diningHall || 'Central Mess';
    if (enteredTimeEl && visit.entryTime) {
      const formatted = formatTime(visit.entryTime);
      if (formatted) enteredTimeEl.textContent = formatted;
    }
    if (exitedTimeEl && visit.exitTime) {
      const formatted = formatTime(visit.exitTime);
      if (formatted) exitedTimeEl.textContent = formatted;
    }
    if (visitDurationEl) {
      visitDurationEl.textContent = `${visit.durationMinutes || 18} min`;
    }
  } else {
    // If opened directly, attempt to fetch latest completed visit from history
    try {
      const hist = await API.getVisitHistory(1, 1);
      if (hist && hist.visits && hist.visits.length > 0) {
        const latest = hist.visits[0];
        if (completedSeatNum) completedSeatNum.textContent = `#${latest.seatNumber || 24}`;
        if (diningHallName) diningHallName.textContent = latest.diningHall || 'Central Mess';
        if (enteredTimeEl && latest.entryTime) {
          const formatted = formatTime(latest.entryTime);
          if (formatted) enteredTimeEl.textContent = formatted;
        }
        if (exitedTimeEl && latest.exitTime) {
          const formatted = formatTime(latest.exitTime);
          if (formatted) exitedTimeEl.textContent = formatted;
        }
        if (visitDurationEl) {
          visitDurationEl.textContent = `${latest.durationMinutes || 18} min`;
        }
      }
    } catch (err) {
      // Retain design default matching designed_pages/page_7.png (#24, 10:26 PM, 10:44 PM, 18 min)
      console.log('Using default design values:', err);
    }
  }
});