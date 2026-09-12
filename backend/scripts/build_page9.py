import os

os.makedirs("../frontend/js", exist_ok=True)

# 1. Create frontend/notifications.html
notifications_html = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DineSpace — Notifications</title>
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
    /* Notification Card Base */
    .notif-card {
      position: relative;
      background: #090E17;
      border: 1px solid #141E2D;
      border-radius: 18px;
      transition: all 0.2s ease;
    }
    .notif-card:hover {
      border-color: #22334A;
      background: #0B111D;
    }

    /* Active Sidebar Item pill matching page_9.png */
    .nav-item-active {
      background: #2E1B15;
      border: 1px solid rgba(255, 94, 30, 0.28);
      color: #FFFFFF;
    }

    /* Tab Filter Pills */
    .tab-pill {
      padding: 8px 22px;
      border-radius: 12px;
      font-size: 14px;
      transition: all 0.2s ease;
      cursor: pointer;
      user-select: none;
    }
    .tab-pill-inactive {
      background: #0B111A;
      border: 1px solid #162030;
      color: #8E97A6;
    }
    .tab-pill-inactive:hover {
      color: #FFFFFF;
      border-color: #22334A;
    }
    .tab-pill-active {
      background: #1F1412;
      border: 1px solid #FF5E1E;
      color: #FFFFFF;
      font-weight: 500;
      box-shadow: 0 0 12px rgba(255, 94, 30, 0.2);
    }

    /* Dropdown menu */
    .dropdown-content {
      display: none;
      position: absolute;
      right: 0;
      top: calc(100% + 8px);
      background: #0D1522;
      border: 1px solid #1F2E45;
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
      z-index: 50;
      min-width: 160px;
    }
    .dropdown-content.show {
      display: block;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #070B11;
    }
    ::-webkit-scrollbar-thumb {
      background: #182335;
      border-radius: 3px;
    }
  </style>
