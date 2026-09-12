import os

os.makedirs("../frontend/js", exist_ok=True)

# 1. Create frontend/entry_success.html
success_html = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DineSpace — Entry Successful!</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@1,500;1,600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              orange: '#FF5E1E',
              orangeHover: '#EA4C10',
              orangeGlow: 'rgba(255, 94, 30, 0.35)',
              darkBg: '#070B11',
              darkSidebar: '#0A0F18',
              darkCard: '#0D1522',
              darkBorder: 'rgba(255, 255, 255, 0.07)',
              textMuted: '#8B9BB4'
            }
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            serifQuote: ['"Playfair Display"', 'serif']
          }
        }
      }
    }
  </script>
  <link rel="stylesheet" href="css/style.css" />
  <style>
    /* Outer glowing card matching designed_pages/page_4.png */
    .success-outer-card {
      width: 550px;
      height: 500px;
      background: rgba(13, 19, 28, 0.88);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 94, 30, 0.32);
      box-shadow: 0 0 60px -6px rgba(255, 94, 30, 0.22), inset 0 0 25px -10px rgba(255, 94, 30, 0.05);
      border-radius: 32px;
      transition: all 0.3s ease;
    }

    .success-outer-card:hover {
      box-shadow: 0 0 75px -4px rgba(255, 94, 30, 0.28), inset 0 0 30px -8px rgba(255, 94, 30, 0.08);
    }

    /* Green checkmark glowing circle */
    .green-glow-circle {
      width: 104px;
      height: 104px;
      border-radius: 9999px;
      background: rgba(8, 26, 16, 0.85);
      border: 1.5px solid #22C55E;
      box-shadow: 0 0 28px rgba(34, 197, 94, 0.42), inset 0 0 16px rgba(34, 197, 94, 0.15);
    }

    /* Inner seat number card */
    .seat-number-card {
      width: 440px;
      height: 140px;
      background: rgba(22, 16, 17, 0.55);
      border: 1px solid rgba(255, 94, 30, 0.28);
      box-shadow: inset 0 0 20px -8px rgba(255, 94, 30, 0.08);
      border-radius: 24px;
    }
  </style>
