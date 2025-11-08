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
    removeFileBtn: document.getElementById('remove-file-btn'),
    profileMenuButton: document.getElementById('profile-menu-button'),
    profileMenuDropdown: document.getElementById('profile-menu-dropdown'),
    deleteHistoryBtns: document.querySelectorAll('.delete-history-btn'),
    clearAllHistoryBtn: document.getElementById('clear-all-history-btn'),
    clearAllForm: document.getElementById('clear-all-form')
  };

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
    
    // Update UI
    if (elements.fileName) {
      elements.fileName.textContent = file.name;
      
      // Add file size info
      const sizeSpan = elements.fileName.nextElementSibling;
      if (sizeSpan) {
        sizeSpan.textContent = `${formatFileSize(file.size)} - Ready to classify`;
      }
    }
    
    if (elements.filePreview) {
      elements.filePreview.classList.remove('hidden');
      elements.filePreview.classList.add('flex');
      
      // Add animation
      elements.filePreview.style.opacity = '0';
      setTimeout(() => {
        elements.filePreview.style.transition = 'opacity 0.3s ease-in-out';
        elements.filePreview.style.opacity = '1';
      }, 10);
    }
    
    if (elements.dropZone) {
      elements.dropZone.classList.add('hidden');
    }
    
    if (elements.classifyBtn) {
      elements.classifyBtn.disabled = false;
      elements.classifyBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
      elements.classifyBtn.classList.add('bg-gray-500', 'hover:bg-blue-600', 'cursor-pointer');
    }
  }

  /**
   * Remove file preview and reset form
   */
  function removeFilePreview() {
    if (elements.fileInput) {
      elements.fileInput.value = '';
    }
    
    if (elements.filePreview) {
      elements.filePreview.style.opacity = '0';
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
      elements.classifyBtn.classList.add('bg-gray-400');
      elements.classifyBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
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
  // 4. PROFILE MENU DROPDOWN
  // ==========================================
  
  if (elements.profileMenuButton && elements.profileMenuDropdown) {
    // Toggle dropdown on button click
    elements.profileMenuButton.addEventListener('click', (e) => {
      e.stopPropagation();
      elements.profileMenuDropdown.classList.toggle('hidden');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!elements.profileMenuButton.contains(e.target) && 
          !elements.profileMenuDropdown.contains(e.target)) {
        elements.profileMenuDropdown.classList.add('hidden');
      }
    });

    // Close dropdown on ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !elements.profileMenuDropdown.classList.contains('hidden')) {
        elements.profileMenuDropdown.classList.add('hidden');
      }
    });
  }

  // ==========================================
  // 5. HISTORY TABLE ACTIONS
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
   * Show notification message
   * @param {string} message - Message to display
   * @param {string} type - Type: 'success', 'error', 'info'
   */
  function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 max-w-md p-4 rounded-xl shadow-lg animate-fade-in ${
      type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
      type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
      'bg-blue-100 border border-blue-300 text-blue-800'
    }`;
    
    notification.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <i class="bi bi-${
            type === 'success' ? 'check-circle-fill' :
            type === 'error' ? 'exclamation-triangle-fill' :
            'info-circle-fill'
          } text-xl mr-3"></i>
          <span class="font-medium">${message}</span>
        </div>
        <button class="ml-4 text-2xl font-bold leading-none hover:opacity-70">&times;</button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => notification.remove(), 300);
    }, 5000);
    
    // Remove on click
    notification.querySelector('button').addEventListener('click', () => {
      notification.style.opacity = '0';
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
  // 6. AUTO-DISMISS MESSAGES
  // ==========================================
  
  const messageAlerts = document.querySelectorAll('[id^="message-alert-"]');
  if (messageAlerts.length > 0) {
    messageAlerts.forEach(alert => {
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    });
  }

  // ==========================================
  // 7. FORM SUBMISSION HANDLING
  // ==========================================
  
  if (elements.classifyBtn) {
    const form = elements.classifyBtn.closest('form');
    
    if (form) {
      form.addEventListener('submit', (e) => {
        // Show loading state
        elements.classifyBtn.disabled = true;
        elements.classifyBtn.innerHTML = `
          <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          PROCESSING...
        `;
      });
    }
  }

  // ==========================================
  // 8. RESPONSIVE UTILITIES
  // ==========================================
  
  /**
   * Handle responsive behavior on window resize
   */
  function handleResize() {
    const isMobile = window.innerWidth < 768;
    
    // Close dropdown on mobile when resizing to desktop
    if (!isMobile && elements.profileMenuDropdown) {
      elements.profileMenuDropdown.classList.add('hidden');
    }
  }

  // Debounce resize handler
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(handleResize, 250);
  });

  // ==========================================
  // 9. KEYBOARD ACCESSIBILITY
  // ==========================================
  
  // Allow file selection with Enter/Space on drop zone
  if (elements.dropZone) {
    elements.dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        elements.fileInput?.click();
      }
    });
  }

  // ==========================================
  // 10. INITIALIZATION
  // ==========================================
  
  console.log('✓ Bloomers Home Page Initialized');
  
})();