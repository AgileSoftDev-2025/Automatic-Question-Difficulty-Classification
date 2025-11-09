/**
 * Enhanced Classification Results Page JavaScript
 * Handles navigation, classification changes, and user interactions
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

  // Category color mapping
  const CATEGORY_COLORS = {
    'C1': { bg: 'bg-green-600', text: 'text-white', light: 'bg-green-100' },
    'C2': { bg: 'bg-blue-600', text: 'text-white', light: 'bg-blue-100' },
    'C3': { bg: 'bg-amber-600', text: 'text-white', light: 'bg-amber-100' },
    'C4': { bg: 'bg-orange-600', text: 'text-white', light: 'bg-orange-100' },
    'C5': { bg: 'bg-red-600', text: 'text-white', light: 'bg-red-100' },
    'C6': { bg: 'bg-purple-600', text: 'text-white', light: 'bg-purple-100' }
  };

  // DOM elements
  let elements = {};

  /**
   * Initialize the application
   */
  function init() {
    cacheElements();
    setupEventListeners();
    updateOverviewCounts();
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
      downloadBtn: document.getElementById('download-btn'),
      exportBtn: document.getElementById('export-btn'),
      tabLinks: document.querySelectorAll('.tab-link'),
      tabContents: document.querySelectorAll('.tab-content'),
      mobileMenuToggle: document.getElementById('mobile-menu-toggle'),
      closeSidebar: document.getElementById('close-sidebar'),
      sidebar: document.getElementById('sidebar'),
      toastContainer: document.getElementById('toast-container'),
      loadingOverlay: document.getElementById('loading-overlay')
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
  }

  /**
   * Handle navigation button click
   */
  function handleNavClick(e) {
    const btn = e.currentTarget;
    const index = parseInt(btn.getAttribute('data-index'));
    setActiveQuestion(index);
    closeMobileSidebar(); // Close sidebar on mobile after navigation
  }

  /**
   * Set active question and scroll to it
   */
  function setActiveQuestion(index) {
    // Clear all active states
    elements.navItems.forEach(btn => {
      btn.classList.remove('bg-blue-600', 'text-white', 'active');
      btn.classList.add('bg-blue-50', 'text-blue-700');
    });

    // Set active state
    const activeBtn = elements.navItems[index];
    if (!activeBtn) return;

    activeBtn.classList.remove('bg-blue-50', 'text-blue-700');
    activeBtn.classList.add('bg-blue-600', 'text-white', 'active');

    // Scroll to question
    const targetQuestion = document.getElementById(`question-${index}`);
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
        btn.classList.add('bg-blue-600', 'text-white');
      } else {
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-blue-50', 'text-blue-700');
      }
    });
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
    
    showLoading(true);

    try {
      // Get CSRF token
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                       getCookie('csrftoken');

      const response = await fetch(`/classification/update-question/${questionId}/`, {
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
    const box = article.querySelector('.bg-gradient-to-br');
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

    // Update count displays
    Object.keys(counts).forEach(level => {
      const countEl = document.getElementById(`count-${level}`);
      if (countEl) {
        countEl.textContent = counts[level];
      }
    });
  }

  /**
   * Highlight navigation buttons by level
   */
  function highlightNavigationByLevel() {
    elements.navItems.forEach(btn => {
      const level = btn.getAttribute('data-level');
      if (level && CATEGORY_COLORS[level]) {
        // Add subtle border color based on level
        btn.style.borderLeft = `3px solid var(--color-${level.toLowerCase()})`;
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
    
    showLoading(true);
    
    try {
      // Collect all question data
      const exportData = [];
      
      elements.questions.forEach(article => {
        const questionId = article.getAttribute('data-question-id');
        const questionText = article.querySelector('p').textContent;
        const level = article.querySelector('.classification-badge').textContent.trim();
        const confidence = article.querySelector('[class*="confidence"]')?.textContent;
        
        exportData.push({
          id: questionId,
          question: questionText,
          level: level,
          confidence: confidence || 'N/A'
        });
      });

      // Create CSV content
      const csvContent = createCSV(exportData);
      
      // Download CSV
      downloadCSV(csvContent, 'classification_results.csv');
      
      showToast('Export successful!', 'success');
    } catch (error) {
      console.error('Export error:', error);
      showToast('Export failed. Please try again.', 'error');
    } finally {
      showLoading(false);
    }
  }

  /**
   * Create CSV from data
   */
  function createCSV(data) {
    const headers = ['Question ID', 'Question Text', 'Classification Level', 'Confidence'];
    const rows = data.map(item => [
      item.id,
      `"${item.question.replace(/"/g, '""')}"`, // Escape quotes
      item.level,
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
      document.getElementById('tab-detail').classList.remove('hidden');
      document.getElementById('tab-overview').classList.add('hidden');
    } else if (targetTab === 'overview') {
      document.getElementById('tab-detail').classList.add('hidden');
      document.getElementById('tab-overview').classList.remove('hidden');
      updateOverviewCounts(); // Refresh counts
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
    // Arrow keys for navigation
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      const activeIndex = Array.from(elements.navItems).findIndex(btn => 
        btn.classList.contains('bg-blue-600')
      );

      let newIndex;
      if (e.key === 'ArrowDown') {
        newIndex = Math.min(activeIndex + 1, elements.navItems.length - 1);
      } else {
        newIndex = Math.max(activeIndex - 1, 0);
      }

      setActiveQuestion(newIndex);
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
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(400px)';
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