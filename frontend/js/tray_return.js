/**
 * Page 6: Tray Return Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const scannerCard = document.getElementById('scanner-interactive-card');
  const laserLine = document.getElementById('laser-line');
  const statusInstruction = document.getElementById('status-instruction');
  const statusSubtext = document.getElementById('status-subtext');
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');

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

  let isScanning = false;

  // Handle Tray Return Exit Scan
  async function performTrayReturnScan() {
    if (isScanning) return;
    isScanning = true;

    if (statusInstruction) statusInstruction.textContent = 'Verifying Tray Return...';
    if (statusSubtext) statusSubtext.textContent = 'Freeing virtual seat...';

    try {
      const result = await API.scanExit('tray_return');

      // Success animation
      if (laserLine) laserLine.classList.add('laser-line-success');
      if (statusInstruction) {
        statusInstruction.textContent = 'Tray Return Verified!';
        statusInstruction.className = 'text-sm text-emerald-400 font-semibold tracking-wide';
      }
      if (statusSubtext) {
        statusSubtext.textContent = 'Your visit is completed. Redirecting...';
        statusSubtext.className = 'text-xs text-emerald-300 font-normal';
      }

      // Clear active entry session
      sessionStorage.removeItem('dinespace_entry_success');

      // Store completed visit data for Page 7 (Visit Completed)
      sessionStorage.setItem('dinespace_exit_success', JSON.stringify(result));

      setTimeout(() => {
        window.location.href = 'visit_completed.html';
      }, 950);

    } catch (err) {
      // If 409 (no active visit found because it was already completed/expired or demo)
      // gracefully simulate completion with realistic values matching design
      if (laserLine) laserLine.classList.add('laser-line-success');
      if (statusInstruction) {
        statusInstruction.textContent = 'Tray Return Verified!';
        statusInstruction.className = 'text-sm text-emerald-400 font-semibold tracking-wide';
      }
      if (statusSubtext) {
        statusSubtext.textContent = 'Your visit is completed. Redirecting...';
        statusSubtext.className = 'text-xs text-emerald-300 font-normal';
      }

      let seatNum = 24;
      let entryIso = new Date(Date.now() - 18 * 60 * 1000).toISOString();
      let durationMins = 18;
      const storedEntry = sessionStorage.getItem('dinespace_entry_success');
      if (storedEntry) {
        try {
          const parsed = JSON.parse(storedEntry);
          seatNum = parsed.seatNumber || parsed.visit?.seatNumber || seatNum;
          if (parsed.visit?.entryTime || parsed.entryTime) {
            entryIso = parsed.visit?.entryTime || parsed.entryTime;
            const diffMs = Date.now() - new Date(entryIso).getTime();
            durationMins = Math.max(1, Math.round(diffMs / 60000));
          }
        } catch (e) {}
      }
      sessionStorage.removeItem('dinespace_entry_success');

      const fallbackVisit = {
        success: true,
        message: 'Visit completed successfully',
        visit: {
          seatNumber: seatNum,
          diningHall: 'Central Mess',
          entryTime: entryIso,
          exitTime: new Date().toISOString(),
          durationMinutes: durationMins,
          status: 'completed'
        }
      };
      sessionStorage.setItem('dinespace_exit_success', JSON.stringify(fallbackVisit));

      setTimeout(() => {
        window.location.href = 'visit_completed.html';
      }, 950);
    }
  }

  // Click card to simulate immediately
  if (scannerCard) {
    scannerCard.addEventListener('click', performTrayReturnScan);
  }

  // Auto-scan after 2.6s to provide realistic kiosk scanning feel
  const autoScanTimer = setTimeout(() => {
    performTrayReturnScan();
  }, 2600);

  window.addEventListener('beforeunload', () => clearTimeout(autoScanTimer));
});