/**
 * Authentication JavaScript Module
 * Handles login, register, and common auth UI interactions
 */

// Utility functions
const AuthUtils = {
    /**
     * Validate email format
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Validate username format and length
     */
    validateUsername(username) {
        return username.length >= 3 && username.length <= 150;
    },

    /**
     * Calculate password strength (0-4)
     */
    calculatePasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        return Math.min(strength, 4);
    },

    /**
     * Show error message on input
     */
    showError(input, errorElement, message) {
        input.classList.add('border-red-500', 'focus:ring-red-500');
        input.classList.remove('border-gray-200');
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    },

    /**
     * Clear error message on input
     */
    clearError(input, errorElement) {
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-200');
        errorElement.classList.add('hidden');
    },

    /**
     * Setup password toggle functionality
     */
    setupPasswordToggle(passwordInput, toggleButton) {
        if (!passwordInput || !toggleButton) return;

        toggleButton.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

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
    },

    /**
     * Auto-dismiss alert messages
     */
    setupAutoDismissAlerts(duration = 5000) {
        const alerts = document.querySelectorAll('[role="alert"]');
        alerts.forEach(alert => {
            // Add close button functionality if not already present
            const closeButton = alert.querySelector('button');
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    alert.style.opacity = '0';
                    alert.style.transition = 'opacity 0.5s ease-out';
                    setTimeout(() => alert.remove(), 500);
                });
            }

            // Auto-dismiss after duration
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s ease-out';
                setTimeout(() => alert.remove(), 500);
            }, duration);
        });
    },

    /**
     * Show loading state on button
     */
    setButtonLoading(button, loadingText = 'Loading...') {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            ${loadingText}
        `;
    },

    /**
     * Reset button from loading state
     */
    resetButton(button) {
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
    }
};


// Login Page Handler
const LoginPage = {
    init() {
        const form = document.getElementById('login-form');
        if (!form) return;

        const emailInput = document.getElementById('email-input');
        const passwordInput = document.getElementById('password-input');
        const toggleButton = document.getElementById('password-toggle');
        const submitButton = document.getElementById('login-submit-btn');
        const emailError = document.getElementById('email-error');
        const passwordError = document.getElementById('password-error');

        // Setup password toggle
        AuthUtils.setupPasswordToggle(passwordInput, toggleButton);

        // Real-time email validation
        if (emailInput && emailError) {
            emailInput.addEventListener('blur', () => {
                const email = emailInput.value.trim();
                if (email && !AuthUtils.validateEmail(email)) {
                    AuthUtils.showError(emailInput, emailError, 'Please enter a valid email address');
                } else {
                    AuthUtils.clearError(emailInput, emailError);
                }
            });

            emailInput.addEventListener('input', () => {
                if (!emailError.classList.contains('hidden')) {
                    AuthUtils.clearError(emailInput, emailError);
                }
            });
        }

        // Real-time password validation
        if (passwordInput && passwordError) {
            passwordInput.addEventListener('input', () => {
                if (!passwordError.classList.contains('hidden')) {
                    AuthUtils.clearError(passwordInput, passwordError);
                }
            });
        }

        // Form submission
        form.addEventListener('submit', (e) => {
            let isValid = true;

            // Validate email
            if (emailInput && emailError) {
                const email = emailInput.value.trim();
                if (!email) {
                    AuthUtils.showError(emailInput, emailError, 'Email is required');
                    isValid = false;
                } else if (!AuthUtils.validateEmail(email)) {
                    AuthUtils.showError(emailInput, emailError, 'Please enter a valid email address');
                    isValid = false;
                }
            }

            // Validate password
            if (passwordInput && passwordError) {
                const password = passwordInput.value;
                if (!password) {
                    AuthUtils.showError(passwordInput, passwordError, 'Password is required');
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                return;
            }

            // Show loading state
            if (submitButton) {
                AuthUtils.setButtonLoading(submitButton, 'Signing In...');
            }
        });
    }
};


// Register Page Handler
const RegisterPage = {
    init() {
        const form = document.getElementById('register-form');
        if (!form) return;

        const usernameInput = document.getElementById('username-input');
        const emailInput = document.getElementById('email-input');
        const passwordInput = document.getElementById('password-input');
        const confirmPasswordInput = document.getElementById('confirm-password-input');
        const toggleButton = document.getElementById('password-toggle');
        const confirmToggleButton = document.getElementById('confirm-password-toggle');
        const submitButton = document.getElementById('register-submit-btn');
        const termsCheckbox = document.getElementById('terms-checkbox');

        const usernameError = document.getElementById('username-error');
        const emailError = document.getElementById('email-error');
        const passwordError = document.getElementById('password-error');
        const confirmPasswordError = document.getElementById('confirm-password-error');

        // Setup password toggles
        AuthUtils.setupPasswordToggle(passwordInput, toggleButton);
        AuthUtils.setupPasswordToggle(confirmPasswordInput, confirmToggleButton);

        // Update password strength indicator
        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                this.updatePasswordStrength(passwordInput.value);
                
                if (passwordError && !passwordError.classList.contains('hidden')) {
                    AuthUtils.clearError(passwordInput, passwordError);
                }

                // Check password match
                if (confirmPasswordInput && confirmPasswordError && confirmPasswordInput.value) {
                    if (passwordInput.value !== confirmPasswordInput.value) {
                        AuthUtils.showError(confirmPasswordInput, confirmPasswordError, 'Passwords do not match');
                    } else {
                        AuthUtils.clearError(confirmPasswordInput, confirmPasswordError);
                    }
                }
            });
        }

        // Confirm password validation
        if (confirmPasswordInput && confirmPasswordError) {
            confirmPasswordInput.addEventListener('input', () => {
                if (passwordInput && passwordInput.value !== confirmPasswordInput.value) {
                    AuthUtils.showError(confirmPasswordInput, confirmPasswordError, 'Passwords do not match');
                } else {
                    AuthUtils.clearError(confirmPasswordInput, confirmPasswordError);
                }
            });
        }

        // Username validation
        if (usernameInput && usernameError) {
            usernameInput.addEventListener('blur', () => {
                const username = usernameInput.value.trim();
                if (username && !AuthUtils.validateUsername(username)) {
                    AuthUtils.showError(usernameInput, usernameError, 'Username must be 3-150 characters');
                } else {
                    AuthUtils.clearError(usernameInput, usernameError);
                }
            });

            usernameInput.addEventListener('input', () => {
                if (!usernameError.classList.contains('hidden')) {
                    AuthUtils.clearError(usernameInput, usernameError);
                }
            });
        }

        // Email validation
        if (emailInput && emailError) {
            emailInput.addEventListener('blur', () => {
                const email = emailInput.value.trim();
                if (email && !AuthUtils.validateEmail(email)) {
                    AuthUtils.showError(emailInput, emailError, 'Please enter a valid email address');
                } else {
                    AuthUtils.clearError(emailInput, emailError);
                }
            });

            emailInput.addEventListener('input', () => {
                if (!emailError.classList.contains('hidden')) {
                    AuthUtils.clearError(emailInput, emailError);
                }
            });
        }

        // Form submission
        form.addEventListener('submit', (e) => {
            let isValid = true;

            // Validate username
            if (usernameInput && usernameError) {
                const username = usernameInput.value.trim();
                if (!username) {
                    AuthUtils.showError(usernameInput, usernameError, 'Username is required');
                    isValid = false;
                } else if (!AuthUtils.validateUsername(username)) {
                    AuthUtils.showError(usernameInput, usernameError, 'Username must be 3-150 characters');
                    isValid = false;
                }
            }

            // Validate email
            if (emailInput && emailError) {
                const email = emailInput.value.trim();
                if (!email) {
                    AuthUtils.showError(emailInput, emailError, 'Email is required');
                    isValid = false;
                } else if (!AuthUtils.validateEmail(email)) {
                    AuthUtils.showError(emailInput, emailError, 'Please enter a valid email address');
                    isValid = false;
                }
            }

            // Validate password
            if (passwordInput && passwordError) {
                const password = passwordInput.value;
                if (!password) {
                    AuthUtils.showError(passwordInput, passwordError, 'Password is required');
                    isValid = false;
                } else if (password.length < 8) {
                    AuthUtils.showError(passwordInput, passwordError, 'Password must be at least 8 characters');
                    isValid = false;
                }
            }

            // Validate confirm password
            if (confirmPasswordInput && confirmPasswordError) {
                const confirmPassword = confirmPasswordInput.value;
                const password = passwordInput ? passwordInput.value : '';
                
                if (!confirmPassword) {
                    AuthUtils.showError(confirmPasswordInput, confirmPasswordError, 'Please confirm your password');
                    isValid = false;
                } else if (password !== confirmPassword) {
                    AuthUtils.showError(confirmPasswordInput, confirmPasswordError, 'Passwords do not match');
                    isValid = false;
                }
            }

            // Validate terms checkbox
            if (termsCheckbox && !termsCheckbox.checked) {
                alert('Please agree to the Terms of Service and Privacy Policy');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
                return;
            }

            // Show loading state
            if (submitButton) {
                AuthUtils.setButtonLoading(submitButton, 'Creating Account...');
            }
        });
    },

    updatePasswordStrength(password) {
        const strength = AuthUtils.calculatePasswordStrength(password);
        const bars = [
            document.getElementById('strength-bar-1'),
            document.getElementById('strength-bar-2'),
            document.getElementById('strength-bar-3'),
            document.getElementById('strength-bar-4')
        ];
        const strengthText = document.getElementById('strength-text');

        if (!bars[0] || !strengthText) return;

        // Reset bars
        bars.forEach(bar => {
            if (bar) bar.className = 'h-1 flex-1 rounded-full bg-gray-200';
        });

        if (password.length === 0) {
            strengthText.textContent = 'At least 8 characters';
            strengthText.className = 'text-xs text-gray-500';
            return;
        }

        let strengthClass = '';
        let strengthLabel = '';

        if (strength <= 2) {
            strengthClass = 'strength-weak';
            strengthLabel = 'Weak password';
            for (let i = 0; i < strength; i++) {
                if (bars[i]) bars[i].className = 'h-1 flex-1 rounded-full ' + strengthClass;
            }
        } else if (strength === 3) {
            strengthClass = 'strength-medium';
            strengthLabel = 'Medium strength';
            for (let i = 0; i < strength; i++) {
                if (bars[i]) bars[i].className = 'h-1 flex-1 rounded-full ' + strengthClass;
            }
        } else {
            strengthClass = 'strength-strong';
            strengthLabel = 'Strong password';
            bars.forEach(bar => {
                if (bar) bar.className = 'h-1 flex-1 rounded-full ' + strengthClass;
            });
        }

        strengthText.textContent = strengthLabel;
        strengthText.className = 'text-xs font-medium ' + 
            (strength <= 2 ? 'text-red-600' : strength === 3 ? 'text-orange-600' : 'text-green-600');
    }
};


// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize appropriate page handler
    LoginPage.init();
    RegisterPage.init();

    // Setup auto-dismiss for alerts
    AuthUtils.setupAutoDismissAlerts();
});