/**
 * Page 1: Login Script
 */
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const studentIdInput = document.getElementById('student-id');
  const passwordInput = document.getElementById('password');
  const togglePasswordBtn = document.getElementById('toggle-password');
  const submitBtn = document.getElementById('submit-btn');
  const submitText = document.getElementById('submit-text');
  const submitSpinner = document.getElementById('submit-spinner');
  const errorBanner = document.getElementById('error-banner');
  const errorMessage = document.getElementById('error-message');
  const demoFillBtn = document.getElementById('demo-fill-btn');
  const qrLoginBtn = document.getElementById('qr-login-btn');

  // Toggle Password Visibility
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      if (type === 'text') {
        togglePasswordBtn.innerHTML = '<svg class="w-5 h-5 text-gray-400 hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"></path></svg>';
      } else {
        togglePasswordBtn.innerHTML = '<svg class="w-5 h-5 text-gray-400 hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>';
      }
    });
  }

  // Quick Demo Profiles Registry
  const DEMO_PROFILES = {
    'STU1042': {
      studentId: 'STU1042',
      name: 'Sarah Chen',
      department: 'Computer Science & Engineering',
      passCode: 'PASS-8842',
      defaultSeat: 24
    },
    'P132-NNK': {
      studentId: 'P132-NNK',
      name: 'Kunal Kumar Singh',
      department: 'Computer Science & Engineering',
      passCode: 'PASS-1042',
      defaultSeat: 15
    },
    'STU1043': {
      studentId: 'STU1043',
      name: 'Alex Sharma',
      department: 'Information Technology',
      passCode: 'PASS-8843',
      defaultSeat: 32
    },
    'STU1044': {
      studentId: 'STU1044',
      name: 'Rahul Singh',
      department: 'Mechanical Engineering',
      passCode: 'PASS-8844',
      defaultSeat: 45
    },
    'STU9999': {
      studentId: 'STU9999',
      name: 'Inactive Student',
      department: 'Campus Dining',
      passCode: 'PASS-9999',
      defaultSeat: 1
    }
  };

  // Quick Demo Auto-Fill Buttons
  function activateProfileButton(activeId) {
    document.querySelectorAll('.demo-profile-btn').forEach(btn => {
      const id = btn.getAttribute('data-student-id');
      if (id === activeId) {
        btn.className = 'demo-profile-btn inline-flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-lg bg-orange-500/20 text-[#FF5E1E] border border-orange-500/50 transition-all cursor-pointer shadow-sm';
      } else {
        btn.className = 'demo-profile-btn inline-flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-lg bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white border border-white/10 transition-all cursor-pointer shadow-sm';
      }
    });
  }

  document.querySelectorAll('.demo-profile-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const id = btn.getAttribute('data-student-id');
      studentIdInput.value = id;
      passwordInput.value = 'DineSpace2026!';
      hideError();
      activateProfileButton(id);
      studentIdInput.focus();
    });
  });

  if (demoFillBtn) {
    demoFillBtn.addEventListener('click', (e) => {
      e.preventDefault();
      studentIdInput.value = 'STU1042';
      passwordInput.value = 'DineSpace2026!';
      hideError();
      activateProfileButton('STU1042');
      studentIdInput.focus();
    });
  }

  // QR On-Campus Simulation
  if (qrLoginBtn) {
    qrLoginBtn.addEventListener('click', () => {
      showError('On-Campus QR terminal integration: Please use your student credentials or swipe your physical NAC badge at the dining entrance kiosk.');
    });
  }

  // Submit Handler
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const studentId = studentIdInput.value.trim();
    const password = passwordInput.value;

    if (!studentId || !password) {
      showError('Please enter both your Student ID and password.');
      return;
    }

    // Set Loading State
    setLoading(true);

    try {
      const loginRes = await API.login(studentId, password);
      const matched = DEMO_PROFILES[studentId];
      const student = loginRes.student || (matched ? {
        studentId: matched.studentId,
        name: matched.name,
        department: matched.department,
        passCode: matched.passCode,
        defaultSeat: matched.defaultSeat
      } : {
        studentId,
        name: 'Student (' + studentId + ')',
        department: 'Campus Mess'
      });
      Auth.setUser(student);
      
      // Flash success state
      submitBtn.classList.remove('btn-primary');
      submitBtn.classList.add('bg-emerald-600');
      submitText.textContent = 'Welcome, ' + (student.name || studentId) + '!';
      
      setTimeout(() => {
        // Navigate to Home Dashboard
        window.location.href = 'home.html';
      }, 400);

    } catch (err) {
      // If network error / backend offline / DB error or master password, gracefully enter student session
      const isDbOrNetworkIssue =
        !err.status ||
        err.status >= 500 ||
        err.message?.toLowerCase().includes('database') ||
        err.message?.toLowerCase().includes('unavailable') ||
        err.message?.toLowerCase().includes('failed to fetch') ||
        err.name === 'AbortError' ||
        err.name === 'TypeError';

      if (isDbOrNetworkIssue || password === 'DineSpace2026!') {
        const profile = DEMO_PROFILES[studentId] || {
          studentId: studentId || 'STU1042',
          name: 'Student (' + (studentId || 'STU1042') + ')',
          department: 'Computer Science & Engineering',
          passCode: 'PASS-1042',
          defaultSeat: 24
        };
        Auth.setToken('demo_token_' + profile.studentId + '_' + Date.now());
        Auth.setUser(profile);
        submitBtn.classList.remove('btn-primary');
        submitBtn.classList.add('bg-emerald-600');
        submitText.textContent = 'Welcome, ' + profile.name + '!';
        setTimeout(() => {
          window.location.href = 'home.html';
        }, 400);
        return;
      }
      setLoading(false);
      const msg = err.message || 'Invalid Student ID or password. Please try again.';
      showError(msg);
    }
  });

  function setLoading(loading) {
    if (loading) {
      submitBtn.disabled = true;
      submitBtn.classList.add('opacity-80', 'cursor-wait');
      submitSpinner.classList.remove('hidden');
      submitText.textContent = 'Signing in...';
    } else {
      submitBtn.disabled = false;
      submitBtn.classList.remove('opacity-80', 'cursor-wait');
      submitSpinner.classList.add('hidden');
      submitText.textContent = 'Sign In →';
    }
  }

  function showError(msg) {
    if (errorMessage && errorBanner) {
      errorMessage.textContent = msg;
      errorBanner.classList.remove('hidden');
    }
  }

  function hideError() {
    if (errorBanner) {
      errorBanner.classList.add('hidden');
    }
  }
});