/**
 * BLOOMERS - Settings Page JavaScript
 * Handles all settings page interactions and form submissions
 */

(function() {
    'use strict';

    // ==========================================
    // 1. DOM ELEMENT REFERENCES
    // ==========================================
    const elements = {
        // Tab buttons
        tabButtons: document.querySelectorAll('.tab-button'),
        tabContents: document.querySelectorAll('.tab-content'),
        
        // Password toggles
        passwordToggles: document.querySelectorAll('.password-toggle'),
        
        // Delete account
        deleteAccountBtn: document.getElementById('delete-account-btn'),
        deleteModal: document.getElementById('delete-modal'),
        cancelDeleteBtn: document.getElementById('cancel-delete-btn'),
        deleteAccountForm: document.getElementById('delete-account-form'),
        
        // Form inputs
        emailInput: document.getElementById('email'),
        firstNameInput: document.getElementById('first-name'),
        lastNameInput: document.getElementById('last-name'),
        
        // Password inputs
        currentPasswordInput: document.getElementById('current-password'),
        newPasswordInput: document.getElementById('new-password'),
        confirmPasswordInput: document.getElementById('confirm-password'),
        
        // Messages
        messageAlerts: document.querySelectorAll('[id^="message-alert-"]')
    };

    // ==========================================
    // 2. TAB SWITCHING FUNCTIONALITY
    // ==========================================
    
    /**
     * Switch to a specific tab
     * @param {string} tabName - Name of the tab to activate
     */
    function switchTab(tabName) {
        // Remove active class from all tabs
        elements.tabButtons.forEach(btn => {
            btn.classList.remove('tab-active');
        });
        
        // Hide all tab contents
        elements.tabContents.forEach(content => {
            content.classList.add('hidden');
        });
        
        // Activate selected tab button
        const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeButton) {
            activeButton.classList.add('tab-active');
        }
        
        // Show selected tab content
        const activeContent = document.getElementById(`${tabName}-tab`);
        if (activeContent) {
            activeContent.classList.remove('hidden');
            
            // Add fade-in animation
            activeContent.style.opacity = '0';
            setTimeout(() => {
                activeContent.style.transition = 'opacity 0.3s ease-in-out';
                activeContent.style.opacity = '1';
            }, 10);
        }
        
        // Update URL hash without scrolling
        if (history.pushState) {
            history.pushState(null, null, `#${tabName}`);
        } else {
            location.hash = `#${tabName}`;
        }
    }
    
    /**
     * Initialize tab switching event listeners
     */
    function initTabSwitching() {
        elements.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
        
        // Handle initial tab from URL hash
        const hash = window.location.hash.substring(1);
        const validTabs = ['account', 'security', 'notifications', 'preferences'];
        
        if (hash && validTabs.includes(hash)) {
            switchTab(hash);
        } else {
            switchTab('account'); // Default tab
        }
    }

    // ==========================================
    // 3. PASSWORD VISIBILITY TOGGLE
    // ==========================================
    
    /**
     * Toggle password visibility for a specific input
     * @param {HTMLElement} toggleButton - The toggle button element
     */
    function setupPasswordToggle(toggleButton) {
        toggleButton.addEventListener('click', () => {
            const input = toggleButton.previousElementSibling;
            if (!input) return;
            
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            const icon = toggleButton.querySelector('i');
            if (icon) {
                if (type === 'password') {
                    icon.classList.remove('bi-eye');
                    icon.classList.add('bi-eye-slash');
                } else {
                    icon.classList.remove('bi-eye-slash');
                    icon.classList.add('bi-eye');
                }
            }
        });
    }
    
    /**
     * Initialize all password toggles
     */
    function initPasswordToggles() {
        elements.passwordToggles.forEach(toggle => {
            setupPasswordToggle(toggle);
        });
    }

    // ==========================================
    // 4. FORM VALIDATION
    // ==========================================
    
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} - True if valid
     */
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {object} - { valid: boolean, message: string }
     */
    function validatePassword(password) {
        if (password.length < 8) {
            return { valid: false, message: 'Password must be at least 8 characters long' };
        }
        
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);
        
        if (!hasUpper || !hasLower || !hasNumber) {
            return { valid: false, message: 'Password must contain uppercase, lowercase, and numbers' };
        }
        
        return { valid: true, message: '' };
    }
    
    /**
     * Show validation error on input
     * @param {HTMLElement} input - Input element
     * @param {string} message - Error message
     */
    function showError(input, message) {
        input.classList.add('border-red-500', 'focus:ring-red-500');
        input.classList.remove('border-gray-200');
        
        // Create or update error message
        let errorMsg = input.parentElement.querySelector('.error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('p');
            errorMsg.className = 'error-message text-red-600 text-sm mt-1';
            input.parentElement.appendChild(errorMsg);
        }
        errorMsg.textContent = message;
    }
    
    /**
     * Clear validation error on input
     * @param {HTMLElement} input - Input element
     */
    function clearError(input) {
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-200');
        
        const errorMsg = input.parentElement.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }
    
    /**
     * Initialize form validation
     */
    function initFormValidation() {
        // Email validation
        if (elements.emailInput) {
            elements.emailInput.addEventListener('blur', () => {
                const email = elements.emailInput.value.trim();
                if (email && !validateEmail(email)) {
                    showError(elements.emailInput, 'Please enter a valid email address');
                } else {
                    clearError(elements.emailInput);
                }
            });
            
            elements.emailInput.addEventListener('input', () => {
                clearError(elements.emailInput);
            });
        }
        
        // Password validation
        if (elements.newPasswordInput) {
            elements.newPasswordInput.addEventListener('blur', () => {
                const password = elements.newPasswordInput.value;
                if (password) {
                    const validation = validatePassword(password);
                    if (!validation.valid) {
                        showError(elements.newPasswordInput, validation.message);
                    } else {
                        clearError(elements.newPasswordInput);
                    }
                }
            });
            
            elements.newPasswordInput.addEventListener('input', () => {
                clearError(elements.newPasswordInput);
                
                // Check if passwords match
                if (elements.confirmPasswordInput && elements.confirmPasswordInput.value) {
                    if (elements.newPasswordInput.value !== elements.confirmPasswordInput.value) {
                        showError(elements.confirmPasswordInput, 'Passwords do not match');
                    } else {
                        clearError(elements.confirmPasswordInput);
                    }
                }
            });
        }
        
        // Confirm password validation
        if (elements.confirmPasswordInput) {
            elements.confirmPasswordInput.addEventListener('input', () => {
                if (elements.newPasswordInput) {
                    if (elements.newPasswordInput.value !== elements.confirmPasswordInput.value) {
                        showError(elements.confirmPasswordInput, 'Passwords do not match');
                    } else {
                        clearError(elements.confirmPasswordInput);
                    }
                }
            });
        }
    }

    // ==========================================
    // 5. DELETE ACCOUNT MODAL
    // ==========================================
    
    /**
     * Show delete account modal
     */
    function showDeleteModal() {
        if (elements.deleteModal) {
            elements.deleteModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
            
            // Focus on password input
            const passwordInput = document.getElementById('confirm-password-delete');
            if (passwordInput) {
                setTimeout(() => passwordInput.focus(), 100);
            }
        }
    }
    
    /**
     * Hide delete account modal
     */
    function hideDeleteModal() {
        if (elements.deleteModal) {
            elements.deleteModal.classList.add('hidden');
            document.body.style.overflow = ''; // Restore scrolling
            
            // Clear password input
            const passwordInput = document.getElementById('confirm-password-delete');
            if (passwordInput) {
                passwordInput.value = '';
            }
        }
    }
    
    /**
     * Initialize delete account modal
     */
    function initDeleteModal() {
        // Show modal
        if (elements.deleteAccountBtn) {
            elements.deleteAccountBtn.addEventListener('click', () => {
                showDeleteModal();
            });
        }
        
        // Hide modal
        if (elements.cancelDeleteBtn) {
            elements.cancelDeleteBtn.addEventListener('click', () => {
                hideDeleteModal();
            });
        }
        
        // Close on outside click
        if (elements.deleteModal) {
            elements.deleteModal.addEventListener('click', (e) => {
                if (e.target === elements.deleteModal) {
                    hideDeleteModal();
                }
            });
        }
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.deleteModal && !elements.deleteModal.classList.contains('hidden')) {
                hideDeleteModal();
            }
        });
        
        // Confirm before submit
        if (elements.deleteAccountForm) {
            elements.deleteAccountForm.addEventListener('submit', (e) => {
                const confirmText = 'Are you absolutely sure you want to delete your account? This action cannot be undone.';
                if (!confirm(confirmText)) {
                    e.preventDefault();
                }
            });
        }
    }

    // ==========================================
    // 6. AUTO-DISMISS MESSAGES
    // ==========================================
    
    /**
     * Auto-dismiss alert messages after delay
     */
    function initAutoDismissMessages() {
        elements.messageAlerts.forEach(alert => {
            // Auto-dismiss after 5 seconds
            const timer = setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
            
            // Cancel timer if manually closed
            const closeButton = alert.querySelector('button');
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    clearTimeout(timer);
                });
            }
        });
    }

    // ==========================================
    // 7. NOTIFICATION PREFERENCES
    // ==========================================
    
    /**
     * Show notification when toggling preferences
     */
    function initNotificationToggles() {
        const notificationCheckboxes = document.querySelectorAll('#notifications-tab input[type="checkbox"]');
        
        notificationCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const label = checkbox.closest('.flex').querySelector('label');
                const settingName = label ? label.textContent.trim() : 'Setting';
                const isEnabled = checkbox.checked;
                
                showNotification(
                    `${settingName} ${isEnabled ? 'enabled' : 'disabled'}`,
                    'info'
                );
            });
        });
    }

    // ==========================================
    // 8. UTILITY FUNCTIONS
    // ==========================================
    
    /**
     * Show notification message
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'info'
     */
    function showNotification(message, type = 'info') {
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
        
        const timer = setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
        
        notification.querySelector('button').addEventListener('click', () => {
            clearTimeout(timer);
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        });
    }
    
    /**
     * Confirm unsaved changes before leaving
     */
    function initUnsavedChangesWarning() {
        let hasUnsavedChanges = false;
        
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
            
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    hasUnsavedChanges = true;
                });
            });
            
            form.addEventListener('submit', () => {
                hasUnsavedChanges = false;
            });
        });
        
        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }
    
    /**
     * Smooth scroll to top when switching tabs
     */
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    // ==========================================
    // 9. KEYBOARD SHORTCUTS
    // ==========================================
    
    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + 1-4 to switch tabs
            if (e.altKey && !e.shiftKey && !e.ctrlKey) {
                const tabs = ['account', 'security', 'notifications', 'preferences'];
                const key = parseInt(e.key);
                
                if (key >= 1 && key <= 4) {
                    e.preventDefault();
                    switchTab(tabs[key - 1]);
                    scrollToTop();
                }
            }
        });
    }

    // ==========================================
    // 10. FORM SUBMISSION HANDLERS
    // ==========================================
    
    /**
     * Add loading state to submit buttons
     */
    function initFormSubmitHandlers() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                
                if (submitBtn && !submitBtn.disabled) {
                    // Disable button
                    submitBtn.disabled = true;
                    
                    // Store original content
                    const originalContent = submitBtn.innerHTML;
                    
                    // Show loading state
                    submitBtn.innerHTML = `
                        <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Saving...
                    `;
                    
                    // Re-enable after timeout (in case of error)
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalContent;
                    }, 10000);
                }
            });
        });
    }

    // ==========================================
    // 11. RESPONSIVE UTILITIES
    // ==========================================
    
    /**
     * Handle responsive behavior
     */
    function handleResize() {
        const isMobile = window.innerWidth < 768;
        
        // Adjust tab labels for mobile
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            const text = button.querySelector('span');
            if (text) {
                if (isMobile) {
                    text.classList.add('hidden', 'sm:inline');
                } else {
                    text.classList.remove('hidden');
                }
            }
        });
    }
    
    // Debounce resize handler
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResize, 250);
    });

    // ==========================================
    // 12. INITIALIZATION
    // ==========================================
    
    /**
     * Initialize all settings page functionality
     */
    function init() {
        console.log('✓ Bloomers Settings Page Initialized');
        
        // Initialize all features
        initTabSwitching();
        initPasswordToggles();
        initFormValidation();
        initDeleteModal();
        initAutoDismissMessages();
        initNotificationToggles();
        initUnsavedChangesWarning();
        initKeyboardShortcuts();
        initFormSubmitHandlers();
        handleResize();
        
        // Show keyboard shortcuts info
        console.log('💡 Tip: Use Alt+1, Alt+2, Alt+3, Alt+4 to quickly switch between tabs');
    }
    
    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();