</head>
<body class="bg-[#070B11] text-white min-h-screen flex overflow-x-hidden selection:bg-[#FF5E1E] selection:text-white">

  <!-- ========================================================================= -->
  <!-- LEFT SIDEBAR                                                              -->
  <!-- ========================================================================= -->
  <aside class="w-[292px] flex-shrink-0 bg-[#0A0F18] border-r border-white/5 flex flex-col justify-between p-6 min-h-screen z-20">
    
    <!-- Top Brand & Navigation -->
    <div class="space-y-8">
      
      <!-- DineSpace Brand Logo -->
      <a href="home.html" class="flex items-center gap-3.5 px-2 group">
        <div class="w-11 h-11 rounded-xl overflow-hidden shadow-inner flex items-center justify-center flex-shrink-0 bg-[#221511] border border-orange-500/20">
          <img src="assets/images/login_badge.png" alt="DineSpace" class="w-full h-full object-cover" />
        </div>
        <div class="flex flex-col">
          <div class="flex items-baseline tracking-tight">
            <span class="text-xl font-bold text-white">Dine</span>
            <span class="text-xl font-bold text-[#FF5E1E]">Space</span>
          </div>
          <span class="text-[11px] text-[#8B9BB4] tracking-wide font-medium -mt-1">Find your seat. Enjoy your meal.</span>
        </div>
      </a>

      <!-- Navigation Menu -->
      <nav class="space-y-2 pt-2">
        
        <!-- Home -->
        <a href="home.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          <span>Home</span>
        </a>

        <!-- Find a Seat -->
        <a href="seats.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 19v2m12-2v2M5 14h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v5a2 2 0 002 2zm0 0v5h14v-5"></path>
          </svg>
          <span>Find a Seat</span>
        </a>

        <!-- Menu -->
        <a href="menu.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v2m-8 12h16a1 1 0 001-1 9 9 0 00-18 0 1 1 0 001 1zM4 18h16"></path>
          </svg>
          <span>Menu</span>
        </a>

        <!-- My Visit -->
        <a href="my_visit.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="4" y="4" width="16" height="16" rx="2" stroke-width="2"></rect>
            <line x1="8" y1="9" x2="16" y2="9" stroke-width="2" stroke-linecap="round"></line>
            <line x1="8" y1="13" x2="13" y2="13" stroke-width="2" stroke-linecap="round"></line>
          </svg>
          <span>My Visit</span>
        </a>

        <!-- Visit History -->
        <a href="visit_history.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
            <polyline points="12 6 12 12 16 14" stroke-width="2" stroke-linecap="round"></polyline>
          </svg>
          <span>Visit History</span>
        </a>

        <!-- Section Divider -->
        <div class="pt-4 pb-2">
          <div class="border-t border-white/5"></div>
        </div>

        <!-- Notifications -->
        <a href="notifications.html" class="flex items-center justify-between px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <div class="flex items-center gap-4">
            <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
            </svg>
            <span>Notifications</span>
          </div>
          <span class="w-2.5 h-2.5 rounded-full bg-[#FF5E1E]"></span>
        </a>

        <!-- Settings -->
        <a href="settings.html" class="flex items-center gap-4 px-4 py-3 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="3" stroke-width="2"></circle>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"></path>
          </svg>
          <span>Settings</span>
        </a>

      </nav>
    </div>

    <!-- Lower Sidebar Footer -->
    <div class="px-2 pt-6 space-y-4">
      <div>
        <div class="w-7 h-[3px] bg-[#FF5E1E] mb-3 rounded-full"></div>
        <p class="font-serif-quote italic text-lg text-gray-200 tracking-wide leading-snug">
          “Good Food<br>Brighter Days”
        </p>
      </div>

      <div class="w-16 h-16 opacity-85">
        <img src="assets/images/leaf_illustration.png" alt="Leaf" class="w-full h-full object-contain filter drop-shadow-sm" />
      </div>

      <div class="text-xs text-[#5A6A85] leading-relaxed">
        Eat Well. Do More.<br>At Campus.
      </div>
    </div>

  </aside>

  <!-- ========================================================================= -->
  <!-- MAIN CONTENT AREA                                                         -->
  <!-- ========================================================================= -->
  <main class="flex-1 flex flex-col min-h-screen overflow-y-auto">
    
    <!-- Top Header Bar (Matching designed_pages/page_4.png: clean left, bell + divider + profile on right) -->
    <header class="h-[84px] border-b border-white/5 px-10 flex items-center justify-end bg-[#070B11]/90 backdrop-blur-md sticky top-0 z-30">
      
      <!-- Right Header Actions -->
      <div class="flex items-center gap-5">
        
        <!-- Notification Bell -->
        <a href="notifications.html" class="relative p-2 rounded-xl text-gray-300 hover:text-white hover:bg-white/5 transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <span class="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-[#FF5E1E]"></span>
        </a>

        <!-- Subtle vertical divider between bell and profile -->
        <div class="w-[1px] h-6 bg-white/10 mx-1"></div>

        <!-- User Profile Pill -->
        <div class="relative">
          <button id="user-menu-btn" class="flex items-center gap-3 p-1.5 pr-2.5 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
            <img id="user-avatar" src="assets/images/user_avatar.png" alt="Avatar" class="w-9 h-9 rounded-full object-cover border border-white/10" />
            <div class="text-left hidden sm:block">
              <div id="user-name" class="text-xs font-semibold text-white">Kunal Kumar Singh</div>
              <div id="user-role" class="text-[10px] text-[#8B9BB4]">P132-NNK | CSE</div>
            </div>
            <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <polyline points="6 9 12 15 18 9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <div id="user-dropdown" class="hidden absolute right-0 mt-2 w-48 rounded-xl bg-[#0E1726] border border-white/10 shadow-2xl py-2 z-50 text-xs">
            <a href="settings.html" class="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/5">Settings & Profile</a>
            <div class="border-t border-white/5 my-1"></div>
            <button id="logout-btn" class="w-full text-left px-4 py-2 text-red-400 hover:bg-red-500/10 cursor-pointer">Sign Out</button>
          </div>
        </div>

      </div>

    </header>

    <!-- Page Content Container -->
    <div class="px-14 pt-8 pb-10 flex-1 flex flex-col justify-between max-w-[1100px]">
      
      <!-- Back Link & Titles -->
      <div class="space-y-3">
        <a href="home.html" class="inline-flex items-center gap-2.5 text-sm font-medium text-gray-400 hover:text-white transition-colors group">
          <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <line x1="19" y1="12" x2="5" y2="12" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></line>
            <polyline points="12 19 5 12 12 5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></polyline>
          </svg>
          <span>Back</span>
        </a>

        <div class="pt-1">
          <h1 class="text-[34px] font-extrabold text-white tracking-tight leading-tight">Entry Successful!</h1>
          <p id="welcome-subtitle" class="text-base text-gray-200 mt-1 font-normal">Welcome to the mess, Kunal.</p>
        </div>
      </div>

      <!-- Main Center Glowing Card (Matching designed_pages/page_4.png: 550px wide) -->
      <div class="flex flex-col items-center justify-center my-auto py-2">
        <div id="success-card" class="success-outer-card p-9 flex flex-col items-center justify-between relative cursor-pointer" title="Click to view My Visit details">
          
          <!-- Green Glowing Circle with Checkmark -->
          <div class="green-glow-circle flex items-center justify-center flex-shrink-0 mt-1">
            <svg class="w-12 h-12" viewBox="0 0 52 52" fill="none">
              <path d="M15 27 L23 35 L37 19" stroke="#86EFAC" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- Headline inside Card -->
          <h2 class="text-[20px] font-medium text-white tracking-wide text-center -mt-2">
            Your seat has been reserved!
          </h2>

          <!-- Inner Seat Number Box (440px wide x 140px high) -->
          <div class="seat-number-card flex flex-col items-center justify-center py-4">
            <span class="text-[13px] font-semibold text-[#CBD5E1] tracking-wider uppercase">
              SEAT NUMBER
            </span>
            <div id="seat-number-display" class="text-[64px] font-extrabold text-[#FF5E1E] leading-none tracking-tight mt-1">
              #24
            </div>
          </div>

          <!-- Bottom Row: Dining Hall & Entry Time with vertical divider -->
          <div class="w-full max-w-[440px] flex items-center justify-between px-3 pt-2">
            
            <!-- Left: Dining Hall -->
            <div class="flex items-center gap-3.5">
              <!-- Custom Building Facade SVG Icon in Orange #FF5E1E -->
              <svg class="w-8 h-8 text-[#FF5E1E] flex-shrink-0" viewBox="0 0 28 28" fill="none" stroke="#FF5E1E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 10.5 L14 3.5 L25 10.5"/>
                <rect x="4.5" y="10.5" width="19" height="13.5" rx="1"/>
                <rect x="7.5" y="13.5" width="3" height="3" rx="0.5"/>
                <rect x="17.5" y="13.5" width="3" height="3" rx="0.5"/>
                <path d="M11.5 24 V18.5 C11.5 17.5 12.5 17 14 17 C15.5 17 16.5 17.5 16.5 18.5 V24"/>
                <line x1="2" y1="24" x2="26" y2="24"/>
              </svg>
              <div>
                <div class="text-[12px] text-[#8B9BB4] font-normal">Dining Hall</div>
                <div id="dining-hall-display" class="text-[15px] font-semibold text-white tracking-tight">Central Mess</div>
              </div>
            </div>

            <!-- Vertical Divider -->
            <div class="w-[1px] h-8 bg-white/10"></div>

            <!-- Right: Entry Time -->
            <div class="flex items-center gap-3.5">
              <!-- Clock SVG Icon in Orange #FF5E1E -->
              <svg class="w-8 h-8 text-[#FF5E1E] flex-shrink-0" viewBox="0 0 28 28" fill="none" stroke="#FF5E1E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="14" cy="14" r="11"/>
                <polyline points="14 8.5 14 14 18 17.5"/>
              </svg>
              <div>
                <div class="text-[12px] text-[#8B9BB4] font-normal">Entry Time</div>
                <div id="entry-time-display" class="text-[15px] font-semibold text-white tracking-tight">10:26 PM</div>
              </div>
            </div>

          </div>

        </div>

        <!-- Footer Text below Card (Matching designed_pages/page_4.png) -->
        <div class="mt-7 text-center space-y-1">
          <div class="flex items-center justify-center gap-2">
            <h3 class="text-[22px] font-bold text-white tracking-tight">Enjoy your meal!</h3>
            <!-- Orange Fork & Knife Icon matching design -->
            <svg class="w-5 h-5 text-[#FF5E1E]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8h2.5v8H21V2c-2.76 0-5 2.24-5 4z"/>
            </svg>
          </div>
          <p class="text-sm text-[#8B9BB4] font-normal">
            Good food fuels great minds.
          </p>
        </div>

      </div>

      <!-- Spacer for bottom layout balance -->
      <div class="h-2"></div>

    </div>

  </main>

  <script src="js/api.js"></script>
  <script src="js/entry_success.js"></script>
</body>
</html>
"""

with open("../frontend/entry_success.html", "w", encoding="utf-8") as f:
    f.write(success_html.strip())

# 2. Create frontend/js/entry_success.js
success_js = """/**
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

  // Load User & Visit Info
  if (Auth.isAuthenticated()) {
    try {
      const me = await API.getMe();
      if (me && me.student) {
        const firstName = me.student.name ? me.student.name.split(' ')[0] : 'Kunal';
        if (welcomeSubtitle) welcomeSubtitle.textContent = `Welcome to the mess, ${firstName}.`;
        if (userNameEl) userNameEl.textContent = me.student.name || 'Kunal Kumar Singh';
        if (userRoleEl) userRoleEl.textContent = `${me.student.studentId} | CSE`;
      }
    } catch (e) {
      console.warn('Could not fetch user profile:', e);
    }
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
"""

with open("../frontend/js/entry_success.js", "w", encoding="utf-8") as f:
    f.write(success_js.strip())

print("Successfully updated entry_success.html and entry_success.js")
