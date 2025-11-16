// ============================================
// BLOOMERS - Enhanced Home Page JavaScript
// ============================================

(function() {
  'use strict';

  // ==========================================
  // 1. DOM ELEMENT REFERENCES
  // ==========================================
  const elements = {
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    classifyBtn: document.getElementById('classify-btn'),
    filePreview: document.getElementById('file-preview'),
    fileName: document.getElementById('file-name'),
    fileSize: document.getElementById('file-size'),
    removeFileBtn: document.getElementById('remove-file-btn'),
    deleteHistoryBtns: document.querySelectorAll('.delete-history-btn'),
    clearAllHistoryBtn: document.getElementById('clear-all-history-btn'),
    clearAllForm: document.getElementById('clear-all-form'),
    uploadForm: document.getElementById('upload-form')
  };

  // Store current file
  let currentFile = null;

  // ==========================================
  // 2. FILE UPLOAD HANDLING
  // ==========================================
  
  /**
   * Validates file type and size
   * @param {File} file - The file to validate
   * @returns {Object} - { valid: boolean, error: string|null }
   */
  function validateFile(file) {
    const allowedTypes = ['text/plain', 'application/pdf', 'text/csv', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['txt', 'pdf', 'csv', 'docx'];
    const maxSizeMB = 10;
    
    if (!file) {
      return { valid: false, error: 'No file selected' };
    }
    
    // Check extension
    const extension = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      return { 
        valid: false, 
        error: `Invalid file type. Please upload ${allowedExtensions.join(', ').toUpperCase()} files only.` 
      };
    }
    
    // Check size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      return { 
        valid: false, 
        error: `File size (${fileSizeMB.toFixed(2)}MB) exceeds ${maxSizeMB}MB limit.` 
      };
    }
    
    return { valid: true, error: null };
  }

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} - Formatted file size
   */
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Get file icon based on extension
   * @param {string} fileName - Name of the file
   * @returns {string} - Bootstrap icon class
   */
  function getFileIcon(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    const iconMap = {
      'pdf': 'file-earmark-pdf-fill text-red-600',
      'csv': 'file-earmark-spreadsheet-fill text-green-600',
      'txt': 'file-earmark-text-fill text-blue-600',
      'docx': 'file-earmark-word-fill text-blue-700'
    };
    return iconMap[extension] || 'file-earmark-text-fill text-blue-600';
  }

  /**
   * Handle file selection and display preview
   * @param {File} file - The selected file
   */
  function handleFileSelect(file) {
    if (!file) return;
    
    // Validate file
    const validation = validateFile(file);
    if (!validation.valid) {
      showNotification(validation.error, 'error');
      removeFilePreview();
      return;
    }
    
    // Store current file
    currentFile = file;
    
    // Update UI
    if (elements.fileName) {
      elements.fileName.textContent = file.name;
    }
    
    if (elements.fileSize) {
      elements.fileSize.textContent = `${formatFileSize(file.size)} - Ready to classify`;
    }
    
    if (elements.filePreview) {
      elements.filePreview.classList.remove('hidden');
      elements.filePreview.classList.add('flex');
      
      // Update file icon
      const iconElement = elements.filePreview.querySelector('i');
      if (iconElement) {
        iconElement.className = `bi ${getFileIcon(file.name)} text-3xl flex-shrink-0`;
      }
      
      // Add animation
      elements.filePreview.style.opacity = '0';
      elements.filePreview.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        elements.filePreview.style.transition = 'all 0.3s ease-in-out';
        elements.filePreview.style.opacity = '1';
        elements.filePreview.style.transform = 'translateY(0)';
      }, 10);
    }
    
    if (elements.dropZone) {
      elements.dropZone.classList.add('hidden');
    }
    
    if (elements.classifyBtn) {
      elements.classifyBtn.disabled = false;
      elements.classifyBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
      elements.classifyBtn.classList.add('bg-blue-600', 'hover:bg-blue-700', 'cursor-pointer');
      
      // Add pulse animation
      elements.classifyBtn.classList.add('animate-pulse');
      setTimeout(() => elements.classifyBtn.classList.remove('animate-pulse'), 2000);
    }

    showNotification('✓ File selected successfully! Ready to classify.', 'success');
  }

  /**
   * Remove file preview and reset form
   */
  function removeFilePreview() {
    currentFile = null;
    
    if (elements.fileInput) {
      elements.fileInput.value = '';
    }
    
    if (elements.filePreview) {
      elements.filePreview.style.opacity = '0';
      elements.filePreview.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        elements.filePreview.classList.add('hidden');
        elements.filePreview.classList.remove('flex');
      }, 200);
    }
    
    if (elements.dropZone) {
      elements.dropZone.classList.remove('hidden');
    }
    
    if (elements.classifyBtn) {
      elements.classifyBtn.disabled = true;
      elements.classifyBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
      elements.classifyBtn.classList.add('bg-gray-400', 'cursor-not-allowed');
    }
  }

  /**
   * Prevent default drag behaviors
   */
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  /**
   * Highlight drop zone on drag enter/over
   */
  function highlightDropZone() {
    if (elements.dropZone) {
      elements.dropZone.classList.add('border-blue-500', 'bg-blue-50', 'scale-105');
    }
  }

  /**
   * Remove drop zone highlight
   */
  function unhighlightDropZone() {
    if (elements.dropZone) {
      elements.dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'scale-105');
    }
  }

  // ==========================================
  // 3. EVENT LISTENERS - FILE UPLOAD
  // ==========================================
  
  if (elements.removeFileBtn) {
    elements.removeFileBtn.addEventListener('click', removeFilePreview);
  }

  if (elements.fileInput) {
    elements.fileInput.addEventListener('change', (e) => {
      handleFileSelect(e.target.files[0]);
    });
  }

  if (elements.dropZone) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      elements.dropZone.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight on drag enter/over
    ['dragenter', 'dragover'].forEach(eventName => {
      elements.dropZone.addEventListener(eventName, highlightDropZone, false);
    });

    // Unhighlight on drag leave/drop
    ['dragleave', 'drop'].forEach(eventName => {
      elements.dropZone.addEventListener(eventName, unhighlightDropZone, false);
    });

    // Handle dropped files
    elements.dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      
      if (files.length > 1) {
        showNotification('Please upload only one file at a time.', 'error');
        return;
      }
      
      if (elements.fileInput) {
        elements.fileInput.files = files;
      }
      handleFileSelect(files[0]);
    }, false);
  }

  // ==========================================
  // 4. HISTORY TABLE ACTIONS
  // ==========================================
  
  /**
   * Show confirmation dialog
   * @param {string} message - Confirmation message
   * @returns {boolean} - User confirmation
   */
  function confirmAction(message) {
    return confirm(message);
  }

  /**
   * Show notification message with enhanced styling
   * @param {string} message - Message to display
   * @param {string} type - Type: 'success', 'error', 'info', 'warning'
   */
  function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 max-w-md p-4 rounded-xl shadow-lg transition-all duration-300 ${
      type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
      type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
      type === 'warning' ? 'bg-yellow-100 border border-yellow-300 text-yellow-800' :
      'bg-blue-100 border border-blue-300 text-blue-800'
    }`;
    
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(400px)';
    
    notification.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <i class="bi bi-${
            type === 'success' ? 'check-circle-fill' :
            type === 'error' ? 'exclamation-triangle-fill' :
            type === 'warning' ? 'exclamation-circle-fill' :
            'info-circle-fill'
          } text-xl mr-3"></i>
          <span class="font-medium">${message}</span>
        </div>
        <button class="ml-4 text-2xl font-bold leading-none hover:opacity-70 transition-opacity">&times;</button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto-remove after 5 seconds
    const timer = setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(400px)';
      setTimeout(() => notification.remove(), 300);
    }, 5000);
    
    // Remove on click
    notification.querySelector('button').addEventListener('click', () => {
      clearTimeout(timer);
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(400px)';
      setTimeout(() => notification.remove(), 300);
    });
  }

  // Delete individual history item
  if (elements.deleteHistoryBtns.length > 0) {
    elements.deleteHistoryBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const filename = btn.closest('tr')?.querySelector('span.font-medium')?.textContent || 'this file';
        
        if (confirmAction(`Are you sure you want to delete "${filename}"?\n\nThis action cannot be undone.`)) {
          window.location.href = btn.href;
        }
      });
    });
  }

  // Clear all history
  if (elements.clearAllHistoryBtn && elements.clearAllForm) {
    elements.clearAllHistoryBtn.addEventListener('click', (e) => {
      e.preventDefault();
      
      if (confirmAction('Are you sure you want to delete ALL files from your history?\n\nThis action cannot be undone.')) {
        elements.clearAllForm.submit();
      }
    });
  }

  // ==========================================
  // 5. AUTO-DISMISS MESSAGES
  // ==========================================
  
  const messageAlerts = document.querySelectorAll('[id^="message-alert-"]');
  if (messageAlerts.length > 0) {
    messageAlerts.forEach(alert => {
      // Auto-dismiss after 5 seconds
      const timer = setTimeout(() => {
        if (alert) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateX(100%)';
          setTimeout(() => alert.remove(), 300);
        }
      }, 5000);
      
      // Stop timer if closed manually
      const closeButton = alert.querySelector('button');
      if (closeButton) {
        closeButton.addEventListener('click', () => {
          clearTimeout(timer);
        });
      }
    });
  }

  // ==========================================
  // 6. FORM SUBMISSION HANDLING
  // ==========================================
  
  if (elements.classifyBtn && elements.uploadForm) {
    elements.uploadForm.addEventListener('submit', (e) => {
      // Check if button is disabled (no file)
      if (elements.classifyBtn.disabled) {
        e.preventDefault();
        showNotification('Please select a valid file first.', 'error');
        return;
      }
      
      // Show loading state
      elements.classifyBtn.disabled = true;
      elements.classifyBtn.innerHTML = `
        <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        PROCESSING...
      `;

      // Show progress notification
      showNotification('⏳ Classifying your questions... This may take a moment.', 'info');
    });
  }

  // ==========================================
  // 7. RESPONSIVE UTILITIES
  // ==========================================
  
  /**
   * Handle responsive behavior on window resize
   */
  function handleResize() {
    const isMobile = window.innerWidth < 768;
    
    // Add responsive adjustments if needed
    if (isMobile && elements.filePreview) {
      // Adjust preview for mobile
      elements.filePreview.classList.add('flex-col');
    } else if (elements.filePreview) {
      elements.filePreview.classList.remove('flex-col');
    }
  }

  // Debounce resize handler
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(handleResize, 250);
  });

  // ==========================================
  // 8. KEYBOARD ACCESSIBILITY
  // ==========================================
  
  // Allow file selection with Enter/Space on drop zone
  if (elements.dropZone) {
    elements.dropZone.setAttribute('tabindex', '0');
    
    elements.dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        elements.fileInput?.click();
      }
    });
  }

  // ==========================================
  // 9. ENHANCED HISTORY TABLE FEATURES
  // ==========================================
  
  /**
   * Add hover effects to table rows
   */
  function enhanceHistoryTable() {
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.transform = 'scale(1.01)';
        row.style.transition = 'transform 0.2s ease-in-out';
      });
      
      row.addEventListener('mouseleave', () => {
        row.style.transform = 'scale(1)';
      });
    });
  }

  // ==========================================
  // 10. FILE PREVIEW ENHANCEMENTS
  // ==========================================
  
  /**
   * Add file details tooltip
   */
  function addFileTooltip() {
    if (elements.fileName && currentFile) {
      elements.fileName.title = `File: ${currentFile.name}\nSize: ${formatFileSize(currentFile.size)}\nType: ${currentFile.type}`;
    }
  }

  // ==========================================
  // 11. INITIALIZATION
  // ==========================================
  
  function init() {
    console.log('✓ Bloomers Home Page Initialized');
    
    // Initial responsive check
    handleResize();
    
    // Enhance history table if present
    enhanceHistoryTable();
    
    // Check for auto-scroll to history (if redirected after classification)
    if (window.location.hash === '#history') {
      const historySection = document.querySelector('section:last-of-type');
      if (historySection) {
        setTimeout(() => {
          historySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 500);
      }
    }
  }

  // Run initialization
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
})();