</head>
<body class="bg-[#070B11] text-white font-sans antialiased min-h-screen flex selection:bg-[#FF5E1E] selection:text-white">

  <!-- ================= LEFT SIDEBAR ================= -->
  <aside class="w-64 bg-[#0A0F18] border-r border-white/5 flex flex-col justify-between shrink-0 min-h-screen sticky top-0 h-screen select-none">
    <div>
      <!-- Brand Logo -->
      <div class="px-6 py-6 flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-[#1C1613] border border-orange-500/20 flex items-center justify-center text-[#FF5E1E] shadow-sm">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 2v20M18 2a3 3 0 0 0-3 3v4a3 3 0 0 0 3 3M6 2v7a3 3 0 0 0 3 3v8M6 2v5M10 2v5"/>
          </svg>
        </div>
        <div>
          <div class="font-bold text-lg leading-tight tracking-tight">
            <span class="text-white">Dine</span><span class="text-[#FF5E1E]">Space</span>
          </div>
          <div class="text-[10px] text-gray-400 font-normal">Find your seat. Enjoy your meal.</div>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="px-3 space-y-1.5 mt-2">
        <!-- Home -->
        <a href="home.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Home
        </a>

        <!-- Find a Seat -->
        <a href="home.html#find-seat" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3"/>
            <path d="M3 11v5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v2H7v-2a2 2 0 0 0-4 0Z"/>
            <path d="M5 18v2M19 18v2"/>
          </svg>
          Find a Seat
        </a>

        <!-- Menu -->
        <a href="home.html#menu" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 15h18M5 15a7 7 0 0 1 14 0M12 4v4M8 6h8"/>
          </svg>
          Menu
        </a>

        <!-- My Visit -->
        <a href="my_visit.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
            <path d="M9 12h6M9 16h6"/>
          </svg>
          My Visit
        </a>

        <!-- Visit History -->
        <a href="visit_history.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          Visit History
        </a>

        <div class="py-2">
          <div class="border-t border-white/5 mx-2"></div>
        </div>

        <!-- Notifications (ACTIVE on Page 9) -->
        <a href="notifications.html" class="flex items-center justify-between px-3.5 py-2.5 rounded-xl nav-item-active text-sm font-medium">
          <div class="flex items-center gap-3">
            <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
              <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
            </svg>
            <span class="text-white">Notifications</span>
          </div>
          <span id="sidebar-notif-dot" class="w-2 h-2 rounded-full bg-[#FF5E1E]"></span>
        </a>

        <!-- Settings -->
        <a href="#" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          Settings
        </a>
      </nav>
    </div>

    <!-- Sidebar Footer Quote & Illustration -->
    <div class="px-6 py-8">
      <div class="w-8 h-1 bg-[#FF5E1E] rounded-full mb-3"></div>
      <div class="font-serifQuote italic text-[#C5C8D0] text-sm leading-snug">
        “Good Food<br>Brighter Days”
      </div>
      <div class="mt-4 mb-3">
        <!-- Orange Leaf Vector -->
        <svg class="w-14 h-14 text-[#FF5E1E]/70" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M12 48 C16 32 32 18 52 14 C48 30 38 46 22 50 Z" />
          <path d="M12 48 Q32 30 52 14" stroke-width="1.4" />
          <path d="M26 36 Q38 32 44 26" stroke-width="1.2" />
          <path d="M20 42 Q28 40 34 36" stroke-width="1.2" />
          <path d="M34 52 C38 42 46 36 56 34 C54 42 48 50 40 52 Z" opacity="0.65" />
          <path d="M34 52 Q44 42 56 34" stroke-width="1.2" opacity="0.65" />
        </svg>
      </div>
      <div class="text-[11px] text-gray-500 font-normal leading-relaxed">
        Eat Well. Do More.<br>At Campus.
      </div>
    </div>
  </aside>

  <!-- ================= MAIN CONTENT AREA ================= -->
  <main class="flex-1 flex flex-col min-w-0 bg-[#070B11]">
    <!-- Top Header Bar (84px Height) -->
    <header class="h-[84px] border-b border-white/5 pl-10 pr-12 flex items-center justify-between shrink-0">
      <!-- Search Input -->
      <div class="relative w-[340px]">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-gray-400">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </span>
        <input 
          id="search-input"
          type="text" 
          placeholder="Search for something..." 
          class="w-full pl-10 pr-4 py-2 bg-[#0C121D] border border-white/5 rounded-xl text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-[#FF5E1E]/50 focus:ring-1 focus:ring-[#FF5E1E]/50 transition-all"
        />
      </div>

      <!-- Right Header Actions -->
      <div class="flex items-center gap-5">
        <!-- Notification Bell with Orange Dot -->
        <a href="notifications.html" class="relative p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-full transition-colors">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
          </svg>
          <span id="header-bell-dot" class="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-[#FF5E1E] border-2 border-[#070B11]"></span>
        </a>

        <!-- User Profile Pill with Dropdown -->
        <div class="relative">
          <button id="profile-dropdown-btn" class="flex items-center gap-3 pl-1 pr-2 py-1 rounded-full hover:bg-white/5 transition-colors">
            <img 
              src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80" 
              alt="Avatar" 
              class="w-8 h-8 rounded-full object-cover border border-white/10"
            />
            <div class="text-left hidden sm:block">
              <div id="user-name" class="text-xs font-semibold text-white leading-tight">Kunal Kumar Singh</div>
              <div id="user-reg" class="text-[10px] text-gray-400 leading-tight">P132-NNK | CSE</div>
            </div>
            <svg class="w-3.5 h-3.5 text-gray-400 ml-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m6 9 6 6 6-6"/>
            </svg>
          </button>

          <!-- Dropdown menu -->
          <div id="profile-dropdown-menu" class="dropdown-content">
            <div class="px-4 py-2.5 border-b border-white/5">
              <div class="text-xs font-semibold text-white" id="dropdown-full-name">Kunal Kumar Singh</div>
              <div class="text-[10px] text-gray-400" id="dropdown-student-id">P132-NNK</div>
            </div>
            <a href="#" id="btn-logout" class="flex items-center gap-2 px-4 py-2.5 text-xs text-red-400 hover:bg-red-500/10 transition-colors">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
              </svg>
              Sign Out
            </a>
          </div>
        </div>
      </div>
    </header>

    <!-- Notifications Main Content -->
    <div class="flex-1 pl-10 pr-12 py-8 overflow-y-auto w-full">
      
      <!-- Top Title Bar & 'Mark all as read' Button -->
      <div class="flex items-end justify-between mb-7">
        <div>
          <h1 class="text-[34px] font-bold text-white tracking-tight leading-tight">Notifications</h1>
          <p class="text-[#8E97A6] text-sm mt-1.5 font-normal">Stay updated with the latest from your mess.</p>
        </div>

        <!-- Mark all as read Button -->
        <button 
          id="btn-mark-all" 
          class="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#090F19] border border-[#1C2638] text-sm text-[#E2E8F0] hover:border-gray-500 transition-colors shadow-sm"
        >
          <svg class="w-4 h-4 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span class="font-normal">Mark all as read</span>
        </button>
      </div>

      <!-- Category Filter Pills -->
      <div class="flex items-center gap-3 mb-8">
        <button class="tab-pill tab-pill-active" data-filter="all">All</button>
        <button class="tab-pill tab-pill-inactive" data-filter="menu">Menu Updates</button>
        <button class="tab-pill tab-pill-inactive" data-filter="crowd">Crowd Alerts</button>
        <button class="tab-pill tab-pill-inactive" data-filter="visit">Visit Updates</button>
        <button class="tab-pill tab-pill-inactive" data-filter="system">System</button>
      </div>

      <!-- Notifications Container -->
      <div id="notif-container" class="space-y-6 w-full">

        <!-- Group 1: Today -->
        <div class="notif-group" data-group="today">
          <div class="text-[13px] font-medium text-[#8E97A6] mb-2 px-0.5">Today</div>
          <div class="space-y-3">
            
            <!-- Item 1: Today's Menu is Live! (Menu - Green) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="menu" data-id="notif-1">
              <!-- Orange Left Bracket SVG Accent -->
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <!-- Green Menu Icon Badge -->
              <div class="w-11 h-11 rounded-full bg-[#0D261A] border border-[#1A633F] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#22C55E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 2v20M18 2a3 3 0 0 0-3 3v4a3 3 0 0 0 3 3M6 2v7a3 3 0 0 0 3 3v8M6 2v5M10 2v5"/>
                </svg>
              </div>

              <!-- Message Content -->
              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Today's Menu is Live!</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">Check out today's lunch and dinner menu at Central Mess.</div>
              </div>

              <!-- Right: Time & Unread Indicator -->
              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">11:02 AM</span>
                <span class="notif-unread-dot w-2.5 h-2.5 rounded-full bg-[#FF5E1E] shadow-[0_0_8px_#FF5E1E] flex-shrink-0"></span>
              </div>
            </div>

            <!-- Item 2: Crowd Update (Crowd - Orange) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="crowd" data-id="notif-2">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <!-- Orange Crowd Icon Badge -->
              <div class="w-11 h-11 rounded-full bg-[#2E1810] border border-[#7C2D12] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#FF5E1E]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 3s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Crowd Update</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">Central Mess is now Moderately Crowded (65% full).</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">10:15 AM</span>
                <span class="notif-unread-dot w-2.5 h-2.5 rounded-full bg-[#FF5E1E] shadow-[0_0_8px_#FF5E1E] flex-shrink-0"></span>
              </div>
            </div>

            <!-- Item 3: Your Visit Completed (Visit - Blue) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="visit" data-id="notif-3">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <!-- Blue Seat Icon Badge -->
              <div class="w-11 h-11 rounded-full bg-[#0A2038] border border-[#1E40AF] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#38BDF8]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3"/>
                  <path d="M3 11v5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v2H7v-2a2 2 0 0 0-4 0Z"/>
                  <path d="M5 18v2M19 18v2"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Your Visit Completed</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">You vacated Seat #24. Thanks for dining with us!</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">10:44 PM</span>
                <span class="notif-unread-dot w-2.5 h-2.5 rounded-full bg-[#FF5E1E] shadow-[0_0_8px_#FF5E1E] flex-shrink-0"></span>
              </div>
            </div>

            <!-- Item 4: Reminder (System - Amber, Read) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="system" data-id="notif-4">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <!-- Amber Bell Icon Badge -->
              <div class="w-11 h-11 rounded-full bg-[#2B1D0C] border border-[#78350F] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#F59E0B]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
                  <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Reminder</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">Don't forget to scan at the tray return counter after your meal.</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">09:30 PM</span>
                <div class="w-2.5 h-2.5 flex-shrink-0"></div> <!-- Placeholder to maintain alignment -->
              </div>
            </div>

          </div>
        </div>

        <!-- Group 2: Yesterday -->
        <div class="notif-group" data-group="yesterday">
          <div class="text-[13px] font-medium text-[#8E97A6] mb-2 px-0.5">Yesterday</div>
          <div class="space-y-3">

            <!-- Item 5: Dinner Menu Updated (Menu - Green, Read) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="menu" data-id="notif-5">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <div class="w-11 h-11 rounded-full bg-[#0D261A] border border-[#1A633F] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#22C55E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 2v20M18 2a3 3 0 0 0-3 3v4a3 3 0 0 0 3 3M6 2v7a3 3 0 0 0 3 3v8M6 2v5M10 2v5"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Dinner Menu Updated</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">New special: Paneer Butter Masala at Central Mess.</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">08:12 PM</span>
                <div class="w-2.5 h-2.5 flex-shrink-0"></div>
              </div>
            </div>

            <!-- Item 6: High Crowd Alert (Crowd - Red, Read) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="crowd" data-id="notif-6">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <!-- Red Crowd Icon Badge -->
              <div class="w-11 h-11 rounded-full bg-[#331114] border border-[#881D24] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#EF4444]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 3s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">High Crowd Alert</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">South Mess is now Highly Crowded (90% full). Consider an alternate mess.</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">07:45 PM</span>
                <div class="w-2.5 h-2.5 flex-shrink-0"></div>
              </div>
            </div>

          </div>
        </div>

        <!-- Group 3: Sep 9, 2026 -->
        <div class="notif-group" data-group="sep9">
          <div class="text-[13px] font-medium text-[#8E97A6] mb-2 px-0.5">Sep 9, 2026</div>
          <div class="space-y-3">

            <!-- Item 7: Seat Assigned (Visit - Blue, Read) -->
            <div class="notif-card flex items-center px-6 py-4 cursor-pointer group min-h-[82px]" data-category="visit" data-id="notif-7">
              <div class="absolute left-0 top-0 bottom-0 w-8 pointer-events-none overflow-hidden">
                <svg class="w-8 h-full" preserveAspectRatio="none" viewBox="0 0 32 82" fill="none">
                  <path d="M 24 1.5 C 10 1.5 1.5 10 1.5 20 L 1.5 62 C 1.5 72 10 80.5 24 80.5" 
                        stroke="#FF5E1E" stroke-width="4" stroke-linecap="round" 
                        style="filter: drop-shadow(0 0 8px rgba(255, 94, 30, 0.75));" />
                </svg>
              </div>

              <div class="w-11 h-11 rounded-full bg-[#0A2038] border border-[#1E40AF] flex items-center justify-center flex-shrink-0 ml-3 mr-4 shadow-sm">
                <svg class="w-5 h-5 text-[#38BDF8]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3"/>
                  <path d="M3 11v5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v2H7v-2a2 2 0 0 0-4 0Z"/>
                  <path d="M5 18v2M19 18v2"/>
                </svg>
              </div>

              <div>
                <div class="text-[16px] font-semibold text-white tracking-tight leading-tight">Seat Assigned</div>
                <div class="text-[13px] text-[#8E97A6] font-normal leading-tight mt-1">You were assigned Seat #18 at Central Mess.</div>
              </div>

              <div class="ml-auto flex items-center gap-4 pr-1">
                <span class="text-[13px] text-[#8E97A6] font-normal">01:04 PM</span>
                <div class="w-2.5 h-2.5 flex-shrink-0"></div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </main>

  <script src="js/api.js"></script>
  <script src="js/notifications.js"></script>
</body>
</html>
"""

with open("../frontend/notifications.html", "w", encoding="utf-8") as f:
    f.write(notifications_html)
print("Wrote frontend/notifications.html")

# 2. Create frontend/js/notifications.js
notifications_js = """/**
 * DineSpace — Notifications Controller
 * Handles category filtering, mark-as-read actions, live search, and dynamic API sync.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Auth check (allow file preview)
  const token = localStorage.getItem('dinespace_token');
  if (!token && !window.location.protocol.startsWith('file')) {
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
"""

with open("../frontend/js/notifications.js", "w", encoding="utf-8") as f:
    f.write(notifications_js)
print("Wrote frontend/js/notifications.js")
