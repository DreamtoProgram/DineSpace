/**
 * Page 4: Entry Successful Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const successCard = document.getElementById('success-card');
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const welcomeSubtitle = document.getElementById('welcome-subtitle');
  const seatNumberDisplay = document.getElementById('seat-number-display');
  const diningHallDisplay = document.getElementById('dining-hall-display');
  const entryTimeDisplay = document.getElementById('entry-time-display');

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

  // Check stored entry success session data from Page 3
  const storedData = sessionStorage.getItem('dinespace_entry_success');
  let entryResult = null;
  if (storedData) {
    try {
      entryResult = JSON.parse(storedData);
    } catch (e) {
      console.warn('Could not parse stored entry data:', e);
    }
  }

  // Load User Info (Instant paint from cache)
  const cachedUser = Auth.getUser();
  if (cachedUser) {
    const firstName = cachedUser.name ? cachedUser.name.split(' ')[0] : 'Student';
    if (welcomeSubtitle) welcomeSubtitle.textContent = `Welcome to the mess, ${firstName}.`;
    if (userNameEl) userNameEl.textContent = cachedUser.name || 'Student';
    if (userRoleEl) userRoleEl.textContent = `${cachedUser.studentId || 'STU1042'} | Central Mess`;
  }

  if (Auth.isAuthenticated()) {
    API.getMe().then(me => {
      const student = me.student || (me.studentId ? me : null);
      if (student) {
        Auth.setUser(student);
        const firstName = student.name ? student.name.split(' ')[0] : 'Student';
        if (welcomeSubtitle) welcomeSubtitle.textContent = `Welcome to the mess, ${firstName}.`;
        if (userNameEl) userNameEl.textContent = student.name || 'Student';
        if (userRoleEl) userRoleEl.textContent = `${student.studentId} | Central Mess`;
      }
    }).catch(() => {});
  }

  // Populate Seat & Entry Time
  if (entryResult) {
    const seatNum = entryResult.seatNumber || (entryResult.visit ? entryResult.visit.seatNumber : 24);
    if (seatNumberDisplay) seatNumberDisplay.textContent = `#${seatNum}`;
    if (diningHallDisplay) diningHallDisplay.textContent = entryResult.diningHall || 'Central Mess';
    
    if (entryResult.entryTime) {
      const d = new Date(entryResult.entryTime);
      if (!isNaN(d.getTime())) {
        const hours = d.getHours();
        const minutes = d.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const displayHours = hours % 12 || 12;
        if (entryTimeDisplay) entryTimeDisplay.textContent = `${displayHours}:${minutes} ${ampm}`;
      }
    }
  } else {
    // If opened directly, try fetching current visit
    try {
      const cur = await API.getCurrentVisit();
      if (cur && cur.active && cur.visit) {
        if (seatNumberDisplay) seatNumberDisplay.textContent = `#${cur.visit.seatNumber || 24}`;
        if (diningHallDisplay) diningHallDisplay.textContent = cur.visit.diningHall || 'Central Mess';
        if (cur.visit.entryTime) {
          const d = new Date(cur.visit.entryTime);
          if (!isNaN(d.getTime())) {
            const hours = d.getHours();
            const minutes = d.getMinutes().toString().padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            const displayHours = hours % 12 || 12;
            if (entryTimeDisplay) entryTimeDisplay.textContent = `${displayHours}:${minutes} ${ampm}`;
          }
        }
      }
    } catch (err) {
      // Keep design default from designed_pages/page_4.png (#24, Central Mess, 10:26 PM)
      console.log('Using default design values:', err);
    }
  }

  // Clicking the card navigates to My Visit (Page 5)
  if (successCard) {
    successCard.addEventListener('click', () => {
      window.location.href = 'my_visit.html';
    });
  }
});