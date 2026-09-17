/**
 * DineSpace: Find a Seat & Virtual Seat Map Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Elements
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const headerTime = document.getElementById('header-time');

  const statCapacity = document.getElementById('stat-capacity');
  const statOccupied = document.getElementById('stat-occupied');
  const statAvailable = document.getElementById('stat-available');
  const statOccupancyRate = document.getElementById('stat-occupancy-rate');
  const statNextSeat = document.getElementById('stat-next-seat');
  const statMySeat = document.getElementById('stat-my-seat');

  const filterAvailCount = document.getElementById('filter-avail-count');
  const filterOccCount = document.getElementById('filter-occ-count');
  const refreshSeatsBtn = document.getElementById('refresh-seats-btn');
  const seatSearchInput = document.getElementById('seat-search');

  const gridA = document.getElementById('grid-zone-a');
  const gridB = document.getElementById('grid-zone-b');
  const gridC = document.getElementById('grid-zone-c');
  const gridD = document.getElementById('grid-zone-d');

  let currentSeatsData = null;
  let currentFilter = 'all'; // 'all', 'available', 'occupied'
  let currentSearchQuery = '';

  // Setup Header Time
  function updateTime() {
    if (headerTime) {
      const now = new Date();
      headerTime.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }
  updateTime();
  setInterval(updateTime, 10000);

  // User Profile & Dropdown
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

  // Load User Info
  if (Auth.isAuthenticated()) {
    try {
      const me = await API.getMe();
      if (me && me.student) {
        if (userNameEl) userNameEl.textContent = me.student.name || 'Kunal Kumar Singh';
        if (userRoleEl) userRoleEl.textContent = `${me.student.studentId} | Campus`;
      }
    } catch (e) {
      const stored = Auth.getUser();
      if (stored && userNameEl) userNameEl.textContent = stored.name || 'Kunal Kumar Singh';
    }
  }

  // Generate Fallback Seat Map Data if Offline
  function generateFallbackSeatMap() {
    const totalCapacity = 100;
    const occupiedIndices = new Set([
      3, 4, 7, 9, 12, 15, 18, 20, 21, 24, // 24 is user's seat
      28, 30, 31, 35, 38, 41, 44, 49,
      52, 55, 59, 61, 64, 68, 70, 72,
      77, 80, 83, 85, 88, 91, 94, 96, 98, 99, 100
    ]);
    const seats = [];
    for (let i = 1; i <= totalCapacity; i++) {
      seats.push({
        seatNumber: i,
        status: occupiedIndices.has(i) ? 'occupied' : 'available'
      });
    }

    return {
      diningHall: 'Central Mess',
      capacity: totalCapacity,
      occupiedCount: occupiedIndices.size,
      availableCount: totalCapacity - occupiedIndices.size,
      mySeat: 24,
      nextAvailableSeat: 1,
      seats: seats
    };
  }

  // Load Seats from Backend or Fallback
  async function loadSeats() {
    try {
      const data = await API.getSeats();
      if (data && data.seats && data.seats.length > 0) {
        currentSeatsData = data;
      } else {
        currentSeatsData = generateFallbackSeatMap();
      }
    } catch (err) {
      console.warn('API getSeats offline, using simulated floor data:', err);
      currentSeatsData = generateFallbackSeatMap();
    }
    renderMetrics();
    renderGrids();
  }

  function renderMetrics() {
    if (!currentSeatsData) return;
    const { capacity, occupiedCount, availableCount, mySeat, nextAvailableSeat } = currentSeatsData;
    const rate = Math.round((occupiedCount / capacity) * 100);

    if (statCapacity) statCapacity.textContent = capacity;
    if (statOccupied) statOccupied.textContent = occupiedCount;
    if (statAvailable) statAvailable.textContent = availableCount;
    if (statOccupancyRate) statOccupancyRate.textContent = `${rate}%`;
    if (statNextSeat) statNextSeat.textContent = nextAvailableSeat ? `Seat #${nextAvailableSeat}` : 'Full';
    if (statMySeat) statMySeat.textContent = mySeat ? `Seat #${mySeat}` : 'None';
    if (filterAvailCount) filterAvailCount.textContent = availableCount;
    if (filterOccCount) filterOccCount.textContent = occupiedCount;
  }

  function renderGrids() {
    if (!currentSeatsData || !currentSeatsData.seats) return;

    const seats = currentSeatsData.seats;
    const mySeatNum = currentSeatsData.mySeat || 24;

    const filterFn = (s) => {
      // Match filter
      if (currentFilter === 'available' && s.status !== 'available') return false;
      if (currentFilter === 'occupied' && s.status !== 'occupied') return false;
      // Match search
      if (currentSearchQuery) {
        const query = currentSearchQuery.toLowerCase().trim();
        const numStr = String(s.seatNumber);
        if (!numStr.includes(query) && !s.status.includes(query)) return false;
      }
      return true;
    };

    const renderSeatNode = (s) => {
      const isMySeat = s.seatNumber === mySeatNum;
      const isOccupied = s.status === 'occupied';

      let bgClass = '';
      let borderClass = '';
      let textClass = '';
      let tooltipStatus = '';

      if (isMySeat) {
        bgClass = 'seat-my-seat text-white font-bold';
        tooltipStatus = 'Your Assigned Seat';
      } else if (isOccupied) {
        bgClass = 'bg-white/[0.04] hover:bg-white/[0.08]';
        borderClass = 'border border-white/5';
        textClass = 'text-gray-500 font-medium';
        tooltipStatus = 'Occupied';
      } else {
        bgClass = 'bg-emerald-500/15 hover:bg-emerald-500/30 border border-emerald-500/30';
        textClass = 'text-emerald-300 font-bold';
        tooltipStatus = 'Available - Open to Dine';
      }

      const div = document.createElement('div');
      div.className = `seat-node h-11 sm:h-10 rounded-xl flex flex-col items-center justify-center cursor-pointer relative group active:scale-95 transition-transform touch-manipulation select-none ${bgClass} ${borderClass}`;
      div.setAttribute('title', `Seat #${s.seatNumber} (${tooltipStatus})`);

      div.innerHTML = `
        <span class="text-xs ${textClass}">${s.seatNumber}</span>
        ${isMySeat ? '<span class="w-1.5 h-1.5 rounded-full bg-white animate-ping absolute -top-0.5 -right-0.5"></span>' : ''}
      `;

      return div;
    };

    // Zone A: 1 - 25
    if (gridA) {
      gridA.innerHTML = '';
      const zoneASeats = seats.filter(s => s.seatNumber >= 1 && s.seatNumber <= 25 && filterFn(s));
      zoneASeats.forEach(s => gridA.appendChild(renderSeatNode(s)));
      if (zoneASeats.length === 0) gridA.innerHTML = '<div class="col-span-5 py-4 text-center text-xs text-gray-500">No matching seats in Zone A</div>';
    }

    // Zone B: 26 - 50
    if (gridB) {
      gridB.innerHTML = '';
      const zoneBSeats = seats.filter(s => s.seatNumber >= 26 && s.seatNumber <= 50 && filterFn(s));
      zoneBSeats.forEach(s => gridB.appendChild(renderSeatNode(s)));
      if (zoneBSeats.length === 0) gridB.innerHTML = '<div class="col-span-5 py-4 text-center text-xs text-gray-500">No matching seats in Zone B</div>';
    }

    // Zone C: 51 - 75
    if (gridC) {
      gridC.innerHTML = '';
      const zoneCSeats = seats.filter(s => s.seatNumber >= 51 && s.seatNumber <= 75 && filterFn(s));
      zoneCSeats.forEach(s => gridC.appendChild(renderSeatNode(s)));
      if (zoneCSeats.length === 0) gridC.innerHTML = '<div class="col-span-5 py-4 text-center text-xs text-gray-500">No matching seats in Zone C</div>';
    }

    // Zone D: 76 - 100
    if (gridD) {
      gridD.innerHTML = '';
      const zoneDSeats = seats.filter(s => s.seatNumber >= 76 && s.seatNumber <= 100 && filterFn(s));
      zoneDSeats.forEach(s => gridD.appendChild(renderSeatNode(s)));
      if (zoneDSeats.length === 0) gridD.innerHTML = '<div class="col-span-5 py-4 text-center text-xs text-gray-500">No matching seats in Zone D</div>';
    }
  }

  // Filter Buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.className = 'filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-[#8B9BB4] hover:text-white hover:bg-white/5';
      });
      btn.className = 'filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 text-white';
      currentFilter = btn.getAttribute('data-filter') || 'all';
      renderGrids();
    });
  });

  // Dining Hall Switcher
  document.querySelectorAll('.hall-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.hall-btn').forEach(b => {
        b.className = 'hall-btn px-4 py-2 rounded-xl text-xs font-semibold text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all';
      });
      btn.className = 'hall-btn px-4 py-2 rounded-xl text-xs font-bold bg-[#FF5E1E] text-white shadow-md shadow-orange-500/20';
      loadSeats();
    });
  });

  // Search input
  if (seatSearchInput) {
    seatSearchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value;
      renderGrids();
    });
  }

  if (refreshSeatsBtn) {
    refreshSeatsBtn.addEventListener('click', () => {
      refreshSeatsBtn.classList.add('animate-spin');
      loadSeats().finally(() => {
        setTimeout(() => refreshSeatsBtn.classList.remove('animate-spin'), 500);
      });
    });
  }

  // Initial Load
  loadSeats();
});
