import os

os.makedirs("../frontend", exist_ok=True)

html_content = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DineSpace — Student Login</title>
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
              darkBg: '#070B11',
              darkCard: '#0D1522',
              darkInput: '#111A29',
              darkBorder: 'rgba(255, 255, 255, 0.08)',
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
    /* Specific pixel-level alignment matching designed_pages/login_page.png */
    .hero-bg-container {
      position: absolute;
      top: 40px;
      left: 360px;
      width: 700px;
      height: 740px;
      background-image: url('assets/images/dining_hall_hero.png');
      background-size: cover;
      background-position: center top;
      border-radius: 20px;
      pointer-events: none;
      z-index: 1;
      opacity: 0.95;
      mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.4) 15%, black 40%, black 85%, transparent 100%), linear-gradient(to bottom, black 85%, transparent 100%);
      -webkit-mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.4) 15%, black 40%, black 85%, transparent 100%), linear-gradient(to bottom, black 85%, transparent 100%);
      -webkit-mask-composite: source-in;
      mask-composite: intersect;
    }

    @media (max-width: 1024px) {
      .hero-bg-container {
        display: none;
      }
    }
  </style>
</head>
<body class="bg-[#070B11] text-white min-h-screen flex flex-col justify-between relative overflow-x-hidden selection:bg-[#FF5E1E] selection:text-white">

  <!-- Ambient background subtle glow -->
  <div class="ambient-glow-left"></div>
  <div class="ambient-glow-card"></div>

  <!-- Hero background photo matching designed_pages/login_page.png -->
  <div class="hero-bg-container"></div>

  <!-- Main Viewport Layout -->
  <div class="relative z-10 w-full max-w-[1711px] mx-auto px-8 sm:px-12 lg:px-16 py-7 flex-1 flex flex-col justify-between min-h-screen">
    
    <!-- Top Header -->
    <header class="flex items-center justify-between w-full">
      <!-- DineSpace Brand Logo -->
      <a href="login.html" class="flex items-center gap-3.5 group">
        <div class="w-11 h-11 rounded-full p-[2px] shadow-lg flex items-center justify-center">
          <img src="assets/images/logo_emblem.png" alt="DineSpace Logo" class="w-11 h-11 object-contain rounded-full" />
        </div>
        <div class="flex flex-col">
          <div class="flex items-baseline tracking-tight">
            <span class="text-2xl font-bold text-white">Dine</span>
            <span class="text-2xl font-bold text-[#FF5E1E]">Space</span>
          </div>
          <span class="text-[11px] text-[#8B9BB4] tracking-wide font-medium -mt-1">Find your seat. Enjoy your meal.</span>
        </div>
      </a>

      <!-- Need help button -->
      <a href="#" onclick="alert('DineSpace Campus Support:\nFor meal plans or credential assistance, visit the Campus Mess Office or email dining@campus.edu.'); return false;" class="flex items-center gap-1.5 text-xs text-[#8B9BB4] hover:text-white transition-colors duration-200 py-1.5 px-3 rounded-lg hover:bg-white/5">
        <span>Need help?</span>
        <svg class="w-4 h-4 text-[#8B9BB4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
          <line x1="12" y1="16" x2="12" y2="12" stroke-width="2" stroke-linecap="round"></line>
          <line x1="12" y1="8" x2="12.01" y2="8" stroke-width="2" stroke-linecap="round"></line>
        </svg>
      </a>
    </header>

    <!-- Main Content Split Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center my-auto py-6">
      
      <!-- LEFT COLUMN: Brand Story, Features, Quote & Stats (7 cols) -->
      <div class="lg:col-span-7 flex flex-col justify-center space-y-7 max-w-[620px] relative z-20">
        
        <!-- Main Headline -->
        <div class="space-y-3">
          <h1 class="text-4xl sm:text-5xl lg:text-[56px] font-extrabold leading-[1.12] tracking-tight">
            Less Waiting.<br>
            <span class="text-[#FF5E1E]">More Eating.</span>
          </h1>
          <p class="text-[#8B9BB4] text-base sm:text-[17px] leading-relaxed max-w-lg font-normal pt-1">
            Real-time mess occupancy, today's menu, and a smarter dining experience for every student.
          </p>
        </div>

        <!-- 4 Key Feature Badges -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1 max-w-[540px]">
          
          <!-- Feature 1: Live Crowd Updates -->
          <div class="feature-pill rounded-xl p-3.5 flex items-center gap-3.5 bg-[#0F1827]/85 border border-white/5 backdrop-blur-md shadow-md">
            <div class="w-10 h-10 rounded-lg bg-[#271510] border border-orange-500/20 flex items-center justify-center flex-shrink-0 text-[#FF5E1E]">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-white">Live Crowd Updates</h3>
              <p class="text-[11px] text-[#8B9BB4]">Check seat availability in real time</p>
            </div>
          </div>

          <!-- Feature 2: Today's Menu -->
          <div class="feature-pill rounded-xl p-3.5 flex items-center gap-3.5 bg-[#0F1827]/85 border border-white/5 backdrop-blur-md shadow-md">
            <div class="w-10 h-10 rounded-lg bg-[#271510] border border-orange-500/20 flex items-center justify-center flex-shrink-0 text-[#FF5E1E]">
              <!-- Utensils / Fork and Knife icon -->
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 4v16m-4-16v6a2 2 0 002 2h2m-8-8v6a4 4 0 01-4 4H4m0 0v6m4-16v16"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-white">Today's Menu</h3>
              <p class="text-[11px] text-[#8B9BB4]">Know what's cooking today</p>
            </div>
          </div>

          <!-- Feature 3: Quick & Easy Entry -->
          <div class="feature-pill rounded-xl p-3.5 flex items-center gap-3.5 bg-[#0F1827]/85 border border-white/5 backdrop-blur-md shadow-md">
            <div class="w-10 h-10 rounded-lg bg-[#271510] border border-orange-500/20 flex items-center justify-center flex-shrink-0 text-[#FF5E1E]">
              <!-- QR Scan Frame Icon -->
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-white">Quick & Easy Entry</h3>
              <p class="text-[11px] text-[#8B9BB4]">Scan and get your seat</p>
            </div>
          </div>

          <!-- Feature 4: Hassle-Free Exit -->
          <div class="feature-pill rounded-xl p-3.5 flex items-center gap-3.5 bg-[#0F1827]/85 border border-white/5 backdrop-blur-md shadow-md">
            <div class="w-10 h-10 rounded-lg bg-[#271510] border border-orange-500/20 flex items-center justify-center flex-shrink-0 text-[#FF5E1E]">
              <!-- Clock Icon -->
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
                <polyline points="12 6 12 12 16 14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-white">Hassle-Free Exit</h3>
              <p class="text-[11px] text-[#8B9BB4]">Scan at tray return or auto-release</p>
            </div>
          </div>

        </div>

        <!-- Campus Quote -->
        <div class="pt-2">
          <div class="w-7 h-[2px] bg-[#FF5E1E] mb-2 rounded-full"></div>
          <p class="font-serif-quote italic text-lg sm:text-xl text-gray-200 tracking-wide">
            “Good food. Better days.”
          </p>
          <p class="text-xs text-[#8B9BB4] mt-0.5 font-normal">— For a Happier Campus</p>
        </div>

        <!-- Bottom Stats Bar -->
        <div class="inline-flex flex-wrap items-center bg-[#0E1624]/90 border border-white/5 rounded-2xl p-4 sm:p-5 gap-6 sm:gap-8 backdrop-blur-md shadow-xl max-w-fit">
          <!-- Stat 1 -->
          <div class="flex items-center gap-3.5">
            <div class="text-[#FF5E1E]">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
              </svg>
            </div>
            <div>
              <div class="text-lg sm:text-xl font-bold text-white">25K+</div>
              <div class="text-[11px] text-[#8B9BB4]">Students Served Daily</div>
            </div>
          </div>

          <div class="hidden sm:block w-px h-8 bg-white/10"></div>

          <!-- Stat 2 -->
          <div class="flex items-center gap-3.5">
            <div class="text-[#FF5E1E]">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"></path>
              </svg>
            </div>
            <div>
              <div class="text-lg sm:text-xl font-bold text-white">4+</div>
              <div class="text-[11px] text-[#8B9BB4]">Dining Halls</div>
            </div>
          </div>

          <div class="hidden sm:block w-px h-8 bg-white/10"></div>

          <!-- Stat 3 -->
          <div class="flex items-center gap-3.5">
            <div class="text-[#FF5E1E]">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
            </div>
            <div>
              <div class="text-lg sm:text-xl font-bold text-white">Happier</div>
              <div class="text-[11px] text-[#8B9BB4]">Campus Community</div>
            </div>
          </div>
        </div>

      </div>

      <!-- RIGHT COLUMN: Sign In Card (5 cols) -->
      <div class="lg:col-span-5 flex justify-center lg:justify-end w-full relative z-20">
        <div class="glass-card w-full max-w-[460px] rounded-[24px] p-8 sm:p-10 shadow-2xl relative">
          
          <!-- Card Brand Header with exact cropped fork/knife badge -->
          <div class="flex items-center gap-3.5 mb-6">
            <div class="w-12 h-12 rounded-xl overflow-hidden shadow-inner flex items-center justify-center flex-shrink-0">
              <img src="assets/images/login_badge.png" alt="DineSpace" class="w-full h-full object-cover" />
            </div>
            <div>
              <div class="flex items-baseline">
                <span class="text-2xl font-bold text-white">Dine</span>
                <span class="text-2xl font-bold text-[#FF5E1E]">Space</span>
              </div>
              <p class="text-xs text-[#8B9BB4]">Dine smarter. Live better.</p>
            </div>
          </div>

          <!-- Welcome Titles -->
          <div class="space-y-1 mb-6">
            <h2 class="text-2xl font-bold text-white tracking-tight">Welcome Back</h2>
            <p class="text-xs sm:text-sm text-[#8B9BB4]">Sign in with your student credentials to continue.</p>
          </div>

          <!-- Error Alert Banner -->
          <div id="error-banner" class="hidden toast-error rounded-xl p-3.5 mb-5 flex items-start gap-2.5 text-xs transition-all duration-200">
            <svg class="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
              <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round"></line>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round"></line>
            </svg>
            <span id="error-message" class="leading-relaxed"></span>
          </div>

          <!-- Login Form -->
          <form id="login-form" class="space-y-4">
            
            <!-- Student ID Field -->
            <div class="space-y-1.5">
              <label for="student-id" class="block text-xs font-semibold text-gray-300">Student ID</label>
              <div class="relative flex items-center">
                <div class="absolute left-3.5 text-gray-500 pointer-events-none flex items-center justify-center">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
                <input 
                  type="text" 
                  id="student-id" 
                  name="studentId"
                  required
                  placeholder="Enter your Student ID (e.g., 12345678)" 
                  class="custom-input w-full pl-10 pr-4 py-3 rounded-xl text-sm focus:ring-0 placeholder:text-gray-500 font-medium"
                />
              </div>
            </div>

            <!-- Password Field -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <label for="password" class="block text-xs font-semibold text-gray-300">Password</label>
                <a href="#" onclick="alert('Password Reset:\nPlease contact your mess administrator or email support@campus.edu to reset your credentials.'); return false;" class="text-xs text-[#FF5E1E] hover:text-[#EA4C10] font-medium transition-colors">Forgot password?</a>
              </div>
              <div class="relative flex items-center">
                <div class="absolute left-3.5 text-gray-500 pointer-events-none flex items-center justify-center">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-width="2"></rect>
                    <path d="M7 11V7a5 5 0 0110 0v4" stroke-width="2"></path>
                  </svg>
                </div>
                <input 
                  type="password" 
                  id="password" 
                  name="password"
                  required
                  placeholder="Enter your password" 
                  class="custom-input w-full pl-10 pr-10 py-3 rounded-xl text-sm focus:ring-0 placeholder:text-gray-500 font-medium"
                />
                <button 
                  type="button" 
                  id="toggle-password" 
                  class="absolute right-3.5 text-gray-500 hover:text-white transition-colors focus:outline-none flex items-center justify-center cursor-pointer"
                  title="Toggle password visibility"
                >
                  <svg class="w-4 h-4 text-gray-500 hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Sign In Button -->
            <button 
              type="submit" 
              id="submit-btn" 
              class="btn-primary w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 mt-2 group cursor-pointer"
            >
              <svg id="submit-spinner" class="hidden animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span id="submit-text">Sign In</span>
              <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></line>
                <polyline points="12 5 19 12 12 19" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
              </svg>
            </button>
          </form>

          <!-- Divider -->
          <div class="relative my-6 flex items-center justify-center">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-white/10"></div>
            </div>
            <div class="relative px-3 bg-[#0D1522] text-[11px] font-semibold text-[#8B9BB4] uppercase tracking-wider">
              OR
            </div>
          </div>

          <!-- Continue with QR On-Campus -->
          <button 
            type="button" 
            id="qr-login-btn" 
            class="btn-secondary w-full py-3 px-4 rounded-xl flex items-center justify-center gap-3.5 text-left group cursor-pointer"
          >
            <div class="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-[#FF5E1E] flex-shrink-0 group-hover:border-orange-500/40 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <div class="text-xs font-semibold text-white">Continue with QR (On-Campus)</div>
              <div class="text-[10px] text-[#8B9BB4]">Only for registered devices</div>
            </div>
          </button>

          <!-- Administrator note & Demo Autofill -->
          <div class="mt-6 text-center space-y-2.5">
            <p class="text-xs text-[#8B9BB4]">
              New here? <a href="#" onclick="alert('Please contact your college dining administrator to register your student account.'); return false;" class="text-gray-300 hover:text-white underline underline-offset-2 transition-colors">Contact your mess administrator.</a>
            </p>
            <div>
              <button 
                type="button" 
                id="demo-fill-btn" 
                class="inline-flex items-center gap-1.5 text-[11px] px-3 py-1 rounded-full bg-orange-500/10 text-[#FF5E1E] hover:bg-orange-500/20 border border-orange-500/25 transition-all cursor-pointer shadow-sm"
              >
                <span>⚡ Fill Demo: Sarah Chen (STU1042)</span>
              </button>
            </div>
          </div>

        </div>
      </div>

    </div>

    <!-- Bottom Footer bar -->
    <footer class="w-full text-center py-1 text-[11px] text-[#4A5568]">
      &copy; 2026 DineSpace. Campus Dining System. All rights reserved.
    </footer>

  </div>

  <script src="js/api.js"></script>
  <script src="js/login.js"></script>
</body>
</html>
"""

with open("../frontend/login.html", "w", encoding="utf-8") as f:
    f.write(html_content.strip())

print("Successfully regenerated login.html with refined design matching")
