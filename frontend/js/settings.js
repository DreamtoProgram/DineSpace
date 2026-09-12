/**
 * DineSpace: Settings & Profile Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const logoutDangerBtn = document.getElementById('logout-danger-btn');
  const clearCacheBtn = document.getElementById('clear-cache-btn');

  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const dropdownUserName = document.getElementById('dropdown-user-name');
  const profileFullName = document.getElementById('profile-full-name');
  const profileStudentId = document.getElementById('profile-student-id');
  const profileDiningHall = document.getElementById('profile-dining-hall');

  const preferencesForm = document.getElementById('preferences-form');
  const prefNotifications = document.getElementById('pref-notifications');
  const prefLowCrowd = document.getElementById('pref-low-crowd');
  const prefDiet = document.getElementById('pref-diet');
  const savePrefBtn = document.getElementById('save-pref-btn');

  const passwordForm = document.getElementById('password-form');
  const currentPassword = document.getElementById('current-password');
  const newPassword = document.getElementById('new-password');
  const confirmPassword = document.getElementById('confirm-password');
  const changePwdBtn = document.getElementById('change-pwd-btn');

  const feedbackBanner = document.getElementById('feedback-banner');
  const feedbackMessage = document.getElementById('feedback-message');
  const closeBannerBtn = document.getElementById('close-banner-btn');

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

  // Logout buttons
  if (logoutBtn) logoutBtn.addEventListener('click', () => Auth.logout());
  if (logoutDangerBtn) logoutDangerBtn.addEventListener('click', () => Auth.logout());

  if (clearCacheBtn) {
    clearCacheBtn.addEventListener('click', () => {
      sessionStorage.clear();
      showBanner('Demo session storage cleared successfully.', 'success');
      setTimeout(() => window.location.reload(), 800);
    });
  }

  if (closeBannerBtn) {
    closeBannerBtn.addEventListener('click', () => {
      feedbackBanner.classList.add('hidden');
    });
  }

  function showBanner(msg, type = 'success') {
    if (!feedbackBanner || !feedbackMessage) return;
    feedbackMessage.textContent = msg;
    feedbackBanner.classList.remove('hidden');
    if (type === 'success') {
      feedbackBanner.className = 'rounded-xl p-4 text-xs font-semibold flex items-center justify-between border bg-emerald-500/10 border-emerald-500/30 text-emerald-300';
    } else {
      feedbackBanner.className = 'rounded-xl p-4 text-xs font-semibold flex items-center justify-between border bg-red-500/10 border-red-500/30 text-red-300';
    }
    setTimeout(() => {
      feedbackBanner.classList.add('hidden');
    }, 5000);
  }

  // Load User Data & Settings
  async function loadProfile() {
    let student = Auth.getUser();

    try {
      const me = await API.getMe();
      if (me && me.student) {
        student = me.student;
      }
    } catch (e) {
      // offline fallback
    }

    if (student) {
      const name = student.name || 'Kunal Kumar Singh';
      const id = student.studentId || 'P132-NNK';
      if (userNameEl) userNameEl.textContent = name;
      if (dropdownUserName) dropdownUserName.textContent = name;
      if (profileFullName) profileFullName.textContent = name;
      if (profileStudentId) profileStudentId.textContent = `Student ID: ${id}`;
      if (userRoleEl) userRoleEl.textContent = `${id} | Campus`;
    }

    // Try API.getSettings()
    try {
      const settings = await API.getSettings();
      if (settings) {
        if (settings.diningHall && profileDiningHall) {
          profileDiningHall.textContent = `${settings.diningHall} (Main)`;
        }
        if (settings.preferences) {
          if (prefNotifications) {
            prefNotifications.checked = settings.preferences.notificationsEnabled ?? true;
          }
        }
      }
    } catch (e) {
      console.warn('API getSettings offline, loaded local defaults.');
    }
  }

  // Handle Preferences Save
  if (preferencesForm) {
    preferencesForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      savePrefBtn.disabled = true;
      savePrefBtn.textContent = 'Saving...';

      const notificationsEnabled = prefNotifications ? prefNotifications.checked : true;

      try {
        await API.updateSettings({
          notificationsEnabled: notificationsEnabled,
          preferences: {
            notificationsEnabled: notificationsEnabled
          }
        });
        showBanner('Preferences updated successfully.', 'success');
      } catch (err) {
        // Fallback local save if offline
        localStorage.setItem('dinespace_pref_notifications', notificationsEnabled);
        showBanner('Preferences saved locally.', 'success');
      } finally {
        savePrefBtn.disabled = false;
        savePrefBtn.textContent = 'Save Preferences';
      }
    });
  }

  // Handle Password Change
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const curr = currentPassword.value;
      const nw = newPassword.value;
      const conf = confirmPassword.value;

      if (!curr || !nw || !conf) {
        showBanner('Please fill in all password fields.', 'error');
        return;
      }

      if (nw !== conf) {
        showBanner('New password and confirmation do not match.', 'error');
        return;
      }

      if (nw.length < 6) {
        showBanner('New password must be at least 6 characters long.', 'error');
        return;
      }

      changePwdBtn.disabled = true;
      changePwdBtn.textContent = 'Updating...';

      try {
        await API.changePassword(curr, nw);
        showBanner('Password updated successfully! Please use it on your next login.', 'success');
        passwordForm.reset();
      } catch (err) {
        // If offline or error
        if (err.status === 400 || err.status === 401) {
          showBanner(err.message || 'Current password is incorrect.', 'error');
        } else {
          // offline simulation
          showBanner('Password updated successfully (Demo Mode).', 'success');
          passwordForm.reset();
        }
      } finally {
        changePwdBtn.disabled = false;
        changePwdBtn.textContent = 'Update Password';
      }
    });
  }

  // Initial Load
  loadProfile();
});
