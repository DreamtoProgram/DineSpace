/**
 * DineSpace — Notifications Controller
 * Handles category filtering, mark-as-read actions, live search, and dynamic API sync.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Auth check (allow file preview)
  if (!Auth.isAuthenticated() && !window.location.protocol.startsWith('file')) {
    window.location.href = 'login.html';
    return;
  }

  // 2. Setup user profile & dropdown
  setupProfile();

  // 3. Setup Category Filter Pills
  setupCategoryTabs();

  // 4. Setup "Mark all as read"
  setupMarkAllRead();

  // 5. Setup Live Search
  setupLiveSearch();

  // 6. Setup Individual Card Interactions
  setupCardClicks();

  // 7. Try fetching notifications from API
  await syncNotifications();
});

/**
 * Configure user profile pill and logout listener
 */
async function setupProfile() {
  try {
    const student = await API.getMe();
    if (student) {
      const displayName = student.fullName || student.name || 'Kunal Kumar Singh';
      const studentId = student.studentId || 'P132-NNK';
      const dept = student.department || 'CSE';

      const userNameEl = document.getElementById('user-name');
      const userRegEl = document.getElementById('user-reg');
      const dropNameEl = document.getElementById('dropdown-full-name');
      const dropIdEl = document.getElementById('dropdown-student-id');

      if (userNameEl) userNameEl.textContent = displayName;
      if (userRegEl) userRegEl.textContent = `${studentId} | ${dept}`;
      if (dropNameEl) dropNameEl.textContent = displayName;
      if (dropIdEl) dropIdEl.textContent = studentId;
    }
  } catch (err) {
    console.warn('Using demo student profile:', err);
  }

  // Dropdown toggle
  const profileBtn = document.getElementById('profile-dropdown-btn');
  const profileMenu = document.getElementById('profile-dropdown-menu');
  if (profileBtn && profileMenu) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle('show');
    });
  }

  // Logout action
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      API.logout();
      window.location.href = 'login.html';
    });
  }

  document.addEventListener('click', () => {
    if (profileMenu) profileMenu.classList.remove('show');
  });
}

/**
 * Configure Category Filter Tabs (All, Menu Updates, Crowd Alerts, Visit Updates, System)
 */
function setupCategoryTabs() {
  const tabs = document.querySelectorAll('.tab-pill');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.className = 'tab-pill tab-pill-inactive';
      });
      tab.className = 'tab-pill tab-pill-active';

      const filter = tab.getAttribute('data-filter');
      filterByCategory(filter);
    });
  });
}

/**
 * Filter notification cards by category and show/hide empty date groups
 */
function filterByCategory(category) {
  const cards = document.querySelectorAll('.notif-card');
  cards.forEach(card => {
    const cardCat = card.getAttribute('data-category');
    if (category === 'all' || cardCat === category) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });

  // Check each date group to hide headers if all children are hidden
  const groups = document.querySelectorAll('.notif-group');
  groups.forEach(group => {
    const visibleCards = group.querySelectorAll('.notif-card:not([style*="display: none"])');
    if (visibleCards.length === 0) {
      group.style.display = 'none';
    } else {
      group.style.display = '';
    }
  });
}

/**
 * Setup "Mark all as read" button handler
 */
function setupMarkAllRead() {
  const markAllBtn = document.getElementById('btn-mark-all');
  if (!markAllBtn) return;

  markAllBtn.addEventListener('click', async () => {
    // 1. Visual update: clear all dots
    const dots = document.querySelectorAll('.notif-unread-dot');
    dots.forEach(dot => dot.remove());

    // 2. Clear header bell dot & sidebar dot
    const headerDot = document.getElementById('header-bell-dot');
    if (headerDot) headerDot.remove();
    const sidebarDot = document.getElementById('sidebar-notif-dot');
    if (sidebarDot) sidebarDot.remove();

    // 3. Update button text temporarily
    const btnText = markAllBtn.querySelector('span');
    if (btnText) {
      btnText.textContent = 'All read';
      setTimeout(() => {
        btnText.textContent = 'Mark all as read';
      }, 2500);
    }

    // 4. Sync with backend API
    try {
      await API.markAllNotificationsRead();
    } catch (err) {
      console.warn('API read-all synced locally:', err);
    }
  });
}

/**
 * Setup Live Search
 */
function setupLiveSearch() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.notif-card');

    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      if (!q || text.includes(q)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });

    // Check date group headers
    const groups = document.querySelectorAll('.notif-group');
    groups.forEach(group => {
      const visible = group.querySelectorAll('.notif-card:not([style*="display: none"])');
      group.style.display = visible.length === 0 ? 'none' : '';
    });
  });
}

/**
 * Setup individual notification card click interactions
 */
function setupCardClicks() {
  const cards = document.querySelectorAll('.notif-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      // Remove individual unread dot on click
      const dot = card.querySelector('.notif-unread-dot');
      if (dot) dot.remove();

      // Check remaining unread count
      const remainingDots = document.querySelectorAll('.notif-unread-dot');
      if (remainingDots.length === 0) {
        const headerDot = document.getElementById('header-bell-dot');
        if (headerDot) headerDot.remove();
        const sidebarDot = document.getElementById('sidebar-notif-dot');
        if (sidebarDot) sidebarDot.remove();
      }
    });
  });
}

/**
 * Try syncing notifications with the backend
 */
async function syncNotifications() {
  try {
    const response = await API.getNotifications('all');
    if (response && response.notifications && response.notifications.length > 0) {
      console.log('Synced notifications from API:', response.notifications.length);
    }
  } catch (err) {
    console.warn('Using baseline reference notifications for visual fidelity:', err);
  }
}
