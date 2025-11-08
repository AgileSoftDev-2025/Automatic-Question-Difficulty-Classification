/**
 * Debug Verification Script
 * Add this temporarily to home.html to diagnose dropdown issues
 * Place this BEFORE nav.js and home.js
 */

(function() {
    console.log('=== BLOOMERS DEBUG VERIFICATION ===');
    
    // Check if we're on the right page
    console.log('Current URL:', window.location.href);
    console.log('Page Title:', document.title);
    
    // Wait for DOM to be ready
    function runDiagnostics() {
        console.log('\n--- DOM Elements Check ---');
        
        // Check profile button
        const profileBtn = document.getElementById('profile-menu-button');
        if (profileBtn) {
            console.log('✓ Profile button found');
            console.log('  - Tag:', profileBtn.tagName);
            console.log('  - Type:', profileBtn.type);
            console.log('  - Classes:', profileBtn.className);
        } else {
            console.error('✗ Profile button NOT FOUND');
            console.log('  Possible reasons:');
            console.log('  1. User is not logged in');
            console.log('  2. Element ID is wrong');
            console.log('  3. Element hasn\'t loaded yet');
        }
        
        // Check profile dropdown
        const profileDropdown = document.getElementById('profile-menu-dropdown');
        if (profileDropdown) {
            console.log('✓ Profile dropdown found');
            console.log('  - Is hidden:', profileDropdown.classList.contains('hidden'));
            console.log('  - Position:', profileDropdown.style.position || 'absolute (from class)');
            console.log('  - Classes:', profileDropdown.className);
        } else {
            console.error('✗ Profile dropdown NOT FOUND');
        }
        
        // Check mobile menu elements
        const mobileBtn = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        console.log(mobileBtn ? '✓ Mobile button found' : '✗ Mobile button NOT found');
        console.log(mobileMenu ? '✓ Mobile menu found' : '✗ Mobile menu NOT found');
        
        console.log('\n--- Authentication Check ---');
        // Check if user is authenticated (profile button exists = logged in)
        if (profileBtn) {
            console.log('✓ User appears to be logged in');
            
            // Try to get username from button
            const usernameSpan = profileBtn.querySelector('span');
            if (usernameSpan) {
                console.log('  Username:', usernameSpan.textContent.trim());
            }
        } else {
            console.log('✗ User appears to be logged out');
            console.log('  The profile dropdown only shows for authenticated users');
        }
        
        console.log('\n--- Event Listener Test ---');
        // Add temporary event listener to profile button
        if (profileBtn) {
            const testListener = function(e) {
                console.log('🎯 BUTTON CLICKED! Event details:');
                console.log('  - Event type:', e.type);
                console.log('  - Target:', e.target);
                console.log('  - Current target:', e.currentTarget);
                console.log('  - Timestamp:', new Date().toLocaleTimeString());
            };
            
            profileBtn.addEventListener('click', testListener);
            console.log('✓ Test event listener added to profile button');
            console.log('  Click the profile button to test...');
        }
        
        console.log('\n--- Script Loading Check ---');
        // Check if scripts are loaded
        const scripts = document.querySelectorAll('script[src]');
        console.log('Loaded external scripts:');
        scripts.forEach((script, index) => {
            const src = script.src;
            if (src.includes('nav.js')) {
                console.log(`  ${index + 1}. nav.js ✓`);
            } else if (src.includes('home.js')) {
                console.log(`  ${index + 1}. home.js ✓`);
            } else if (src.includes('tailwind')) {
                console.log(`  ${index + 1}. Tailwind CSS ✓`);
            } else if (src.includes('bootstrap-icons')) {
                console.log(`  ${index + 1}. Bootstrap Icons ✓`);
            }
        });
        
        console.log('\n--- CSS Check ---');
        if (profileDropdown) {
            const styles = window.getComputedStyle(profileDropdown);
            console.log('Dropdown computed styles:');
            console.log('  - Display:', styles.display);
            console.log('  - Visibility:', styles.visibility);
            console.log('  - Opacity:', styles.opacity);
            console.log('  - Z-index:', styles.zIndex);
        }
        
        console.log('\n=== END DEBUG VERIFICATION ===');
        console.log('If you see errors above, check the troubleshooting guide.');
        console.log('If everything shows ✓, the problem might be with nav.js itself.');
    }
    
    // Run diagnostics when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runDiagnostics);
    } else {
        runDiagnostics();
    }
    
})();