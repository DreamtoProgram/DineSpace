import os

os.makedirs("../frontend/js", exist_ok=True)

# 1. Create frontend/home.html
home_html = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DineSpace — Home Dashboard</title>
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
              darkCardWarm: '#1A1412',
              darkBorder: 'rgba(255, 255, 255, 0.07)',
              darkInput: '#111A29',
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
    /* Donut circle smooth transition and glowing shadow */
    #gauge-circle {
      transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
      filter: drop-shadow(0 0 10px rgba(255, 94, 30, 0.45));
    }
    
    .nav-item-active {
      background: linear-gradient(90deg, #2D1A14 0%, #1D1311 100%);
      border-left: 3px solid #FF5E1E;
      color: #FFFFFF;
    }
  </style>
</head>
<body class="bg-[#070B11] text-white min-h-screen flex overflow-x-hidden selection:bg-[#FF5E1E] selection:text-white">

  <!-- ========================================================================= -->
  <!-- LEFT SIDEBAR                                                              -->
  <!-- ========================================================================= -->
  <aside class="w-[260px] flex-shrink-0 bg-[#0A0F18] border-r border-white/5 flex flex-col justify-between p-5 min-h-screen z-20">
    
    <!-- Top Brand & Navigation -->
    <div class="space-y-7">
      
      <!-- DineSpace Brand Logo -->
      <a href="home.html" class="flex items-center gap-3 px-2 group">
        <div class="w-10 h-10 rounded-xl overflow-hidden shadow-inner flex items-center justify-center flex-shrink-0 bg-[#221511] border border-orange-500/20">
          <img src="assets/images/login_badge.png" alt="DineSpace" class="w-full h-full object-cover" />
        </div>
        <div class="flex flex-col">
          <div class="flex items-baseline tracking-tight">
            <span class="text-xl font-bold text-white">Dine</span>
            <span class="text-xl font-bold text-[#FF5E1E]">Space</span>
          </div>
          <span class="text-[10px] text-[#8B9BB4] tracking-wide font-medium -mt-1">Find your seat. Enjoy your meal.</span>
        </div>
      </a>

      <!-- Navigation Menu -->
      <nav class="space-y-1.5 pt-2">
        
        <!-- Home (ACTIVE) -->
        <a href="home.html" class="nav-item-active flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl font-semibold text-sm shadow-sm">
          <svg class="w-4 h-4 text-[#FF5E1E]" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
          </svg>
          <span>Home</span>
        </a>

        <!-- Find a Seat -->
        <a href="seats.html" class="flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <!-- Chair Icon matching designed_pages/page_2.png -->
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 19v2m12-2v2M5 14h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v5a2 2 0 002 2zm0 0v5h14v-5"></path>
          </svg>
          <span>Find a Seat</span>
        </a>

        <!-- Menu -->
        <a href="menu.html" class="flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <!-- Cloche / Food Cover Icon matching page_2.png -->
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v2m-8 12h16a1 1 0 001-1 9 9 0 00-18 0 1 1 0 001 1zM4 18h16"></path>
          </svg>
          <span>Menu</span>
        </a>

        <!-- My Visit -->
        <a href="my_visit.html" class="flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <!-- ID Card / Visit Icon -->
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="4" y="4" width="16" height="16" rx="2" stroke-width="2"></rect>
            <line x1="8" y1="9" x2="16" y2="9" stroke-width="2" stroke-linecap="round"></line>
            <line x1="8" y1="13" x2="13" y2="13" stroke-width="2" stroke-linecap="round"></line>
          </svg>
          <span>My Visit</span>
        </a>

        <!-- Visit History -->
        <a href="visit_history.html" class="flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <!-- Clock History Icon -->
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

        <!-- Notifications (with unread dot) -->
        <a href="notifications.html" class="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <div class="flex items-center gap-3.5">
            <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
            </svg>
            <span>Notifications</span>
          </div>
          <!-- Orange unread indicator dot -->
          <span class="w-2 h-2 rounded-full bg-[#FF5E1E]"></span>
        </a>

        <!-- Settings -->
        <a href="settings.html" class="flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="3" stroke-width="2"></circle>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"></path>
          </svg>
          <span>Settings</span>
        </a>

      </nav>
    </div>

    <!-- Lower Sidebar Footer -->
    <div class="px-2 pt-6 space-y-3.5">
      <div>
        <div class="w-6 h-[2px] bg-[#FF5E1E] mb-2.5 rounded-full"></div>
        <p class="font-serif-quote italic text-[15px] text-gray-200 tracking-wide leading-snug">
          “Good Food<br>Brighter Days”
        </p>
      </div>

      <!-- Leaf Illustration -->
      <div class="w-14 h-14 opacity-75">
        <img src="assets/images/leaf_illustration.png" alt="Leaf" class="w-full h-full object-contain filter drop-shadow-sm" />
      </div>

      <div class="text-[11px] text-[#5A6A85] leading-tight">
        Eat Well. Do More.<br>At Campus.
      </div>
    </div>

  </aside>

  <!-- ========================================================================= -->
  <!-- MAIN CONTENT AREA                                                         -->
  <!-- ========================================================================= -->
  <main class="flex-1 flex flex-col min-h-screen overflow-y-auto">
    
    <!-- Top Header Bar -->
    <header class="h-20 border-b border-white/5 px-8 flex items-center justify-between bg-[#070B11]/90 backdrop-blur-md sticky top-0 z-30">
      
      <!-- Search Input -->
      <div class="relative w-80">
        <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5A6A85] pointer-events-none">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" stroke-width="2"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-width="2" stroke-linecap="round"></line>
          </svg>
        </div>
        <input 
          type="text" 
          placeholder="Search for something..." 
          class="w-full bg-[#0E1624] border border-white/5 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-[#5A6A85] focus:outline-none focus:border-orange-500/50"
        />
      </div>

      <!-- Right Header Actions -->
      <div class="flex items-center gap-5">
        
        <!-- Notification Bell -->
        <a href="notifications.html" class="relative p-2 rounded-xl text-gray-300 hover:text-white hover:bg-white/5 transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#FF5E1E]"></span>
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
    <div class="p-8 max-w-[1400px] w-full mx-auto space-y-6 flex-1">
      
      <!-- Greeting Headline -->
      <div class="space-y-1">
        <h1 class="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2">
          <span id="greeting-text">Good Evening, Kunal</span>
          <span>👋</span>
        </h1>
        <p class="text-xs sm:text-sm text-[#8B9BB4]">Check the current mess status and plan your meal.</p>
      </div>

      <!-- Dining Hall Selector -->
      <div class="inline-flex items-center gap-3.5 px-4 py-3 rounded-2xl bg-[#0D1522] border border-white/5 shadow-md">
        <div class="w-9 h-9 rounded-xl bg-[#221511] border border-orange-500/20 flex items-center justify-center text-[#FF5E1E] flex-shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"></path>
          </svg>
        </div>
        <div class="text-left pr-6">
          <div class="text-[10px] uppercase tracking-wider text-[#8B9BB4] font-semibold">Dining Hall</div>
          <div class="text-sm font-bold text-white">Central Mess</div>
        </div>
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <polyline points="6 9 12 15 18 9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
        </svg>
      </div>

      <!-- Top Two-Column Grid: Current Crowd & Ready to dine? -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left: Current Crowd Card (7 cols) -->
        <div class="lg:col-span-7 rounded-2xl bg-[#0D1522] border border-white/5 p-6 shadow-xl flex flex-col justify-between relative overflow-hidden">
          
          <!-- Card Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <h2 class="text-base font-bold text-white tracking-tight">Current Crowd</h2>
              <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-semibold">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Live</span>
              </span>
            </div>
            
            <div class="flex items-center gap-2 text-xs text-[#8B9BB4]">
              <span id="updated-at-text">Updated 10:24 PM</span>
              <button id="refresh-status-btn" class="p-1 rounded-lg hover:text-white hover:bg-white/5 transition-colors cursor-pointer" title="Refresh status">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Gauge + Metrics Row -->
          <div class="flex flex-col sm:flex-row items-center gap-6 sm:gap-10 my-auto py-2">
            
            <!-- Circular Donut Progress Ring -->
            <div class="relative w-40 h-40 flex-shrink-0 flex items-center justify-center">
              <svg class="w-full h-full transform -rotate-90" viewBox="0 0 144 144">
                <!-- Background track -->
                <circle cx="72" cy="72" r="52" stroke="#162235" stroke-width="15" fill="transparent" />
                <!-- Dynamic progress arc -->
                <circle 
                  id="gauge-circle" 
                  cx="72" 
                  cy="72" 
                  r="52" 
                  stroke="url(#crowd-gradient)" 
                  stroke-width="15" 
                  stroke-dasharray="326.73" 
                  stroke-dashoffset="137.2" 
                  stroke-linecap="round" 
                  fill="transparent" 
                />
                <!-- Gradient definition -->
                <defs>
                  <linearGradient id="crowd-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#FFA048" />
                    <stop offset="100%" stop-color="#FF5E1E" />
                  </linearGradient>
                </defs>
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span id="crowd-percent" class="text-3xl font-extrabold text-white tracking-tight">58%</span>
                <span class="text-[11px] text-[#8B9BB4] font-medium mt-0.5">Occupied</span>
              </div>
            </div>

            <!-- Stats Stack -->
            <div class="flex-1 space-y-5 w-full">
              
              <!-- Crowd Level Header -->
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-[#281812] border border-orange-500/25 flex items-center justify-center text-[#FFA048] flex-shrink-0">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                </div>
                <div>
                  <div id="crowd-level-badge" class="text-base font-bold text-[#FFA048]">Moderate Crowd</div>
                  <div id="crowd-subtitle" class="text-xs text-[#8B9BB4]">Some rush, but you'll find a seat!</div>
                </div>
              </div>

              <!-- Numbers: Available & Currently Dining -->
              <div class="flex items-center gap-8 pt-1">
                <div>
                  <div id="seats-available" class="text-3xl font-extrabold text-white tracking-tight">42</div>
                  <div class="text-xs text-[#8B9BB4] font-medium mt-0.5">Seats Available</div>
                </div>

                <div class="w-px h-10 bg-white/10"></div>

                <div>
                  <div class="flex items-baseline gap-1">
                    <span id="seats-occupied" class="text-3xl font-extrabold text-white tracking-tight">58</span>
                    <span class="text-lg text-gray-500 font-semibold">/ 100</span>
                  </div>
                  <div class="text-xs text-[#8B9BB4] font-medium mt-0.5">Currently Dining</div>
                </div>
              </div>

            </div>

          </div>

        </div>

        <!-- Right: Ready to dine? Card (5 cols) -->
        <div class="lg:col-span-5 rounded-2xl bg-[#1A1412] border border-orange-500/20 p-7 shadow-xl flex flex-col items-center justify-center text-center relative overflow-hidden">
          
          <!-- Subtle top background glow -->
          <div class="absolute top-0 inset-x-0 h-24 bg-gradient-to-b from-orange-500/10 to-transparent pointer-events-none"></div>

          <!-- QR Icon Badge matching page_2.png -->
          <div class="w-14 h-14 rounded-2xl bg-[#281611] border border-orange-500/35 flex items-center justify-center text-[#FF5E1E] shadow-lg shadow-orange-950/60 mb-4">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7V5a2 2 0 012-2h2m12 0h2a2 2 0 012 2v2m0 10v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"></path>
              <rect x="7" y="7" width="10" height="10" rx="1.5" stroke-width="2"></rect>
              <circle cx="10" cy="10" r="1" fill="currentColor"></circle>
              <circle cx="14" cy="10" r="1" fill="currentColor"></circle>
              <path d="M10 14h4" stroke-linecap="round" stroke-width="2"></path>
            </svg>
          </div>

          <h2 class="text-xl font-bold text-white tracking-tight mb-1">Ready to dine?</h2>
          <p class="text-xs text-[#8B9BB4] max-w-xs mb-6">Scan at the entrance and get your seat.</p>

          <!-- Scan Entry Button -->
          <a href="entry_scan.html" class="btn-primary w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 group shadow-lg shadow-orange-500/30 cursor-pointer">
            <span>Scan Entry</span>
            <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></line>
              <polyline points="12 5 19 12 12 19" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
            </svg>
          </a>

        </div>

      </div>

      <!-- Bottom Two-Column Grid: Today's Menu & Your Visit -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left: Today's Menu Card (7 cols) -->
        <div class="lg:col-span-7 rounded-2xl bg-[#0D1522] border border-white/5 p-6 shadow-xl space-y-4">
          
          <!-- Menu Card Header with Fork & Knife Icon -->
          <div class="flex items-center justify-between border-b border-white/5 pb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded-lg bg-[#251511] flex items-center justify-center text-[#FF5E1E]">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 4v16m-4-16v6a2 2 0 002 2h2m-8-8v6a4 4 0 01-4 4H4m0 0v6m4-16v16"></path>
                </svg>
              </div>
              <h2 class="text-base font-bold text-white tracking-tight">Today's Menu</h2>
            </div>

            <a href="menu.html" class="flex items-center gap-1 text-xs font-semibold text-[#FF5E1E] hover:text-[#FFA048] transition-colors">
              <span>View Full Menu</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></line>
                <polyline points="12 5 19 12 12 19" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
              </svg>
            </a>
          </div>

          <!-- Menu Item List -->
          <div id="menu-items-list" class="divide-y divide-white/5">
            
            <!-- Item 1: Paneer Butter Masala -->
            <div class="flex items-center gap-3.5 py-2.5 group">
              <img src="assets/images/food_paneer.png" alt="Paneer Butter Masala" class="w-12 h-12 rounded-full object-cover border border-white/10 shadow-sm" />
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-white group-hover:text-[#FFA048] transition-colors">Paneer Butter Masala</span>
                  <!-- Indian Veg Icon -->
                  <span class="inline-flex items-center justify-center w-3 h-3 border border-emerald-500 rounded-sm p-[1.5px]">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  </span>
                </div>
                <div class="text-[11px] text-[#8B9BB4]">A classic favorite</div>
              </div>
            </div>

            <!-- Item 2: Dal Tadka -->
            <div class="flex items-center gap-3.5 py-2.5 group">
              <img src="assets/images/food_dal.png" alt="Dal Tadka" class="w-12 h-12 rounded-full object-cover border border-white/10 shadow-sm" />
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-white group-hover:text-[#FFA048] transition-colors">Dal Tadka</span>
                  <span class="inline-flex items-center justify-center w-3 h-3 border border-emerald-500 rounded-sm p-[1.5px]">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  </span>
                </div>
                <div class="text-[11px] text-[#8B9BB4]">Protein rich and wholesome</div>
              </div>
            </div>

            <!-- Item 3: Steamed Rice -->
            <div class="flex items-center gap-3.5 py-2.5 group">
              <img src="assets/images/food_rice.png" alt="Steamed Rice" class="w-12 h-12 rounded-full object-cover border border-white/10 shadow-sm" />
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-white group-hover:text-[#FFA048] transition-colors">Steamed Rice</span>
                  <span class="inline-flex items-center justify-center w-3 h-3 border border-emerald-500 rounded-sm p-[1.5px]">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  </span>
                </div>
                <div class="text-[11px] text-[#8B9BB4]">Light and healthy</div>
              </div>
            </div>

            <!-- Item 4: Roti -->
            <div class="flex items-center gap-3.5 py-2.5 group">
              <img src="assets/images/food_roti.png" alt="Roti" class="w-12 h-12 rounded-full object-cover border border-white/10 shadow-sm" />
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-white group-hover:text-[#FFA048] transition-colors">Roti</span>
                  <span class="inline-flex items-center justify-center w-3 h-3 border border-emerald-500 rounded-sm p-[1.5px]">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  </span>
                </div>
                <div class="text-[11px] text-[#8B9BB4]">Freshly made</div>
              </div>
            </div>

            <!-- Item 5: Gulab Jamun -->
            <div class="flex items-center gap-3.5 py-2.5 group">
              <img src="assets/images/food_sweet.png" alt="Gulab Jamun" class="w-12 h-12 rounded-full object-cover border border-white/10 shadow-sm" />
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-white group-hover:text-[#FFA048] transition-colors">Gulab Jamun</span>
                  <span class="inline-flex items-center justify-center w-3 h-3 border border-emerald-500 rounded-sm p-[1.5px]">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  </span>
                </div>
                <div class="text-[11px] text-[#8B9BB4]">Because every meal deserves a sweet ending</div>
              </div>
            </div>

          </div>

        </div>

        <!-- Right: Your Visit Card (5 cols) -->
        <div class="lg:col-span-5 rounded-2xl bg-[#0D1522] border border-white/5 p-6 shadow-xl flex flex-col justify-between">
          
          <!-- Card Header with Clock Icon -->
          <div class="flex items-center gap-2.5 border-b border-white/5 pb-3">
            <div class="w-7 h-7 rounded-lg bg-[#251511] flex items-center justify-center text-[#FF5E1E]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
                <polyline points="12 6 12 12 16 14" stroke-width="2" stroke-linecap="round"></polyline>
              </svg>
            </div>
            <h2 class="text-base font-bold text-white tracking-tight">Your Visit</h2>
          </div>

          <!-- Empty Visit State (Matching designed_pages/page_2.png) -->
          <div id="visit-empty-state" class="py-8 flex flex-col items-center justify-center text-center my-auto">
            
            <!-- Outlined Empty Tray Icon matching page_2.png -->
            <div class="w-14 h-11 rounded-lg border-2 border-dashed border-gray-600/70 flex items-center justify-center text-gray-500 mb-4">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16a1 1 0 011 1v10a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 011-1zm2 3h12m-12 3h12m-12 3h12"></path>
              </svg>
            </div>

            <h3 class="text-sm font-bold text-white">No Active Visit</h3>
            <p class="text-xs text-[#8B9BB4] mt-1 mb-6">Haven't entered the mess yet?</p>

            <a href="seats.html" class="btn-secondary w-full py-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 text-white border-white/10 hover:border-orange-500/40 cursor-pointer">
              <span>Find a Seat</span>
              <svg class="w-3.5 h-3.5 text-[#FF5E1E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></line>
                <polyline points="12 5 19 12 12 19" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
              </svg>
            </a>

          </div>

          <!-- Active Visit State (Populated dynamically if student has active visit) -->
          <div id="visit-active-state" class="hidden py-4 flex flex-col items-center justify-center text-center my-auto space-y-4">
            <div class="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              ● You're Dining
            </div>
            <div>
              <div class="text-[11px] text-[#8B9BB4] font-medium">RESERVED SEAT</div>
              <div id="active-seat-number" class="text-4xl font-extrabold text-[#FF5E1E] tracking-tight">#24</div>
            </div>
            <div class="text-xs text-gray-300">
              Duration: <span id="active-duration" class="font-bold text-white">08 min</span>
            </div>
            <a href="tray_return.html" class="btn-primary w-full py-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer">
              <span>Scan Tray Return</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></line>
                <polyline points="12 5 19 12 12 19" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
              </svg>
            </a>
          </div>

        </div>

      </div>

    </div>

  </main>

  <script src="js/api.js"></script>
  <script src="js/home.js"></script>
</body>
</html>
"""

with open("../frontend/home.html", "w", encoding="utf-8") as f:
    f.write(home_html.strip())

print("Successfully generated refined home.html")
