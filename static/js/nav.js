/**
 * Navigation JavaScript
 * Handles mobile menu, profile dropdown, and profile page initialization
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeMobileMenu();
    initializeProfileDropdown();
    
    // Initialize profile page functions if on profile page
    if (document.getElementById('profile-pic-form')) {
        initializeProfilePage();
    }
    
    // Auto-hide alert messages
    initializeAlertMessages();
});

/**
 * Mobile Menu Toggle
 */
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

/**
 * Profile Dropdown Toggle
 */
function initializeProfileDropdown() {
    const profileButton = document.getElementById('profile-menu-button');
    const profileDropdown = document.getElementById('profile-menu-dropdown');
    
    if (profileButton && profileDropdown) {
        // Toggle dropdown on button click
        profileButton.addEventListener('click', function(event) {
            event.stopPropagation();
            profileDropdown.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!profileButton.contains(event.target) && !profileDropdown.contains(event.target)) {
                profileDropdown.classList.add('hidden');
            }
        });
        
        // Close dropdown when pressing Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && !profileDropdown.classList.contains('hidden')) {
                profileDropdown.classList.add('hidden');
            }
        });
    }
}

/**
 * Initialize Profile Page Functions
 */
function initializeProfilePage() {
    initializeProfilePicture();
    initializePasswordForm();
    initializeDetailsForm();
    initializeResponsiveFeatures();
}

/**
 * Profile Picture Upload and Preview
 */
function initializeProfilePicture() {
    const profilePicInput = document.getElementById('profile-pic-input');
    const profilePicPreview = document.getElementById('profile-pic-preview');
    const savePicBtn = document.getElementById('save-pic-btn');
    const profilePicForm = document.getElementById('profile-pic-form');
    
    if (!profilePicInput || !profilePicPreview) return;
    
    // Handle file selection
    profilePicInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (!file) {
            return;
        }
        
        // Client-side validation
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
        if (!allowedTypes.includes(file.type)) {
            showNotification('Please select a valid image file (PNG, JPG, or JPEG)', 'error');
            profilePicInput.value = '';
            return;
        }
        
        const maxSize = 2 * 1024 * 1024; // 2MB
        if (file.size > maxSize) {
            showNotification('File size must be less than 2MB', 'error');
            profilePicInput.value = '';
            return;
        }
        
        // Preview the image
        const reader = new FileReader();
        reader.onload = function(event) {
            const currentPreview = document.getElementById('profile-pic-preview');
            
            // If preview is currently a DIV (letter avatar)
            if (currentPreview.tagName === 'DIV') {
                const img = document.createElement('img');
                img.id = 'profile-pic-preview';
                img.className = 'w-32 h-32 md:w-48 md:h-48 rounded-full object-cover border-4 border-blue-200 shadow-md';
                img.src = event.target.result;
                img.alt = 'Profile Preview';
                currentPreview.parentNode.replaceChild(img, currentPreview);
            } else {
                // If already an <img> tag, just update the src
                currentPreview.src = event.target.result;
            }
            
            // Show save button
            if (savePicBtn) {
                savePicBtn.classList.remove('hidden');
            }
        };
        
        reader.onerror = function() {
            showNotification('Error reading file. Please try again.', 'error');
            profilePicInput.value = '';
        };
        
        reader.readAsDataURL(file);
    });
    
    // Handle form submission with loading state
    if (profilePicForm) {
        profilePicForm.addEventListener('submit', function(e) {
            const submitButton = e.submitter || document.activeElement;
            
            // Check if this is the "Remove" button
            if (submitButton && submitButton.name === 'remove_image') {
                if (!confirm('Are you sure you want to remove your profile picture?')) {
                    e.preventDefault();
                    return;
                }
            }
            
            // Check if this is the "Save New Photo" button
            if (submitButton && submitButton.id === 'save-pic-btn') {
                if (!profilePicInput.files || !profilePicInput.files[0]) {
                    e.preventDefault();
                    showNotification('Please select an image first', 'error');
                    return;
                }
            }
            
            // Show loading state
            if (submitButton && submitButton.type === 'submit') {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                
                if (submitButton.name === 'remove_image') {
                    submitButton.innerHTML = '<i class="bi bi-hourglass-split animate-spin"></i> Removing...';
                } else {
                    submitButton.innerHTML = '<i class="bi bi-hourglass-split animate-spin"></i> Uploading...';
                }
                
                // Timeout to re-enable if something goes wrong
                setTimeout(() => {
                    if (submitButton.disabled) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                }, 10000);
            }
        });
    }
}

/**
 * Password Change Form Validation
 */
