document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Show/Hide Password Functionality ---
    const passwordInput = document.getElementById('password-input');
    const toggleButton = document.getElementById('password-toggle');

    if (passwordInput && toggleButton) {
        toggleButton.addEventListener('click', () => {
            // Toggle input type
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Toggle icon
            const icon = toggleButton.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    }

    // --- 2. Loading State on Form Submit ---
    const loginForm = document.getElementById('login-form');
    const submitButton = document.getElementById('login-submit-btn');

    if (loginForm && submitButton) {
        loginForm.addEventListener('submit', () => {
            // Disable button
            submitButton.disabled = true;
            
            // Change text and add spinner
            submitButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing In...
            `;
        });
    }

});