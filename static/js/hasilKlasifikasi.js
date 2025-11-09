/**
 * Enhanced Classification Results Page JavaScript
 * Handles navigation, classification changes, charts, and user interactions
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    animationDuration: 300,
    toastDuration: 3000,
    scrollOffset: 100,
    debounceDelay: 300
  };

  // Category color mapping for charts and UI
  const CATEGORY_COLORS = {
    'C1': { 
      bg: '#10b981', // green-500
      light: '#d1fae5',
      border: '#059669'
    },
    'C2': { 
      bg: '#3b82f6', // blue-500
      light: '#dbeafe',
      border: '#2563eb'
    },
    'C3': { 
      bg: '#f59e0b', // amber-500
      light: '#fef3c7',
      border: '#d97706'
    },
    'C4': { 
      bg: '#f97316', // orange-500
      light: '#fed7aa',
      border: '#ea580c'
    },
    'C5': { 
      bg: '#ef4444', // red-500
      light: '#fecaca',
      border: '#dc2626'
    },
    'C6': { 
      bg: '#a855f7', // purple-500
      light: '#e9d5ff',
      border: '#9333ea'
    }
  };

  // DOM elements
  let elements = {};
  
  // Chart instances
  let distributionChart = null;
  let typeChart = null;

  /**
   * Initialize the application
   */
  function init() {
    cacheElements();
    setupEventListeners();
    initializeCharts();
    updateOverviewCounts();
    updateCharts();
    highlightNavigationByLevel();
    
    // Set first question as active by default
    if (elements.navItems.length > 0) {
      setActiveQuestion(0);
    }

    console.log('Classification page initialized');
  }

  /**
   * Cache frequently accessed DOM elements
   */
  function cacheElements() {
    elements = {
      navItems: document.querySelectorAll('#question-nav .nav-item'),
      questions: document.querySelectorAll('#questions-list article'),
      selects: document.querySelectorAll('.change-select'),
      prevBtn: document.getElementById('prev-question'),
      nextBtn: document.getElementById('next-question'),
      questionCounter: document.getElementById('question-counter'),
      downloadBtn: document.getElementById('download-btn'),
      exportBtn: document.getElementById('export-btn'),
      tabLinks: document.querySelectorAll('.tab-link'),
      tabContents: document.querySelectorAll('.tab-content'),
      mobileMenuToggle: document.getElementById('mobile-menu-toggle'),
      closeSidebar: document.getElementById('close-sidebar'),
      sidebar: document.getElementById('sidebar'),
      toastContainer: document.getElementById('toast-container'),
      loadingOverlay: document.getElementById('loading-overlay'),
      distributionCanvas: document.getElementById('distributionChart'),
      typeCanvas: document.getElementById('typeChart'),
      chartLegend: document.getElementById('chart-legend')
    };
  }

  /**
   * Setup all event listeners
   */
  function setupEventListeners() {
    // Navigation buttons
    elements.navItems.forEach(btn => {
      btn.addEventListener('click', handleNavClick);
    });

    // Previous/Next buttons
    if (elements.prevBtn) {
      elements.prevBtn.addEventListener('click', () => navigateQuestion(-1));
    }
    
    if (elements.nextBtn) {
      elements.nextBtn.addEventListener('click', () => navigateQuestion(1));
    }

    // Classification select dropdowns
    elements.selects.forEach(select => {
      select.addEventListener('change', handleClassificationChange);
    });

    // Download button
    if (elements.downloadBtn) {
      elements.downloadBtn.addEventListener('click', handleDownload);
    }

    // Export button
    if (elements.exportBtn) {
      elements.exportBtn.addEventListener('click', handleExport);
    }

    // Tab navigation
    elements.tabLinks.forEach(link => {
      link.addEventListener('click', handleTabClick);
    });

    // Mobile menu
    if (elements.mobileMenuToggle) {
      elements.mobileMenuToggle.addEventListener('click', toggleMobileSidebar);
    }

    if (elements.closeSidebar) {
      elements.closeSidebar.addEventListener('click', closeMobileSidebar);
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 1024) {
        if (elements.sidebar && 
            !elements.sidebar.contains(e.target) && 
            elements.mobileMenuToggle &&
            !elements.mobileMenuToggle.contains(e.target) &&
            elements.sidebar.classList.contains('show')) {
          closeMobileSidebar();
        }
      }
    });

    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardNav);

    // Scroll to update active nav
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(updateActiveNavOnScroll, 100);
    });

    // Responsive chart resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (distributionChart) distributionChart.resize();
        if (typeChart) typeChart.resize();
      }, 250);
    });
  }

  /**
   * Initialize Chart.js charts
   */
  function initializeCharts() {
    // Bar Chart - Distribution
    if (elements.distributionCanvas) {
      const ctx = elements.distributionCanvas.getContext('2d');
      distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
          datasets: [{
            label: 'Number of Questions',
            data: [0, 0, 0, 0, 0, 0],
            backgroundColor: [
              CATEGORY_COLORS.C1.bg,
              CATEGORY_COLORS.C2.bg,
              CATEGORY_COLORS.C3.bg,
              CATEGORY_COLORS.C4.bg,
              CATEGORY_COLORS.C5.bg,
              CATEGORY_COLORS.C6.bg
            ],
            borderColor: [
              CATEGORY_COLORS.C1.border,
              CATEGORY_COLORS.C2.border,
              CATEGORY_COLORS.C3.border,
              CATEGORY_COLORS.C4.border,
              CATEGORY_COLORS.C5.border,
              CATEGORY_COLORS.C6.border
            ],
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              padding: 12,
              titleFont: {
                size: 14,
                weight: 'bold'
              },
              bodyFont: {
                size: 13
              },
              callbacks: {
                title: function(context) {
                  return context[0].label + ' - ' + getCategoryName(context[0].label);
                },
                label: function(context) {
                  return 'Questions: ' + context.parsed.y;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                font: {
                  size: 12
                }
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                font: {
                  size: 12,
                  weight: 'bold'
                }
              }
            }
          }
        }
      });
    }

    // Doughnut Chart - Type Distribution
    if (elements.typeCanvas) {
      const ctx = elements.typeCanvas.getContext('2d');
      typeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
          datasets: [{
            data: [0, 0, 0, 0, 0, 0],
            backgroundColor: [
              CATEGORY_COLORS.C1.bg,
              CATEGORY_COLORS.C2.bg,
              CATEGORY_COLORS.C3.bg,
              CATEGORY_COLORS.C4.bg,
              CATEGORY_COLORS.C5.bg,
              CATEGORY_COLORS.C6.bg
            ],
            borderColor: '#ffffff',
            borderWidth: 3,
            hoverOffset: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '65%',
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              padding: 12,
              titleFont: {
                size: 14,
                weight: 'bold'
              },
              bodyFont: {
                size: 13
              },
              callbacks: {
                title: function(context) {
                  return context[0].label + ' - ' + getCategoryName(context[0].label);
                },
                label: function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                  return [
                    'Questions: ' + context.parsed,
                    'Percentage: ' + percentage + '%'
                  ];
                }
              }
            }
          }
        }
      });
    }
  }

  /**
   * Get category full name
   */
  function getCategoryName(code) {
    const names = {
      'C1': 'Remember',
      'C2': 'Understand',
      'C3': 'Apply',
      'C4': 'Analyze',
      'C5': 'Evaluate',
      'C6': 'Create'
    };
    return names[code] || code;
  }

  /**
   * Update charts with current data
   */
  function updateCharts() {
    const counts = getCategoryCounts();
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    // Update bar chart
    if (distributionChart) {
      distributionChart.data.datasets[0].data = [
        counts.C1, counts.C2, counts.C3, counts.C4, counts.C5, counts.C6
      ];
      distributionChart.update('none'); // Update without animation
    }

    // Update doughnut chart
    if (typeChart) {
      typeChart.data.datasets[0].data = [
        counts.C1, counts.C2, counts.C3, counts.C4, counts.C5, counts.C6
      ];
      typeChart.update('none');
    }

    // Update custom legend
    updateChartLegend(counts, total);
  }

  /**
   * Update custom chart legend
   */
  function updateChartLegend(counts, total) {
    if (!elements.chartLegend) return;

    const categories = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'];
    const legendHTML = categories.map(cat => {
      const count = counts[cat] || 0;
      const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
      
      return `
        <div class="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-100 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-4 h-4 rounded-full" style="background-color: ${CATEGORY_COLORS[cat].bg}"></div>
            <span class="text-sm font-medium text-gray-700">${cat} - ${getCategoryName(cat)}</span>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-gray-800">${count}</div>
            <div class="text-xs text-gray-500">${percentage}%</div>
          </div>
        </div>
      `;
    }).join('');

    elements.chartLegend.innerHTML = legendHTML;
  }

  /**
   * Get category counts from questions
   */
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

  /**
   * Navigate to previous/next question
   */
  function navigateQuestion(direction) {
    const activeIndex = getActiveQuestionIndex();
    const newIndex = activeIndex + direction;
    
    if (newIndex >= 0 && newIndex < elements.questions.length) {
      setActiveQuestion(newIndex);
    }
  }

  /**
   * Get current active question index
   */
  function getActiveQuestionIndex() {
    return Array.from(elements.navItems).findIndex(btn => 
      btn.classList.contains('bg-blue-600') || btn.classList.contains('active')
    );
  }

  /**
   * Handle navigation button click
   */
  function handleNavClick(e) {
    const btn = e.currentTarget;
    const index = parseInt(btn.getAttribute('data-index'));
    setActiveQuestion(index);
    closeMobileSidebar();
  }

  /**
   * Set active question and scroll to it
   */
  function setActiveQuestion(index) {
    if (index < 0 || index >= elements.questions.length) return;

    // Clear all active states
    elements.navItems.forEach(btn => {
      btn.classList.remove('bg-blue-600', 'text-white', 'active');
      btn.classList.add('bg-blue-50', 'text-blue-700');
    });

    // Set active state
    const activeBtn = elements.navItems[index];
    if (activeBtn) {
      activeBtn.classList.remove('bg-blue-50', 'text-blue-700');
      activeBtn.classList.add('bg-blue-600', 'text-white', 'active');
    }

    // Update navigation buttons
    updateNavigationButtons(index);

    // Update counter
    updateQuestionCounter(index);

    // Scroll to question
    const targetQuestion = elements.questions[index];
    if (targetQuestion) {
      const offset = window.innerWidth < 768 ? 80 : CONFIG.scrollOffset;
      const elementPosition = targetQuestion.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });

      // Flash effect
      targetQuestion.classList.add('ring-4', 'ring-blue-200');
      setTimeout(() => {
        targetQuestion.classList.remove('ring-4', 'ring-blue-200');
      }, 800);
    }
  }

  /**
   * Update navigation button states
   */
  function updateNavigationButtons(index) {
    if (elements.prevBtn) {
      elements.prevBtn.disabled = index === 0;
    }
    
    if (elements.nextBtn) {
      elements.nextBtn.disabled = index === elements.questions.length - 1;
    }
  }

  /**
   * Update question counter display
   */
  function updateQuestionCounter(index) {
    if (elements.questionCounter) {
      elements.questionCounter.textContent = `Question ${index + 1} of ${elements.questions.length}`;
    }
  }

  /**
   * Update active navigation based on scroll position
   */
  function updateActiveNavOnScroll() {
    const scrollPosition = window.scrollY + window.innerHeight / 3;
    
    let currentIndex = 0;
    elements.questions.forEach((question, index) => {
      const rect = question.getBoundingClientRect();
      const offset = window.pageYOffset;
      const top = rect.top + offset;
      
      if (scrollPosition >= top) {
        currentIndex = index;
      }
    });

    // Update nav without scrolling
    elements.navItems.forEach((btn, index) => {
      if (index === currentIndex) {
        btn.classList.remove('bg-blue-50', 'text-blue-700');
        btn.classList.add('bg-blue-600', 'text-white', 'active');
      } else {
        btn.classList.remove('bg-blue-600', 'text-white', 'active');
        btn.classList.add('bg-blue-50', 'text-blue-700');
      }
    });

    // Update navigation buttons and counter
    updateNavigationButtons(currentIndex);
    updateQuestionCounter(currentIndex);
  }

  /**
   * Handle classification level change
   */
  function handleClassificationChange(e) {
    const select = e.target;
    const newLevel = select.value;
    const questionIndex = select.getAttribute('data-question-index');
    const originalLevel = select.getAttribute('data-original-level');
    const article = select.closest('article');
    
    if (!newLevel || newLevel === originalLevel) {
      hideSaveButton(article);
      return;
    }

    // Show save button
    showSaveButton(article, () => {
      saveClassificationChange(questionIndex, newLevel, originalLevel, article);
    });

    // Visual feedback
    updateVisualFeedback(article, newLevel);
  }

  /**
   * Show save button for pending changes
   */
  function showSaveButton(article, callback) {
    const saveBtn = article.querySelector('.save-change-btn');
    if (saveBtn) {
      saveBtn.classList.remove('hidden');
      saveBtn.onclick = callback;
    }
  }

  /**
   * Hide save button
   */
  function hideSaveButton(article) {
    const saveBtn = article.querySelector('.save-change-btn');
    if (saveBtn) {
      saveBtn.classList.add('hidden');
      saveBtn.onclick = null;
    }
  }

  /**
   * Save classification change to server
   */
  async function saveClassificationChange(questionIndex, newLevel, originalLevel, article) {
    const questionId = article.getAttribute('data-question-id');
    const classificationId = getClassificationId();
    
    showLoading(true);

    try {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                       getCookie('csrftoken');

      const response = await fetch(`/klasifikasi/update/${classificationId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          question_id: questionId,
          category: newLevel
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Update UI
        updateQuestionLevel(article, newLevel);
        updateNavigationLevel(questionIndex, newLevel);
        updateOverviewCounts();
        updateCharts();
        
        // Update original level
        const select = article.querySelector('.change-select');
        if (select) {
          select.setAttribute('data-original-level', newLevel);
        }
        
        hideSaveButton(article);
        showToast('Classification updated successfully!', 'success');
      } else {
        throw new Error(data.error || 'Failed to update classification');
      }
    } catch (error) {
      console.error('Error updating classification:', error);
      showToast(error.message || 'Failed to update classification', 'error');
      
      // Revert select to original value
      const select = article.querySelector('.change-select');
      if (select) {
        select.value = originalLevel;
      }
    } finally {
      showLoading(false);
    }
  }

  /**
   * Get classification ID from URL or page
   */
  function getClassificationId() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 2] || '1';
  }

  /**
   * Update question level in UI
   */
  function updateQuestionLevel(article, newLevel) {
    const labelEl = article.querySelector('.current-label');
    const badgeEl = article.querySelector('.classification-badge');
    
    if (labelEl) {
      labelEl.textContent = newLevel;
    }
    
    if (badgeEl) {
      // Remove old category classes
      badgeEl.className = badgeEl.className.replace(/category-c\d/gi, '');
      badgeEl.classList.add(`category-${newLevel.toLowerCase()}`);
      badgeEl.textContent = newLevel;
    }
  }

  /**
   * Update navigation button level indicator
   */
  function updateNavigationLevel(questionIndex, newLevel) {
    const navBtn = elements.navItems[questionIndex];
    if (navBtn) {
      navBtn.setAttribute('data-level', newLevel);
    }
  }

  /**
   * Update visual feedback for classification box
   */
  function updateVisualFeedback(article, newLevel) {
    const box = article.querySelector('.classification-box');
    if (!box) return;

    // Remove all color classes
    const colorClasses = ['from-blue-600', 'to-blue-700', 'from-green-600', 'to-green-700',
                         'from-amber-600', 'to-amber-700', 'from-orange-600', 'to-orange-700',
                         'from-red-600', 'to-red-700', 'from-purple-600', 'to-purple-700'];
    
    colorClasses.forEach(cls => box.classList.remove(cls));

    // Add new color based on level
    const colorMap = {
      'C1': ['from-green-600', 'to-green-700'],
      'C2': ['from-blue-600', 'to-blue-700'],
      'C3': ['from-amber-600', 'to-amber-700'],
      'C4': ['from-orange-600', 'to-orange-700'],
      'C5': ['from-red-600', 'to-red-700'],
      'C6': ['from-purple-600', 'to-purple-700']
    };

    if (colorMap[newLevel]) {
      box.classList.add(...colorMap[newLevel]);
    }
  }

  /**
   * Update overview tab counts
   */
  function updateOverviewCounts() {
    const counts = getCategoryCounts();
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    // Update count displays
    Object.keys(counts).forEach(level => {
      const countEl = document.getElementById(`count-${level}`);
      const percentageEl = document.getElementById(`percentage-${level}`);
      
      if (countEl) {
        countEl.textContent = counts[level];
      }
      
      if (percentageEl) {
        const percentage = total > 0 ? ((counts[level] / total) * 100).toFixed(1) : 0;
        percentageEl.textContent = percentage + '%';
      }
    });

    // Update summary statistics
    updateSummaryStats(counts);
  }

  /**
   * Update summary statistics in overview
   */
  function updateSummaryStats(counts) {
    // Find highest category
    const entries = Object.entries(counts);
    const highest = entries.reduce((a, b) => b[1] > a[1] ? b : a, ['', 0]);
    const highestEl = document.getElementById('highest-category');
    if (highestEl) {
      highestEl.textContent = highest[1] > 0 ? `${highest[0]} (${highest[1]})` : '-';
    }

    // Calculate lower order (C1-C2)
    const lowerOrder = (counts.C1 || 0) + (counts.C2 || 0);
    const lowerOrderEl = document.getElementById('lower-order');
    if (lowerOrderEl) {
      lowerOrderEl.textContent = lowerOrder;
    }

    // Calculate higher order (C3-C6)
    const higherOrder = (counts.C3 || 0) + (counts.C4 || 0) + (counts.C5 || 0) + (counts.C6 || 0);
    const higherOrderEl = document.getElementById('higher-order');
    if (higherOrderEl) {
      higherOrderEl.textContent = higherOrder;
    }
  }

  /**
   * Highlight navigation buttons by level
   */
  function highlightNavigationByLevel() {
    elements.navItems.forEach(btn => {
      const level = btn.getAttribute('data-level');
      if (level && CATEGORY_COLORS[level]) {
        btn.style.borderLeft = `3px solid ${CATEGORY_COLORS[level].bg}`;
      }
    });
  }

  /**
   * Handle download button click
   */
  function handleDownload(e) {
    const href = elements.downloadBtn.getAttribute('href');
    
    if (href === '#' || !href) {
      e.preventDefault();
      showToast('PDF file is not available for download', 'info');
      return;
    }

    showToast('Download started...', 'info');
  }

  /**
   * Handle export to Excel
   */
  async function handleExport(e) {
    e.preventDefault();
    
    const classificationId = getClassificationId();
    showLoading(true);
    
    try {
      // Try to use server endpoint if available
      const response = await fetch(`/klasifikasi/export/${classificationId}/`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `classification_${classificationId}_${Date.now()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showToast('Export successful!', 'success');
      } else {
        // Fallback to CSV export
        await exportToCSV();
      }
    } catch (error) {
      console.error('Export error:', error);
      // Fallback to CSV export
      await exportToCSV();
    } finally {
      showLoading(false);
    }
  }

  /**
   * Export to CSV as fallback
   */
  async function exportToCSV() {
    try {
      const exportData = [];
      
      elements.questions.forEach((article, index) => {
        const questionId = article.getAttribute('data-question-id');
        const questionText = article.querySelector('p')?.textContent || '';
        const level = article.querySelector('.classification-badge')?.textContent.trim() || '';
        const confidenceEl = article.querySelector('[class*="confidence"]');
        const confidence = confidenceEl ? confidenceEl.textContent : 'N/A';
        
        exportData.push({
          number: index + 1,
          id: questionId,
          question: questionText,
          level: level,
          levelName: getCategoryName(level),
          confidence: confidence
        });
      });

      const csvContent = createCSV(exportData);
      downloadCSV(csvContent, `classification_results_${Date.now()}.csv`);
      
      showToast('Exported as CSV successfully!', 'success');
    } catch (error) {
      console.error('CSV export error:', error);
      showToast('Export failed. Please try again.', 'error');
    }
  }

  /**
   * Create CSV from data
   */
  function createCSV(data) {
    const headers = ['No', 'Question ID', 'Question Text', 'Level', 'Level Name', 'Confidence'];
    const rows = data.map(item => [
      item.number,
      item.id,
      `"${item.question.replace(/"/g, '""')}"`,
      item.level,
      item.levelName,
      item.confidence
    ]);

    const csvRows = [headers, ...rows];
    return csvRows.map(row => row.join(',')).join('\n');
  }

  /**
   * Download CSV file
   */
  function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Handle tab switching
   */
  function handleTabClick(e) {
    e.preventDefault();
    const clickedTab = e.currentTarget;
    const targetTab = clickedTab.getAttribute('data-tab');

    // Update tab links
    elements.tabLinks.forEach(link => {
      link.classList.remove('text-blue-600', 'font-semibold', 'bg-blue-50', 'active');
      link.classList.add('text-gray-600');
    });

    clickedTab.classList.remove('text-gray-600');
    clickedTab.classList.add('text-blue-600', 'font-semibold', 'bg-blue-50', 'active');

    // Show/hide tab content
    if (targetTab === 'detail') {
      document.getElementById('tab-detail')?.classList.remove('hidden');
      document.getElementById('tab-overview')?.classList.add('hidden');
    } else if (targetTab === 'overview') {
      document.getElementById('tab-detail')?.classList.add('hidden');
      document.getElementById('tab-overview')?.classList.remove('hidden');
      
      // Refresh data when switching to overview
      updateOverviewCounts();
      updateCharts();
      
      // Trigger chart animation
      setTimeout(() => {
        if (distributionChart) distributionChart.update();
        if (typeChart) typeChart.update();
      }, 100);
    }
  }

  /**
   * Toggle mobile sidebar
   */
  function toggleMobileSidebar() {
    if (elements.sidebar) {
      elements.sidebar.classList.toggle('show');
    }
  }

  /**
   * Close mobile sidebar
   */
  function closeMobileSidebar() {
    if (elements.sidebar) {
      elements.sidebar.classList.remove('show');
    }
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyboardNav(e) {
    // Don't interfere if user is typing
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
      return;
    }

    // Arrow keys for navigation
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      e.preventDefault();
      navigateQuestion(1);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      e.preventDefault();
      navigateQuestion(-1);
    }

    // Escape key to close mobile sidebar
    if (e.key === 'Escape' && window.innerWidth < 1024) {
      closeMobileSidebar();
    }
  }

  /**
   * Show toast notification
   */
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast px-6 py-4 rounded-lg shadow-lg text-white ${
      type === 'success' ? 'bg-green-500' :
      type === 'error' ? 'bg-red-500' :
      type === 'warning' ? 'bg-yellow-500' :
      'bg-blue-500'
    }`;
    
    const icon = type === 'success' ? 'check-circle' :
                 type === 'error' ? 'x-circle' :
                 type === 'warning' ? 'exclamation-circle' :
                 'info-circle';
    
    toast.innerHTML = `
      <div class="flex items-center gap-3">
        <i class="bi bi-${icon} text-xl"></i>
        <span>${message}</span>
      </div>
    `;

    elements.toastContainer.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, CONFIG.toastDuration);
  }

  /**
   * Show/hide loading overlay
   */
  function showLoading(show) {
    if (elements.loadingOverlay) {
      if (show) {
        elements.loadingOverlay.classList.remove('hidden');
      } else {
        elements.loadingOverlay.classList.add('hidden');
      }
    }
  }

  /**
   * Get cookie value by name
   */
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

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();