function initializePasswordForm() {
    const passwordForm = document.getElementById('password-form');
    if (!passwordForm) return;
    
    const oldPassword = passwordForm.querySelector('[name="old_password"]');
    const newPassword1 = passwordForm.querySelector('[name="new_password1"]');
    const newPassword2 = passwordForm.querySelector('[name="new_password2"]');
    
    // Real-time password match validation
    if (newPassword2 && newPassword1) {
        const validateMatch = () => {
            if (newPassword1.value && newPassword2.value) {
                if (newPassword1.value !== newPassword2.value) {
                    newPassword2.setCustomValidity('Passwords do not match');
                    newPassword2.classList.add('border-red-500');
                    newPassword2.classList.remove('border-gray-300', 'border-green-500');
                } else {
                    newPassword2.setCustomValidity('');
                    newPassword2.classList.remove('border-red-500', 'border-gray-300');
                    newPassword2.classList.add('border-green-500');
                }
            } else {
                newPassword2.setCustomValidity('');
                newPassword2.classList.remove('border-red-500', 'border-green-500');
                newPassword2.classList.add('border-gray-300');
            }
        };
        
        newPassword1.addEventListener('input', validateMatch);
        newPassword2.addEventListener('input', validateMatch);
    }
    
    // Password strength indicator
    if (newPassword1) {
        newPassword1.addEventListener('input', function() {
            const strength = calculatePasswordStrength(newPassword1.value);
            updatePasswordStrengthUI(newPassword1, strength);
        });
    }
    
    // Form submission
    passwordForm.addEventListener('submit', function(e) {
        const submitButton = passwordForm.querySelector('button[type="submit"]');
        
        // Validation
        if (oldPassword && newPassword1 && newPassword2) {
            if (!oldPassword.value || !newPassword1.value || !newPassword2.value) {
                e.preventDefault();
                showNotification('Please fill in all password fields', 'error');
                return;
            }
            if (newPassword1.value !== newPassword2.value) {
                e.preventDefault();
                showNotification('New passwords do not match', 'error');
                return;
            }
            if (newPassword1.value.length < 8) {
                e.preventDefault();
                showNotification('Password must be at least 8 characters long', 'error');
                return;
            }
        }
        
        // Loading state
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="bi bi-hourglass-split animate-spin"></i> Updating Password...';
            
            setTimeout(() => {
                if (submitButton.disabled) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }
            }, 10000);
        }
    });
}

/**
 * Profile Details Form Validation
 */
function initializeDetailsForm() {
    const detailsForm = document.getElementById('details-form');
    if (!detailsForm) return;
    
    const emailInput = detailsForm.querySelector('[name="email"]');
    
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (emailInput.value && !validateEmail(emailInput.value)) {
                emailInput.classList.add('border-red-500');
                showNotification('Please enter a valid email address', 'error');
            } else if (emailInput.value) {
                emailInput.classList.remove('border-red-500');
                emailInput.classList.add('border-green-500');
            }
        });
        
        emailInput.addEventListener('input', function() {
            emailInput.classList.remove('border-red-500', 'border-green-500');
        });
    }
    
    // Form submission
    detailsForm.addEventListener('submit', function(e) {
        const submitButton = detailsForm.querySelector('button[type="submit"]');
        
        if (emailInput && (!emailInput.value || !validateEmail(emailInput.value))) {
            e.preventDefault();
            showNotification('Please enter a valid email address', 'error');
            return;
        }
        
        // Loading state
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="bi bi-hourglass-split animate-spin"></i> Saving Changes...';
            
            setTimeout(() => {
                if (submitButton.disabled) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }
            }, 10000);
        }
    });
}

/**
 * Responsive Features (Auto-hide messages)
 */
function initializeResponsiveFeatures() {
    const messages = document.querySelectorAll('[id^="message-alert-"]');
    messages.forEach((message, index) => {
        const closeButton = message.querySelector('button');
        
        const removeMessage = () => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            setTimeout(() => message.remove(), 500);
        };
        
        const timer = setTimeout(removeMessage, 5000 + (index * 500));
        
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                clearTimeout(timer);
                removeMessage();
            });
        }
    });
}

/**
 * Auto-hide Alert Messages (for all pages)
 */
function initializeAlertMessages() {
    const messages = document.querySelectorAll('[id^="message-alert-"]');
    messages.forEach((message, index) => {
        const closeButton = message.querySelector('button[type="button"]');
        
        const removeMessage = () => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            setTimeout(() => message.remove(), 500);
        };
        
        // Auto-hide after 5 seconds
        const timer = setTimeout(removeMessage, 5000 + (index * 500));
        
        // Allow manual close
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                clearTimeout(timer);
                removeMessage();
            });
        }
    });
}

/**
 * Utility Functions
 */
function calculatePasswordStrength(password) {
    let strength = 0;
    if (!password) return 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
}

function updatePasswordStrengthUI(input, strength) {
    let indicator = input.parentElement.querySelector('.password-strength');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength text-xs mt-1';
        input.parentElement.appendChild(indicator);
    }
    
    if (!input.value) {
        indicator.innerHTML = '';
        return;
    }
    
    const strengthLevels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['text-red-600', 'text-orange-600', 'text-yellow-600', 'text-blue-600', 'text-green-600'];
    const levelIndex = Math.max(0, strength - 1);
    
    indicator.innerHTML = `Password Strength: <span class="${strengthColors[levelIndex]} font-semibold">${strengthLevels[levelIndex]}</span>`;
}

function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 z-50 p-4 rounded-xl shadow-lg max-w-md ${
        type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
        type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
        'bg-blue-100 border border-blue-300 text-blue-800'
    }`;
    notification.style.transform = 'translateX(110%)';
    notification.style.opacity = '0';
    notification.style.transition = 'transform 0.3s ease-out, opacity 0.3s ease-out';
    
    notification.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <i class="bi bi-${type === 'success' ? 'check-circle-fill' : type === 'error' ? 'exclamation-triangle-fill' : 'info-circle-fill'} text-xl mr-3"></i>
                <span class="font-medium">${message}</span>
            </div>
            <button type="button" class="ml-4 text-2xl font-bold leading-none hover:opacity-70">
                &times;
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);

    const removeNotification = () => {
        notification.style.transform = 'translateX(110%)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    };

    const timer = setTimeout(removeNotification, 5000);

    notification.querySelector('button').addEventListener('click', () => {
        clearTimeout(timer);
        removeNotification();
    });
}

// Add spin animation CSS if not already present
if (!document.getElementById('spin-animation-style')) {
    const style = document.createElement('style');
    style.id = 'spin-animation-style';
    style.textContent = `
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .animate-spin {
            animation: spin 1s linear infinite;
        }
    `;
    document.head.appendChild(style);
}