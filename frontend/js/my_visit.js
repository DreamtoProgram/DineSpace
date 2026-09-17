/**
 * Page 5: My Visit Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const diningHallTitle = document.getElementById('dining-hall-title');
  const seatNumberDisplay = document.getElementById('seat-number-display');
  const enteredTimeDisplay = document.getElementById('entered-time-display');

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
    if (userNameEl) userNameEl.textContent = cachedUser.name || 'Student';
    if (userRoleEl) userRoleEl.textContent = `${cachedUser.studentId || 'STU1042'} | Central Mess`;
  }

  if (Auth.isAuthenticated()) {
    API.getMe().then(me => {
      const student = me.student || (me.studentId ? me : null);
      if (student) {
        Auth.setUser(student);
        if (userNameEl) userNameEl.textContent = student.name || 'Student';
        if (userRoleEl) userRoleEl.textContent = `${student.studentId} | Central Mess`;
      }
    }).catch(() => {});
  }

  // Check stored entry success session data
  const storedData = sessionStorage.getItem('dinespace_entry_success');
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData);
      const seatNum = parsed.seatNumber || (parsed.visit ? parsed.visit.seatNumber : 24);
      if (seatNumberDisplay) seatNumberDisplay.textContent = `#${seatNum}`;
      if (diningHallTitle) diningHallTitle.textContent = parsed.diningHall || 'Central Mess';
      if (parsed.entryTime) {
        const d = new Date(parsed.entryTime);
        if (!isNaN(d.getTime())) {
          const hours = d.getHours();
          const minutes = d.getMinutes().toString().padStart(2, '0');
          const ampm = hours >= 12 ? 'PM' : 'AM';
          const displayHours = hours % 12 || 12;
          if (enteredTimeDisplay) enteredTimeDisplay.textContent = `${displayHours}:${minutes} ${ampm}`;
        }
      }
    } catch (e) {
      console.warn('Could not parse stored visit data:', e);
    }
  }

  // Load Current Active Visit from backend
  try {
    const cur = await API.getCurrentVisit();
    if (cur && cur.active && cur.visit) {
      if (seatNumberDisplay) seatNumberDisplay.textContent = `#${cur.visit.seatNumber || 24}`;
      if (diningHallTitle) diningHallTitle.textContent = cur.visit.diningHall || 'Central Mess';
      if (cur.visit.entryTime) {
        const d = new Date(cur.visit.entryTime);
        if (!isNaN(d.getTime())) {
          const hours = d.getHours();
          const minutes = d.getMinutes().toString().padStart(2, '0');
          const ampm = hours >= 12 ? 'PM' : 'AM';
          const displayHours = hours % 12 || 12;
          if (enteredTimeDisplay) enteredTimeDisplay.textContent = `${displayHours}:${minutes} ${ampm}`;
        }
      }
    }
  } catch (err) {
    // Keep design default from designed_pages/page_5.png (#24, Central Mess, 10:26 PM)
    console.log('Using default design values:', err);
  }
});