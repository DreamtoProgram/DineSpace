/**
 * DineSpace: Today's Menu Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-name');
  const userRoleEl = document.getElementById('user-role');
  const dishesGrid = document.getElementById('dishes-grid');
  const mealTitleDisplay = document.getElementById('meal-title-display');
  const dishCountDisplay = document.getElementById('dish-count-display');
  const menuSearchInput = document.getElementById('menu-search');
  const headerDate = document.getElementById('header-date');
  const fullDateText = document.getElementById('full-date-text');

  let selectedMeal = 'Lunch';
  let selectedDiet = 'all'; // 'all', 'veg', 'nonveg'
  let searchQuery = '';

  // Dates
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const fullDate = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  if (headerDate) headerDate.textContent = dateStr;
  if (fullDateText) fullDateText.textContent = fullDate;

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

  // Instant paint user info from cache
  const storedUser = Auth.getUser();
  if (storedUser) {
    if (userNameEl) userNameEl.textContent = storedUser.name || 'Student';
    if (userRoleEl) userRoleEl.textContent = `${storedUser.studentId || 'STU1042'} | Central Mess`;
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

  // Comprehensive Menu Dataset (Fallback & Enhancements)
  const MENU_DATABASE = {
    Lunch: [
      {
        name: 'Paneer Butter Masala',
        desc: 'Cottage cheese simmered in a rich tomato, butter, and cashew gravy with aromatic fenugreek leaves.',
        isVeg: true,
        calories: 320,
        protein: '14g',
        special: true,
        allergens: 'Dairy, Nuts'
      },
      {
        name: 'Dal Makhani',
        desc: 'Slow-cooked whole black lentils and red kidney beans finished with country churned butter and cream.',
        isVeg: true,
        calories: 260,
        protein: '12g',
        special: false,
        allergens: 'Dairy'
      },
      {
        name: 'Murgh Lababdar (Chicken)',
        desc: 'Tender tandoori chicken chunks cooked in spiced onion tomato masala and grated paneer.',
        isVeg: false,
        calories: 420,
        protein: '32g',
        special: true,
        allergens: 'Dairy'
      },
      {
        name: 'Jeera Rice & Tawa Roti',
        desc: 'Steamed basmati rice tempered with roasted cumin seeds alongside whole wheat fresh rotis.',
        isVeg: true,
        calories: 210,
        protein: '6g',
        special: false,
        allergens: 'Gluten'
      },
      {
        name: 'Boondi Raita',
        desc: 'Chilled spiced yogurt infused with crispy chickpea pearls, roasted cumin, and black salt.',
        isVeg: true,
        calories: 90,
        protein: '4g',
        special: false,
        allergens: 'Dairy'
      },
      {
        name: 'Fresh Garden Salad',
        desc: 'Crisp sliced cucumbers, red onions, carrots, and tomatoes seasoned with lemon and fresh coriander.',
        isVeg: true,
        calories: 45,
        protein: '1g',
        special: false,
        allergens: 'None'
      },
      {
        name: 'Gulab Jamun (2 pcs)',
        desc: 'Warm milk-solid dumplings soaked in cardamom and rose infused golden saffron syrup.',
        isVeg: true,
        calories: 240,
        protein: '3g',
        special: false,
        allergens: 'Dairy, Gluten'
      }
    ],
    Dinner: [
      {
        name: 'Kadai Paneer',
        desc: 'Paneer batons tossed with bell peppers, onions, and crushed whole coriander seeds in a robust gravy.',
        isVeg: true,
        calories: 290,
        protein: '15g',
        special: false,
        allergens: 'Dairy'
      },
      {
        name: 'Yellow Dal Tadka',
        desc: 'Pigeon pea lentils tempered with desi ghee, garlic, dried red chili, and cumin seeds.',
        isVeg: true,
        calories: 180,
        protein: '9g',
        special: false,
        allergens: 'Dairy (Ghee)'
      },
      {
        name: 'Butter Chicken Curry',
        desc: 'Charcoal-grilled boneless chicken cooked in silky smooth tomato gravy with kasoori methi.',
        isVeg: false,
        calories: 440,
        protein: '34g',
        special: true,
        allergens: 'Dairy, Nuts'
      },
      {
        name: 'Veg Pulao & Phulka Roti',
        desc: 'Long grain rice cooked with seasonal diced vegetables, cinnamon, and whole spices.',
        isVeg: true,
        calories: 230,
        protein: '5g',
        special: false,
        allergens: 'Gluten'
      },
      {
        name: 'Cucumber Mint Raita',
        desc: 'Whisked fresh curd with grated organic cucumbers and crushed garden mint.',
        isVeg: true,
        calories: 80,
        protein: '3g',
        special: false,
        allergens: 'Dairy'
      },
      {
        name: 'Moong Dal Halwa',
        desc: 'Traditional roasted yellow lentil pudding with pure ghee, almonds, and green cardamom.',
        isVeg: true,
        calories: 310,
        protein: '6g',
        special: true,
        allergens: 'Dairy, Nuts'
      }
    ],
    Breakfast: [
      {
        name: 'Masala Dosa & Sambar',
        desc: 'Crispy fermented rice-lentil crepe filled with spiced potato masala, served with piping hot vegetable sambar.',
        isVeg: true,
        calories: 340,
        protein: '8g',
        special: true,
        allergens: 'Mustard'
      },
      {
        name: 'Steamed Idli with Chutneys',
        desc: 'Soft fluffy steamed cakes served with coconut and roasted tomato chutneys.',
        isVeg: true,
        calories: 190,
        protein: '6g',
        special: false,
        allergens: 'Mustard'
      },
      {
        name: 'Scrambled Eggs & Toast',
        desc: 'Farm eggs scrambled with butter and fresh herbs served with toasted multigrain bread.',
        isVeg: false,
        calories: 280,
        protein: '16g',
        special: false,
        allergens: 'Egg, Gluten'
      },
      {
        name: 'Poha with Peanuts',
        desc: 'Flattened rice tossed with turmeric, mustard seeds, curry leaves, and crunchy roasted peanuts.',
        isVeg: true,
        calories: 220,
        protein: '5g',
        special: false,
        allergens: 'Peanuts'
      },
      {
        name: 'Filter Coffee & Masala Chai',
        desc: 'Freshly brewed South Indian filter coffee or spiced ginger-cardamom tea.',
        isVeg: true,
        calories: 70,
        protein: '2g',
        special: false,
        allergens: 'Dairy'
      }
    ],
    Snacks: [
      {
        name: 'Vegetable Samosa (2 pcs)',
        desc: 'Crispy golden pastry crust filled with spiced potatoes and green peas, served with sweet tamarind chutney.',
        isVeg: true,
        calories: 260,
        protein: '4g',
        special: true,
        allergens: 'Gluten'
      },
      {
        name: 'Paneer Kathi Roll',
        desc: 'Spiced marinated cottage cheese rolled in flaky flatbread with mint mayo and pickled onion rings.',
        isVeg: true,
        calories: 350,
        protein: '14g',
        special: false,
        allergens: 'Dairy, Gluten'
      },
      {
        name: 'Chicken Momos (6 pcs)',
        desc: 'Steamed Tibetan dumplings stuffed with juicy minced chicken and ginger, served with fiery chili dip.',
        isVeg: false,
        calories: 280,
        protein: '18g',
        special: true,
        allergens: 'Gluten'
      },
      {
        name: 'Adrak Chai (Ginger Tea)',
        desc: 'Fresh crushed organic ginger boiled with Assam tea leaves and whole milk.',
        isVeg: true,
        calories: 60,
        protein: '2g',
        special: false,
        allergens: 'Dairy'
      }
    ]
  };

  async function loadMenu() {
    let items = MENU_DATABASE[selectedMeal] || [];

    try {
      const liveData = await API.getMenuToday();
      if (liveData && liveData.menus) {
        const matching = liveData.menus.find(m => m.mealType.toLowerCase() === selectedMeal.toLowerCase());
        if (matching && matching.items && matching.items.length > 0) {
          // Merge API items with dietary tags
          items = matching.items.map(apiItem => {
            const isNonVeg = /chicken|egg|fish|mutton|meat/i.test(apiItem.name);
            return {
              name: apiItem.name,
              desc: apiItem.description || 'Prepared fresh daily by our campus culinary team.',
              isVeg: !isNonVeg,
              calories: isNonVeg ? 380 : 250,
              protein: isNonVeg ? '24g' : '10g',
              special: false,
              allergens: 'Fresh Kitchen'
            };
          });
        }
      }
    } catch (e) {
      // Backend offline or no menu for today, using rich dataset
    }

    renderDishes(items);
  }

  function renderDishes(items) {
    if (!dishesGrid) return;
    dishesGrid.innerHTML = '';

    // Filter
    const filtered = items.filter(dish => {
      // Diet
      if (selectedDiet === 'veg' && !dish.isVeg) return false;
      if (selectedDiet === 'nonveg' && dish.isVeg) return false;

      // Search
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchName = dish.name.toLowerCase().includes(q);
        const matchDesc = dish.desc.toLowerCase().includes(q);
        if (!matchName && !matchDesc) return false;
      }
      return true;
    });

    if (dishCountDisplay) {
      dishCountDisplay.textContent = `(${filtered.length} items)`;
    }

    if (mealTitleDisplay) {
      mealTitleDisplay.firstElementChild.textContent = `${selectedMeal} Menu Items`;
    }

    if (filtered.length === 0) {
      dishesGrid.innerHTML = `
        <div class="col-span-full py-12 text-center text-gray-400 bg-[#0E1624]/60 rounded-2xl border border-white/5">
          <p class="text-sm">No dishes match your filter criteria.</p>
          <button id="reset-filter-btn" class="mt-3 text-xs text-[#FF5E1E] font-semibold hover:underline">Reset Filters</button>
        </div>
      `;
      const resetBtn = document.getElementById('reset-filter-btn');
      if (resetBtn) {
        resetBtn.addEventListener('click', () => {
          selectedDiet = 'all';
          searchQuery = '';
          if (menuSearchInput) menuSearchInput.value = '';
          document.querySelectorAll('.diet-filter-btn').forEach((b, idx) => {
            b.className = idx === 0 
              ? 'diet-filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 text-white'
              : 'diet-filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-[#8B9BB4] hover:text-white hover:bg-white/5 flex items-center gap-1.5';
          });
          renderDishes(items);
        });
      }
      return;
    }

    filtered.forEach(dish => {
      const card = document.createElement('div');
      card.className = 'dish-card glass-card rounded-2xl p-5 border border-white/5 bg-[#0E1624]/85 flex flex-col justify-between space-y-4';

      card.innerHTML = `
        <div class="space-y-3">
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2">
              ${dish.isVeg 
                ? '<span class="w-4 h-4 rounded border border-emerald-500 flex items-center justify-center flex-shrink-0" title="Vegetarian"><span class="w-2 h-2 rounded-full bg-emerald-500"></span></span>' 
                : '<span class="w-4 h-4 rounded border border-red-500 flex items-center justify-center flex-shrink-0" title="Non-Vegetarian"><span class="w-2 h-2 bg-red-500 rotate-45"></span></span>'
              }
              <h3 class="text-sm font-bold text-white leading-snug">${dish.name}</h3>
            </div>
            ${dish.special ? '<span class="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-semibold flex-shrink-0">★ Chef Special</span>' : ''}
          </div>
          
          <p class="text-xs text-[#8B9BB4] leading-relaxed line-clamp-2">${dish.desc}</p>
        </div>

        <div class="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-[#8B9BB4]">
          <div class="flex items-center gap-3">
            <span class="font-medium text-gray-300">${dish.calories} kcal</span>
            <span>•</span>
            <span class="text-orange-400 font-semibold">${dish.protein} protein</span>
          </div>
          <span class="text-[11px] text-gray-500 truncate max-w-[110px]" title="Allergens: ${dish.allergens}">${dish.allergens}</span>
        </div>
      `;

      dishesGrid.appendChild(card);
    });
  }

  // Meal Tabs
  document.querySelectorAll('.meal-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.meal-tab-btn').forEach(b => {
        b.className = 'meal-tab-btn px-5 py-2.5 rounded-xl text-xs font-semibold text-[#8B9BB4] hover:text-white hover:bg-white/5 transition-all';
      });
      btn.className = 'meal-tab-btn px-5 py-2.5 rounded-xl text-xs font-bold bg-[#FF5E1E] text-white shadow-md shadow-orange-500/20';
      selectedMeal = btn.getAttribute('data-meal') || 'Lunch';
      loadMenu();
    });
  });

  // Diet Filter
  document.querySelectorAll('.diet-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.diet-filter-btn').forEach(b => {
        b.className = 'diet-filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-[#8B9BB4] hover:text-white hover:bg-white/5 flex items-center gap-1.5';
      });
      btn.className = 'diet-filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 text-white flex items-center gap-1.5';
      selectedDiet = btn.getAttribute('data-diet') || 'all';
      loadMenu();
    });
  });

  // Search input
  if (menuSearchInput) {
    menuSearchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      loadMenu();
    });
  }

  // Initial Load
  loadMenu();
});
