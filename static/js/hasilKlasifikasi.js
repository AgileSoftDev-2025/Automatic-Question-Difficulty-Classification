/**
 * Enhanced Classification Results JavaScript - Complete with All Features + Dark Mode
 * Handles navigation, classification updates, charts, mobile interactions, and animations
 */

(function() {
  'use strict';

  // ==================== CONFIGURATION ====================
  const CONFIG = {
    animationDuration: 300,
    toastDuration: 3000,
    scrollOffset: 100,
    debounceDelay: 300,
    apiEndpoints: {
      update: '/klasifikasi/update/{id}/',
      details: '/klasifikasi/question/{classificationId}/{questionId}/',
      stats: '/klasifikasi/api/stats/'
    }
  };

  // Category colors - matching HTML styles
  const CATEGORY_COLORS = {
    'C1': { bg: '#10b981', light: '#d1fae5', border: '#059669' },
    'C2': { bg: '#3b82f6', light: '#dbeafe', border: '#2563eb' },
    'C3': { bg: '#f59e0b', light: '#fef3c7', border: '#d97706' },
    'C4': { bg: '#f97316', light: '#fed7aa', border: '#ea580c' },
    'C5': { bg: '#ef4444', light: '#fecaca', border: '#dc2626' },
    'C6': { bg: '#a855f7', light: '#e9d5ff', border: '#9333ea' }
  };

  // Category gradient classes for visual feedback
  const GRADIENT_CLASSES = {
    'C1': ['from-green-600', 'to-green-700'],
    'C2': ['from-blue-600', 'to-blue-700'],
    'C3': ['from-amber-600', 'to-amber-700'],
    'C4': ['from-orange-600', 'to-orange-700'],
    'C5': ['from-red-600', 'to-red-700'],
    'C6': ['from-purple-600', 'to-purple-700']
  };

  // ==================== STATE MANAGEMENT ====================
  const state = {
    currentQuestionIndex: 0,
    totalQuestions: 0,
    classificationId: null,
    pendingChanges: new Map(),
    charts: {
      distribution: null,
      type: null
    },
    isProcessing: false,
    isDarkMode: false
  };

  // ==================== DOM ELEMENTS ====================
  let elements = {};

  // ==================== INITIALIZATION ====================
  function init() {
    cacheElements();
    
    if (elements.questions.length === 0) {
      console.warn('No questions found on page');
      return;
    }

    state.totalQuestions = elements.questions.length;
    state.classificationId = getClassificationId();
    state.isDarkMode = document.documentElement.classList.contains('dark');

    setupEventListeners();
    initializeCharts();
    updateOverviewData();
    highlightNavigationByLevel();
    setActiveQuestion(0);
    setupResponsiveFeatures();
    addSmoothScrolling();
    setupDarkModeListener();

    console.log('✓ Classification page initialized with', state.totalQuestions, 'questions');
  }

  // ==================== CACHE DOM ELEMENTS ====================
  function cacheElements() {
    elements = {
      // Navigation
      navItems: document.querySelectorAll('#question-nav .nav-item'),
      prevBtn: document.getElementById('prev-question'),
      nextBtn: document.getElementById('next-question'),
      questionCounter: document.getElementById('question-counter'),
      
      // Questions
      questions: document.querySelectorAll('#questions-list article'),
      selects: document.querySelectorAll('.change-select'),
      
      // Tabs
      tabLinks: document.querySelectorAll('.tab-link'),
      tabDetail: document.getElementById('tab-detail'),
      tabOverview: document.getElementById('tab-overview'),
      
      // Mobile
      mobileMenuToggle: document.getElementById('mobile-menu-toggle'),
      closeSidebar: document.getElementById('close-sidebar'),
      sidebar: document.getElementById('sidebar'),
      
      // Charts
      distributionCanvas: document.getElementById('distributionChart'),
      typeCanvas: document.getElementById('typeChart'),
      chartLegend: document.getElementById('chart-legend'),
      
      // UI
      toastContainer: document.getElementById('toast-container'),
      loadingOverlay: document.getElementById('loading-overlay'),
      downloadBtn: document.getElementById('download-btn'),
      exportBtn: document.getElementById('export-btn'),
      darkModeToggle: document.getElementById('dark-mode-toggle')
    };
  }

  // ==================== DARK MODE ====================
  function setupDarkModeListener() {
    if (elements.darkModeToggle) {
      elements.darkModeToggle.addEventListener('click', () => {
        setTimeout(() => {
          state.isDarkMode = document.documentElement.classList.contains('dark');
          updateChartsForDarkMode();
        }, 100);
      });
    }
  }

  function updateChartsForDarkMode() {
    const textColor = state.isDarkMode ? '#e5e7eb' : '#374151';
    const gridColor = state.isDarkMode ? 'rgba(75, 85, 99, 0.3)' : 'rgba(0, 0, 0, 0.05)';

    if (state.charts.distribution) {
      state.charts.distribution.options.scales.y.grid.color = gridColor;
      state.charts.distribution.options.scales.y.ticks.color = textColor;
      state.charts.distribution.options.scales.x.ticks.color = textColor;
      state.charts.distribution.update('none');
    }

    if (state.charts.type) {
      state.charts.type.update('none');
    }
  }

  // ==================== EVENT LISTENERS ====================
  function setupEventListeners() {
    // Navigation buttons
    elements.navItems.forEach(btn => {
      btn.addEventListener('click', handleNavClick);
    });

    // Previous/Next
    elements.prevBtn?.addEventListener('click', () => navigateQuestion(-1));
    elements.nextBtn?.addEventListener('click', () => navigateQuestion(1));

    // Classification changes
    elements.selects.forEach(select => {
      select.addEventListener('change', handleClassificationChange);
    });

    // Save buttons (delegated)
    document.addEventListener('click', (e) => {
      if (e.target.closest('.save-change-btn')) {
        handleSaveChange(e.target.closest('.save-change-btn'));
      }
    });

    // Tabs
    elements.tabLinks.forEach(link => {
      link.addEventListener('click', handleTabClick);
    });

    // Mobile menu
    elements.mobileMenuToggle?.addEventListener('click', toggleMobileSidebar);
    elements.closeSidebar?.addEventListener('click', closeMobileSidebar);

    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardNav);

    // Scroll tracking with throttling
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(updateActiveNavOnScroll, 100);
    }, { passive: true });

    // Responsive resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(handleResize, 250);
    });

    // Click outside sidebar (mobile)
    document.addEventListener('click', handleClickOutside);
  }

  // ==================== SMOOTH SCROLLING ====================
  function addSmoothScrolling() {
    document.documentElement.style.scrollBehavior = 'smooth';
  }

  // ==================== RESPONSIVE FEATURES ====================
  function setupResponsiveFeatures() {
    // Touch swipe for mobile navigation
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, { passive: true });

    function handleSwipe() {
      const swipeThreshold = 100;
      if (touchEndX < touchStartX - swipeThreshold) {
        navigateQuestion(1);
      } else if (touchEndX > touchStartX + swipeThreshold) {
        navigateQuestion(-1);
      }
    }
  }

  function handleResize() {
    // Redraw charts on resize
    if (state.charts.distribution) {
      state.charts.distribution.resize();
    }
    if (state.charts.type) {
      state.charts.type.resize();
    }

    // Close mobile sidebar on desktop
    if (window.innerWidth >= 1024 && elements.sidebar) {
      elements.sidebar.classList.remove('show');
    }
  }

  function handleClickOutside(e) {
    if (window.innerWidth < 1024 && elements.sidebar && elements.sidebar.classList.contains('show')) {
      if (!elements.sidebar.contains(e.target) && 
          !elements.mobileMenuToggle?.contains(e.target)) {
        closeMobileSidebar();
      }
    }
  }

  // ==================== NAVIGATION ====================
  function handleNavClick(e) {
    const btn = e.currentTarget;
    const index = parseInt(btn.getAttribute('data-index'));
    setActiveQuestion(index);
    closeMobileSidebar();
  }

  function navigateQuestion(direction) {
    const newIndex = state.currentQuestionIndex + direction;
    if (newIndex >= 0 && newIndex < state.totalQuestions) {
      setActiveQuestion(newIndex);
    }
  }

  function setActiveQuestion(index) {
    if (index < 0 || index >= state.totalQuestions) return;

    state.currentQuestionIndex = index;

    // Update navigation buttons with animation
    elements.navItems.forEach((btn, i) => {
      if (i === index) {
        btn.classList.remove('bg-blue-50', 'text-blue-700', 'dark:bg-gray-700', 'dark:text-blue-300');
        btn.classList.add('bg-blue-600', 'text-white', 'active', 'ring-2', 'ring-blue-300', 'scale-105');
      } else {
        btn.classList.remove('bg-blue-600', 'text-white', 'active', 'ring-2', 'ring-blue-300', 'scale-105');
        btn.classList.add('bg-blue-50', 'text-blue-700', 'dark:bg-gray-700', 'dark:text-blue-300');
      }
    });

    updateNavigationButtons(index);
    updateQuestionCounter(index);
    scrollToQuestion(index);
  }

  function scrollToQuestion(index) {
    const targetQuestion = elements.questions[index];
    if (!targetQuestion) return;

    const isMobile = window.innerWidth < 768;
    const offset = isMobile ? 80 : CONFIG.scrollOffset;
    const elementPosition = targetQuestion.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });

    // Flash effect with animation
    targetQuestion.classList.add('ring-4', 'ring-blue-300', 'shadow-2xl');
    setTimeout(() => {
      targetQuestion.classList.remove('ring-4', 'ring-blue-300', 'shadow-2xl');
    }, 1000);
  }

  function updateNavigationButtons(index) {
    if (elements.prevBtn) {
      elements.prevBtn.disabled = index === 0;
      elements.prevBtn.classList.toggle('opacity-50', index === 0);
      elements.prevBtn.classList.toggle('cursor-not-allowed', index === 0);
    }
    
    if (elements.nextBtn) {
      const isLast = index === state.totalQuestions - 1;
      elements.nextBtn.disabled = isLast;
      elements.nextBtn.classList.toggle('opacity-50', isLast);
      elements.nextBtn.classList.toggle('cursor-not-allowed', isLast);
    }
  }

  function updateQuestionCounter(index) {
    if (elements.questionCounter) {
      elements.questionCounter.textContent = `Question ${index + 1} of ${state.totalQuestions}`;
    }
  }

  function updateActiveNavOnScroll() {
    const scrollPosition = window.scrollY + window.innerHeight / 3;
    
    let currentIndex = 0;
    elements.questions.forEach((question, index) => {
      const rect = question.getBoundingClientRect();
      const top = rect.top + window.pageYOffset;
      
      if (scrollPosition >= top) {
        currentIndex = index;
      }
    });

    if (currentIndex !== state.currentQuestionIndex) {
      state.currentQuestionIndex = currentIndex;
      
      elements.navItems.forEach((btn, i) => {
        if (i === currentIndex) {
          btn.classList.remove('bg-blue-50', 'text-blue-700', 'dark:bg-gray-700', 'dark:text-blue-300');
          btn.classList.add('bg-blue-600', 'text-white', 'active');
        } else {
          btn.classList.remove('bg-blue-600', 'text-white', 'active');
          btn.classList.add('bg-blue-50', 'text-blue-700', 'dark:bg-gray-700', 'dark:text-blue-300');
        }
      });

      updateNavigationButtons(currentIndex);
      updateQuestionCounter(currentIndex);
    }
  }

  function highlightNavigationByLevel() {
    elements.navItems.forEach(btn => {
      const level = btn.getAttribute('data-level');
      if (level && CATEGORY_COLORS[level]) {
        btn.style.borderLeft = `4px solid ${CATEGORY_COLORS[level].bg}`;
      }
    });
  }

  // ==================== CLASSIFICATION CHANGES ====================
  function handleClassificationChange(e) {
    const select = e.target;
    const newLevel = select.value;
    const questionIndex = select.getAttribute('data-question-index');
    const originalLevel = select.getAttribute('data-original-level');
    const article = select.closest('article');
    
    if (!newLevel || newLevel === originalLevel) {
      hideSaveButton(article);
      state.pendingChanges.delete(questionIndex);
      return;
    }

    // Store pending change
    state.pendingChanges.set(questionIndex, {
      newLevel,
      originalLevel,
      article
    });

    // Show save button with animation
    showSaveButton(article, questionIndex);

    // Visual feedback
    updateVisualFeedback(article, newLevel);
  }

  function showSaveButton(article, questionIndex) {
    const saveBtn = article.querySelector('.save-change-btn');
    if (saveBtn) {
      saveBtn.classList.remove('hidden');
      saveBtn.setAttribute('data-question-index', questionIndex);
      
      // Add pulse animation
      saveBtn.classList.add('animate-pulse');
      setTimeout(() => saveBtn.classList.remove('animate-pulse'), 1000);
    }
  }

  function hideSaveButton(article) {
    const saveBtn = article.querySelector('.save-change-btn');
    if (saveBtn) {
      saveBtn.classList.add('hidden');
    }
  }

  function handleSaveChange(button) {
    if (state.isProcessing) {
      showToast('⏳ Please wait for the current operation to complete', 'warning');
      return;
    }

    const questionIndex = button.getAttribute('data-question-index');
    const change = state.pendingChanges.get(questionIndex);
    
    if (!change) return;

    saveClassificationChange(
      parseInt(questionIndex) + 1,
      change.newLevel,
      change.originalLevel,
      change.article
    );
  }

  async function saveClassificationChange(questionNumber, newLevel, originalLevel, article) {
    state.isProcessing = true;
    showLoading(true);

    try {
      const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      const response = await fetch(`/klasifikasi/update/${state.classificationId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          question_number: questionNumber,
          category: newLevel
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Update UI with animation
        updateQuestionLevel(article, newLevel);
        updateNavigationLevel(questionNumber - 1, newLevel);
        
        // Update original level
        const select = article.querySelector('.change-select');
        if (select) {
          select.setAttribute('data-original-level', newLevel);
        }
        
        // Clear pending change
        const questionIndex = (questionNumber - 1).toString();
        state.pendingChanges.delete(questionIndex);
        hideSaveButton(article);
        
        // Refresh overview
        updateOverviewData();
        updateCharts();
        
        showToast('✓ Classification updated successfully!', 'success');
      } else {
        throw new Error(data.error || 'Failed to update');
      }
    } catch (error) {
      console.error('Error updating:', error);
      showToast('✗ ' + (error.message || 'Failed to update classification'), 'error');
      
      // Revert select
      const select = article.querySelector('.change-select');
      if (select) {
        select.value = originalLevel;
      }
    } finally {
      state.isProcessing = false;
      showLoading(false);
    }
  }

  function updateQuestionLevel(article, newLevel) {
    const labelEl = article.querySelector('.current-label');
    const badgeEl = article.querySelector('.classification-badge');
    
    if (labelEl) {
      labelEl.textContent = newLevel;
      // Add flash animation
      labelEl.classList.add('animate-pulse');
      setTimeout(() => labelEl.classList.remove('animate-pulse'), 500);
    }
    
    if (badgeEl) {
      badgeEl.className = 'classification-badge px-3 py-1 rounded-full text-xs sm:text-sm font-semibold category-' + newLevel.toLowerCase();
      badgeEl.textContent = newLevel;
    }
  }

  function updateNavigationLevel(questionIndex, newLevel) {
    const navBtn = elements.navItems[questionIndex];
    if (navBtn) {
      navBtn.setAttribute('data-level', newLevel);
      navBtn.style.borderLeft = `4px solid ${CATEGORY_COLORS[newLevel].bg}`;
    }
  }

  function updateVisualFeedback(article, newLevel) {
    const box = article.querySelector('.classification-box');
    if (!box) return;

    // Remove all gradient classes
    const allGradients = Object.values(GRADIENT_CLASSES).flat();
    allGradients.forEach(cls => box.classList.remove(cls));

    // Add new gradient classes
    if (GRADIENT_CLASSES[newLevel]) {
      box.classList.add(...GRADIENT_CLASSES[newLevel]);
    }
  }

  // ==================== CHARTS ====================
  function initializeCharts() {
    if (!elements.distributionCanvas || !elements.typeCanvas) return;

    const textColor = state.isDarkMode ? '#e5e7eb' : '#374151';
    const gridColor = state.isDarkMode ? 'rgba(75, 85, 99, 0.3)' : 'rgba(0, 0, 0, 0.05)';

    // Bar Chart
    const ctxBar = elements.distributionCanvas.getContext('2d');
    state.charts.distribution = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
        datasets: [{
          label: 'Questions',
          data: [0, 0, 0, 0, 0, 0],
          backgroundColor: Object.values(CATEGORY_COLORS).map(c => c.bg),
          borderColor: Object.values(CATEGORY_COLORS).map(c => c.border),
          borderWidth: 2,
          borderRadius: 8,
          hoverBackgroundColor: Object.values(CATEGORY_COLORS).map(c => c.border)
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: state.isDarkMode ? 'rgba(31, 41, 55, 0.95)' : 'rgba(0, 0, 0, 0.9)',
            padding: 12,
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 13 },
            borderColor: state.isDarkMode ? '#4b5563' : 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            callbacks: {
              title: (ctx) => ctx[0].label + ' - ' + getCategoryName(ctx[0].label),
              label: (ctx) => 'Questions: ' + ctx.parsed.y
            }
          }
        },
        scales: {
          y: { 
            beginAtZero: true, 
            ticks: { 
              stepSize: 1,
              color: textColor
            },
            grid: { color: gridColor }
          },
          x: { 
            grid: { display: false },
            ticks: { 
              font: { weight: 'bold' },
              color: textColor
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutQuart'
        }
      }
    });

    // Doughnut Chart with Percentages
    const ctxDoughnut = elements.typeCanvas.getContext('2d');
    
    // Check if ChartDataLabels plugin is available
    const doughnutPlugins = [];
    if (typeof ChartDataLabels !== 'undefined') {
      doughnutPlugins.push(ChartDataLabels);
    }
    
    state.charts.type = new Chart(ctxDoughnut, {
      type: 'doughnut',
      data: {
        labels: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
        datasets: [{
          data: [0, 0, 0, 0, 0, 0],
          backgroundColor: Object.values(CATEGORY_COLORS).map(c => c.bg),
          borderColor: state.isDarkMode ? '#1f2937' : '#ffffff',
          borderWidth: 3,
          hoverOffset: 12,
          hoverBorderWidth: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: state.isDarkMode ? 'rgba(31, 41, 55, 0.95)' : 'rgba(0, 0, 0, 0.9)',
            padding: 12,
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 13 },
            borderColor: state.isDarkMode ? '#4b5563' : 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            callbacks: {
              title: (ctx) => ctx[0].label + ' - ' + getCategoryName(ctx[0].label),
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                return ['Questions: ' + ctx.parsed, 'Percentage: ' + pct + '%'];
              }
            }
          },
          datalabels: typeof ChartDataLabels !== 'undefined' ? {
            color: '#ffffff',
            font: {
              weight: 'bold',
              size: 14
            },
            formatter: function(value, context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
              return percentage > 3 ? percentage + '%' : ''; // Only show if > 3%
            }
          } : undefined
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutQuart'
        }
      },
      plugins: doughnutPlugins
    });
  }

  function updateCharts() {
    const counts = getCategoryCounts();
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    if (state.charts.distribution) {
      state.charts.distribution.data.datasets[0].data = [
        counts.C1, counts.C2, counts.C3, counts.C4, counts.C5, counts.C6
      ];
      state.charts.distribution.update('active');
    }

    if (state.charts.type) {
      state.charts.type.data.datasets[0].data = [
        counts.C1, counts.C2, counts.C3, counts.C4, counts.C5, counts.C6
      ];
      // Update border color based on dark mode
      state.charts.type.data.datasets[0].borderColor = state.isDarkMode ? '#1f2937' : '#ffffff';
      state.charts.type.update('active');
    }

    updateChartLegend(counts, total);
  }

  function updateChartLegend(counts, total) {
    if (!elements.chartLegend) return;

    const categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'];
    const html = categories.map(cat => {
      const count = counts[cat] || 0;
      const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
      
      return `
        <div class="legend-item">
          <div class="flex items-center">
            <div class="legend-color" style="background-color: ${CATEGORY_COLORS[cat].bg};"></div>
            <span class="legend-label">${cat} - ${getCategoryName(cat)}</span>
          </div>
          <span class="legend-percentage">${pct}%</span>
        </div>
      `;
    }).join('');

    elements.chartLegend.innerHTML = html;
  }

  function getCategoryCounts() {
    const counts = { C1: 0, C2: 0, C3: 0, C4: 0, C5: 0, C6: 0 };
    
    elements.questions.forEach(article => {
      const badge = article.querySelector('.classification-badge');
      if (badge) {
        const level = badge.textContent.trim();
        if (counts.hasOwnProperty(level)) {
          counts[level]++;
        }
      }
    });

    return counts;
  }

  function getCategoryName(code) {
    const names = {
      'C1': 'Remember', 'C2': 'Understand', 'C3': 'Apply',
      'C4': 'Analyze', 'C5': 'Evaluate', 'C6': 'Create'
    };
    return names[code] || code;
  }

  // ==================== OVERVIEW DATA ====================
  function updateOverviewData() {
    const counts = getCategoryCounts();
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    Object.keys(counts).forEach(level => {
      const countEl = document.getElementById(`count-${level}`);
      const pctEl = document.getElementById(`percentage-${level}`);
      
      if (countEl) countEl.textContent = counts[level];
      if (pctEl) {
        const pct = total > 0 ? ((counts[level] / total) * 100).toFixed(1) : 0;
        pctEl.textContent = pct + '%';
      }
    });

    updateSummaryStats(counts);
  }

  function updateSummaryStats(counts) {
    const entries = Object.entries(counts);
    const highest = entries.reduce((a, b) => b[1] > a[1] ? b : a, ['', 0]);
    
    const highestEl = document.getElementById('highest-category');
    if (highestEl) {
      highestEl.textContent = highest[1] > 0 ? `${highest[0]} (${highest[1]})` : '-';
    }

    const lowerOrder = (counts.C1 || 0) + (counts.C2 || 0);
    const higherOrder = (counts.C3 || 0) + (counts.C4 || 0) + (counts.C5 || 0) + (counts.C6 || 0);

    const lowerEl = document.getElementById('lower-order');
    const higherEl = document.getElementById('higher-order');
    
    if (lowerEl) lowerEl.textContent = lowerOrder;
    if (higherEl) higherEl.textContent = higherOrder;
  }

  // ==================== TABS ====================
  function handleTabClick(e) {
    e.preventDefault();
    const tab = e.currentTarget.getAttribute('data-tab');

    elements.tabLinks.forEach(link => {
      link.classList.remove('text-blue-600', 'dark:text-blue-400', 'font-semibold', 'bg-blue-50', 'dark:bg-gray-700', 'active');
      link.classList.add('text-gray-600', 'dark:text-gray-300');
    });

    e.currentTarget.classList.remove('text-gray-600', 'dark:text-gray-300');
    e.currentTarget.classList.add('text-blue-600', 'dark:text-blue-400', 'font-semibold', 'bg-blue-50', 'dark:bg-gray-700', 'active');

    if (tab === 'detail') {
      elements.tabDetail?.classList.remove('hidden');
      elements.tabOverview?.classList.add('hidden');
    } else {
      elements.tabDetail?.classList.add('hidden');
      elements.tabOverview?.classList.remove('hidden');
      updateOverviewData();
      updateCharts();
      setTimeout(() => {
        if (state.charts.distribution) state.charts.distribution.resize();
        if (state.charts.type) state.charts.type.resize();
      }, 100);
    }
  }

  // ==================== MOBILE SIDEBAR ====================
  function toggleMobileSidebar() {
    elements.sidebar?.classList.toggle('show');
  }

  function closeMobileSidebar() {
    elements.sidebar?.classList.remove('show');
  }

  // ==================== KEYBOARD NAVIGATION ====================
  function handleKeyboardNav(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
      return;
    }

    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      e.preventDefault();
      navigateQuestion(1);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      e.preventDefault();
      navigateQuestion(-1);
    } else if (e.key === 'Escape' && window.innerWidth < 1024) {
      closeMobileSidebar();
    }
  }

  // ==================== UI HELPERS ====================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast px-6 py-4 rounded-lg shadow-lg text-white flex items-center gap-3 ${
      type === 'success' ? 'bg-green-500' :
      type === 'error' ? 'bg-red-500' :
      type === 'warning' ? 'bg-yellow-500' :
      'bg-blue-500'
    }`;
    
    const icon = {
      success: 'check-circle-fill',
      error: 'x-circle-fill',
      warning: 'exclamation-triangle-fill',
      info: 'info-circle-fill'
    }[type] || 'info-circle-fill';
    
    toast.innerHTML = `
      <i class="bi bi-${icon} text-xl"></i>
      <span>${message}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, CONFIG.toastDuration);
  }

  function showLoading(show) {
    if (elements.loadingOverlay) {
      elements.loadingOverlay.classList.toggle('hidden', !show);
    }
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function getClassificationId() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 2] || '1';
  }

  // ==================== INITIALIZE ON DOM READY ====================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();