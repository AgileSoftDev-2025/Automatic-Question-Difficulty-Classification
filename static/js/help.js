// ===================================
// FILE: help.js
// Enhanced FAQ Accordion with Smooth Animations
// ===================================

(function() {
    'use strict';

    // ========== FAQ Accordion with Smooth Animation ==========
    function initFAQAccordion() {
        const faqButtons = document.querySelectorAll('.faq-button');

        faqButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Get the answer panel (next sibling element)
                const panel = button.nextElementSibling;
                // Get the icon inside the button
                const icon = button.querySelector('i');

                // Check if this panel is currently open
                const isPanelOpen = !panel.classList.contains('hidden');

                // --- Close all other panels for cleaner UI ---
                // Remove these lines if you want multiple answers open at once
                faqButtons.forEach(otherButton => {
                    if (otherButton !== button) {
                        const otherPanel = otherButton.nextElementSibling;
                        const otherIcon = otherButton.querySelector('i');

                        // Close other panels with animation
                        otherPanel.classList.remove('active');
                        otherPanel.classList.add('hidden');
                        
                        // Reset icon
                        otherIcon.classList.remove('bi-dash-circle', 'rotate-180');
                        otherIcon.classList.add('bi-plus-circle');
                    }
                });
                // --- End of closing other panels logic ---

                // Toggle the clicked panel
                if (isPanelOpen) {
                    // Close the panel
                    panel.classList.remove('active');
                    setTimeout(() => {
                        panel.classList.add('hidden');
                    }, 300); // Wait for animation to complete
                    
                    // Change icon
                    icon.classList.remove('bi-dash-circle', 'rotate-180');
                    icon.classList.add('bi-plus-circle');
                } else {
                    // Open the panel
                    panel.classList.remove('hidden');
                    // Trigger reflow to enable animation
                    void panel.offsetHeight;
                    panel.classList.add('active');
                    
                    // Change icon
                    icon.classList.remove('bi-plus-circle');
                    icon.classList.add('bi-dash-circle', 'rotate-180');
                }

                // Add pulse animation to button for better feedback
                button.classList.add('scale-105');
                setTimeout(() => button.classList.remove('scale-105'), 200);
            });
        });

        console.log('✓ FAQ accordion initialized with', faqButtons.length, 'items');
    }

    // ========== Smooth Scroll to Hash ==========
    function initSmoothScroll() {
        // If URL has a hash, scroll to it smoothly
        if (window.location.hash) {
            setTimeout(() => {
                const element = document.querySelector(window.location.hash);
                if (element) {
                    element.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }
            }, 100);
        }
    }

    // ========== Keyboard Accessibility ==========
    function initKeyboardAccessibility() {
        const faqButtons = document.querySelectorAll('.faq-button');
        
        faqButtons.forEach(button => {
            // Make sure buttons are keyboard accessible
            button.setAttribute('role', 'button');
            button.setAttribute('aria-expanded', 'false');
            
            // Handle Enter and Space key presses
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });

            // Update aria-expanded on click
            button.addEventListener('click', () => {
                const panel = button.nextElementSibling;
                const isExpanded = !panel.classList.contains('hidden');
                button.setAttribute('aria-expanded', isExpanded);
            });
        });
    }

    // ========== Auto-expand from URL Parameter ==========
    function handleURLParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const expandItem = urlParams.get('expand');
        
        if (expandItem) {
            const faqButtons = document.querySelectorAll('.faq-button');
            const index = parseInt(expandItem);
            
            if (!isNaN(index) && index >= 0 && index < faqButtons.length) {
                setTimeout(() => {
                    faqButtons[index].click();
                    faqButtons[index].scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 300);
            }
        }
    }

    // ========== Search/Filter FAQ Items ==========
    function initFAQSearch() {
        // Create search input if it doesn't exist
        const faqAccordion = document.getElementById('faq-accordion');
        if (!faqAccordion) return;

        // Add search functionality (optional enhancement)
        // You can uncomment this if you want to add a search bar later
        /*
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search FAQ...';
        searchInput.className = 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 mb-6';
        faqAccordion.parentElement.insertBefore(searchInput, faqAccordion);
        
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const faqItems = faqAccordion.querySelectorAll('.border-b');
            
            faqItems.forEach(item => {
                const question = item.querySelector('.faq-button span').textContent.toLowerCase();
                const answer = item.querySelector('.faq-panel').textContent.toLowerCase();
                
                if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
        */
    }

    // ========== Add Transition Classes ==========
    function addTransitionStyles() {
        // Add CSS transition styles for smooth animations
        const style = document.createElement('style');
        style.textContent = `
            .faq-button {
                transition: all 0.2s ease;
            }
            
            .faq-button:hover {
                background-color: rgba(59, 130, 246, 0.05);
            }
            
            .dark .faq-button:hover {
                background-color: rgba(59, 130, 246, 0.1);
            }
            
            .faq-button i {
                transition: transform 0.3s ease;
            }
            
            .faq-panel {
                transition: all 0.3s ease-in-out;
                max-height: 0;
                overflow: hidden;
                opacity: 0;
            }
            
            .faq-panel.active {
                max-height: 1000px;
                opacity: 1;
            }
            
            .rotate-180 {
                transform: rotate(180deg);
            }
            
            .scale-105 {
                transform: scale(1.05);
            }
        `;
        document.head.appendChild(style);
    }

    // ========== Initialize Everything ==========
    function init() {
        addTransitionStyles();
        initFAQAccordion();
        initKeyboardAccessibility();
        initSmoothScroll();
        handleURLParameters();
        initFAQSearch();
        
        console.log('✓ Help page JavaScript loaded successfully');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();