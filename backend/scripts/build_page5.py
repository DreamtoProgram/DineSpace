import os

os.makedirs("../frontend/js", exist_ok=True)

# 1. Create frontend/my_visit.html
visit_html = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DineSpace — My Visit</title>
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
    /* Outer glowing card matching designed_pages/page_5.png */
    .visit-outer-card {
      width: 580px;
      height: 636px;
      background: rgba(13, 19, 28, 0.88);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 94, 30, 0.32);
      box-shadow: 0 0 65px -6px rgba(255, 94, 30, 0.22), inset 0 0 25px -10px rgba(255, 94, 30, 0.05);
      border-radius: 32px;
      transition: all 0.3s ease;
    }

    .visit-outer-card:hover {
      box-shadow: 0 0 78px -4px rgba(255, 94, 30, 0.28), inset 0 0 30px -8px rgba(255, 94, 30, 0.08);
    }

    /* Inner seat number card (404px wide x 126px high) */
    .seat-number-box {
      width: 404px;
      height: 126px;
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

        <!-- My Visit (ACTIVE with warm reddish glow pill matching page_5.png) -->
        <a href="my_visit.html" class="flex items-center gap-4 px-4 py-3 rounded-xl bg-[#241712] border border-[#FF5E1E]/30 text-white transition-all text-sm font-semibold shadow-inner">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    
    <!-- Top Header Bar (Height: 84px matching designed_pages/page_5.png) -->
    <header class="h-[84px] border-b border-white/5 px-10 flex items-center justify-between bg-[#070B11]/90 backdrop-blur-md sticky top-0 z-30">
      
      <!-- Search Input -->
      <div class="relative w-84">
        <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5A6A85] pointer-events-none">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" stroke-width="2"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-width="2" stroke-linecap="round"></line>
          </svg>
        </div>
        <input 
          type="text" 
          placeholder="Search for something..." 
          class="w-full bg-[#0C1320] border border-white/5 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-[#5A6A85] focus:outline-none focus:border-orange-500/50"
        />
      </div>

      <!-- Right Header Actions -->
      <div class="flex items-center gap-6">
        
        <!-- Notification Bell -->
        <a href="notifications.html" class="relative p-2 rounded-xl text-gray-300 hover:text-white hover:bg-white/5 transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <span class="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-[#FF5E1E]"></span>
        </a>

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
    <div class="px-14 pt-8 pb-8 flex-1 flex flex-col justify-between max-w-[1140px]">
      
      <!-- Titles (No Back button in designed_pages/page_5.png) -->
      <div class="space-y-1">
        <h1 class="text-[34px] font-extrabold text-white tracking-tight leading-tight">My Visit</h1>
        <p class="text-sm text-[#8B9BB4] font-normal">Here's your current dining session.</p>
      </div>

      <!-- Main Center Glowing Card (580px wide by 636px high matching page_5.png) -->
      <div class="flex flex-col items-center justify-center my-auto py-2">
        <div class="visit-outer-card p-8 flex flex-col justify-between relative">
          
          <!-- Top Section: Dining Hall Header -->
          <div>
            <div class="flex items-center justify-center gap-4 py-1">
              <!-- Building Facade Icon in Orange #FF5E1E -->
              <svg class="w-9 h-9 text-[#FF5E1E] flex-shrink-0" viewBox="0 0 28 28" fill="none" stroke="#FF5E1E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 10.5 L14 3.5 L25 10.5"/>
                <rect x="4.5" y="10.5" width="19" height="13.5" rx="1"/>
                <rect x="7.5" y="13.5" width="3" height="3" rx="0.5"/>
                <rect x="17.5" y="13.5" width="3" height="3" rx="0.5"/>
                <path d="M11.5 24 V18.5 C11.5 17.5 12.5 17 14 17 C15.5 17 16.5 17.5 16.5 18.5 V24"/>
                <line x1="2" y1="24" x2="26" y2="24"/>
              </svg>
              <div>
                <h3 id="dining-hall-title" class="text-lg font-bold text-white tracking-tight leading-snug">Central Mess</h3>
                <p class="text-xs text-[#8B9BB4] font-normal">Dining Hall</p>
              </div>
            </div>

            <!-- Top Divider -->
            <div class="w-full h-[1px] bg-white/5 mt-5"></div>
          </div>

          <!-- Middle Section: Your Seat & Status -->
          <div class="flex flex-col items-center justify-center my-1">
            <span class="text-xs font-semibold text-gray-300 tracking-wider uppercase mb-2">
              YOUR SEAT
            </span>

            <!-- Seat Box (404px wide by 126px high matching page_5.png) -->
            <div class="seat-number-box flex items-center justify-center">
              <span id="seat-number-display" class="text-[68px] font-extrabold text-[#FF5E1E] leading-none tracking-tight">
                #24
              </span>
            </div>

            <!-- Glowing Emerald Green Status Pill: "● You're dining" -->
            <div class="mt-5 px-6 py-2 rounded-full bg-[#0A2616] border border-[#10B981]/35 flex items-center gap-2.5 shadow-sm">
              <span class="w-2.5 h-2.5 rounded-full bg-[#10B981] shadow-[0_0_8px_#10B981]"></span>
              <span class="text-sm font-medium text-[#A7F3D0] tracking-wide">You're dining</span>
            </div>

            <!-- Middle Divider -->
            <div class="w-full h-[1px] bg-white/5 mt-6"></div>
          </div>

          <!-- Lower Section: Entered Time + Scan Tray Return Action Button -->
          <div class="space-y-4">
            
            <!-- Entry Time Detail Row -->
            <div class="flex items-center gap-3.5 px-2">
              <!-- Clock SVG Icon in Orange #FF5E1E -->
              <svg class="w-8 h-8 text-[#FF5E1E] flex-shrink-0" viewBox="0 0 28 28" fill="none" stroke="#FF5E1E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="14" cy="14" r="11"/>
                <polyline points="14 8.5 14 14 18 17.5"/>
              </svg>
              <div>
                <div class="text-[11px] text-[#8B9BB4] font-normal">Entered</div>
                <div id="entered-time-display" class="text-base font-bold text-white tracking-tight">10:26 PM</div>
              </div>
            </div>

            <!-- Scan Tray Return Action Button (Matching page_5.png) -->
            <a 
              href="tray_return.html" 
              id="scan-tray-btn" 
              class="w-full h-[84px] rounded-[24px] bg-[#FF5E1E] hover:bg-[#EA4C10] px-5 py-4 flex items-center justify-between transition-all cursor-pointer shadow-lg shadow-orange-500/25 group"
            >
              <!-- Left: QR Icon badge + texts -->
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-[#26150D]/80 flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 8V5a1 1 0 0 1 1-1h3"/>
                    <path d="M16 4h3a1 1 0 0 1 1 1v3"/>
                    <path d="M4 16v3a1 1 0 0 0 1 1h3"/>
                    <path d="M16 20h3a1 1 0 0 0 1-1v-3"/>
                    <rect x="7.5" y="7.5" width="2.5" height="2.5" fill="currentColor" stroke="none"/>
                    <rect x="14" y="7.5" width="2.5" height="2.5" fill="currentColor" stroke="none"/>
                    <rect x="7.5" y="14" width="2.5" height="2.5" fill="currentColor" stroke="none"/>
                    <path d="M13.5 13.5h3v3h-3z" fill="currentColor" stroke="none"/>
                  </svg>
                </div>
                <div class="text-left">
                  <div class="text-base font-bold text-[#0F172A] tracking-tight leading-tight">Scan Tray Return</div>
                  <div class="text-xs text-[#334155] font-medium mt-0.5">Finish your meal and free your seat.</div>
                </div>
              </div>

              <!-- Right: Circle Arrow Button -->
              <div class="w-12 h-12 rounded-full bg-[#2E1408]/40 group-hover:bg-[#2E1408]/60 flex items-center justify-center text-white transition-all flex-shrink-0">
                <svg class="w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <line x1="5" y1="12" x2="19" y2="12" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></line>
                  <polyline points="12 5 19 12 12 19" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></polyline>
                </svg>
              </div>
            </a>

          </div>

        </div>

        <!-- Bottom Quote below Card (Matching page_5.png) -->
        <div class="mt-8 flex items-center justify-center gap-4 text-center">
          <div class="w-16 h-[1px] bg-white/10"></div>
          <p class="font-serif-quote italic text-sm text-gray-300 tracking-wide">
            “Good Food Brighter Days”
          </p>
          <div class="w-16 h-[1px] bg-white/10"></div>
        </div>

      </div>

      <!-- Spacer -->
      <div class="h-2"></div>

    </div>

  </main>

  <script src="js/api.js"></script>
  <script src="js/my_visit.js"></script>
</body>
</html>
"""

with open("../frontend/my_visit.html", "w", encoding="utf-8") as f:
    f.write(visit_html.strip())

# 2. Create frontend/js/my_visit.js
visit_js = """/**
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

  // Load User Profile
  if (Auth.isAuthenticated()) {
    try {
      const me = await API.getMe();
      if (me && me.student) {
        if (userNameEl) userNameEl.textContent = me.student.name || 'Kunal Kumar Singh';
        if (userRoleEl) userRoleEl.textContent = `${me.student.studentId} | CSE`;
      }
    } catch (e) {
      console.warn('Could not fetch user profile:', e);
    }
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
"""

with open("../frontend/js/my_visit.js", "w", encoding="utf-8") as f:
    f.write(visit_js.strip())

print("Successfully updated my_visit.html and my_visit.js")
