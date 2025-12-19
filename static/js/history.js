// ============================================
// BLOOMERS - Enhanced History Page JavaScript
// ============================================

(function() {
    'use strict';

    // ==========================================
    // 1. DOM ELEMENT REFERENCES
    // ==========================================
    const elements = {
        mobileMenuButton: document.getElementById('mobile-menu-button'),
        mobileMenu: document.getElementById('mobile-menu'),
        searchInput: document.getElementById('search-input'),
        sortSelect: document.getElementById('sort-select'),
        tableBody: document.getElementById('table-body'),
        deleteModal: document.getElementById('delete-modal'),
        confirmDeleteBtn: document.getElementById('confirm-delete-btn'),
        cancelDeleteBtn: document.getElementById('cancel-delete-btn'),
        deleteFilename: document.getElementById('delete-filename'),
        profileMenuButton: document.getElementById('profile-menu-button'),
        profileMenuDropdown: document.getElementById('profile-menu-dropdown'),
        historyTable: document.getElementById('history-table'),
        messagesContainer: document.getElementById('messages-container'),

        // Filter elements
        filterToggleBtn: document.getElementById('filter-toggle-btn'),
        resetFilterBtn: document.getElementById('reset-filter-btn'),
        filterPanel: document.getElementById('filter-panel'),
        applyFilterBtn: document.getElementById('apply-filter-btn'),

        filterQuestionsMin: document.getElementById('filter-questions-min'),
        filterQuestionsMax: document.getElementById('filter-questions-max'),

        filterDatePreset: document.getElementById('filter-date-preset'),
        filterDateStart: document.getElementById('filter-date-start'),
        filterDateEnd: document.getElementById('filter-date-end'),
        customDateRange: document.getElementById('custom-date-range'),

        filterC1: document.getElementById('filter-c1'),
        filterC2: document.getElementById('filter-c2'),
        filterC3: document.getElementById('filter-c3'),
        filterC4: document.getElementById('filter-c4'),
        filterC5: document.getElementById('filter-c5'),
        filterC6: document.getElementById('filter-c6')
    };
    
    let currentDeleteId = null;
    let searchTimeout = null;
    let allRows = [];

    // ==========================================
    // 2. INITIALIZATION
    // ==========================================
    function init() {
        setupEventListeners();
        setupProfileDropdown();
        enhanceTableRows();
        setupMessages();
        setupKeyboardShortcuts();
        checkTableScroll();
        storeAllRows();
        
        console.log('✓ History page initialized successfully');
    }

    function storeAllRows() {
        allRows = Array.from(elements.tableBody.querySelectorAll('tr[data-id]'));
    }

    // ==========================================
    // 3. EVENT LISTENERS SETUP
    // ==========================================
    function setupEventListeners() {

        if (elements.applyFilterBtn) {
            elements.applyFilterBtn.addEventListener('click', () => {
                applyFilters();
                toggleFilterPanel();
            });
        }
        // Mobile menu toggle
        if (elements.mobileMenuButton) {
            elements.mobileMenuButton.addEventListener('click', toggleMobileMenu);
        }

        // Search functionality with debounce
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', handleSearch);
        }

        // Sort functionality
        if (elements.sortSelect) {
            elements.sortSelect.addEventListener('change', handleSort);
        }

        // Delete buttons
        setupDeleteButtons();

        // Modal controls
        if (elements.cancelDeleteBtn) {
            elements.cancelDeleteBtn.addEventListener('click', closeDeleteModal);
        }

        if (elements.confirmDeleteBtn) {
            elements.confirmDeleteBtn.addEventListener('click', confirmDelete);
        }

        // Close modal on backdrop click
        if (elements.deleteModal) {
            elements.deleteModal.addEventListener('click', handleModalBackdropClick);
        }

        // Window resize handler
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(checkTableScroll, 250);
        });

         // Toggle filter panel
        if (elements.filterToggleBtn) {
            elements.filterToggleBtn.addEventListener('click', toggleFilterPanel);
        }

        // Reset filters
        if (elements.resetFilterBtn) {
            elements.resetFilterBtn.addEventListener('click', resetFilters);
        }

        // Date preset change
        if (elements.filterDatePreset) {
            elements.filterDatePreset.addEventListener('change', handleDatePresetChange);
        }
    }

    // ==========================================
    // FILTER FUNCTIONALITY
    // ==========================================
    function toggleFilterPanel() {
    if (!elements.filterPanel) return;

    elements.filterPanel.classList.toggle('active');
    }

    function handleDatePresetChange() {
        const preset = elements.filterDatePreset.value;
        
        if (preset === 'custom') {
            elements.customDateRange.classList.remove('hidden');
        } else {
            elements.customDateRange.classList.add('hidden');
            elements.filterDateStart.value = '';
            elements.filterDateEnd.value = '';
        }
    }

    function applyFilters() {
        const filters = getFilterValues();
        let visibleCount = 0;
        
        // Remove existing "no results" message
        const existingMsg = elements.tableBody.querySelector('.no-results-row');
        if (existingMsg) existingMsg.remove();
        
        allRows.forEach(row => {
            const shouldShow = checkRowMatchesFilters(row, filters);
            
            if (shouldShow) {
                row.style.display = '';
                row.style.animation = 'fadeIn 0.3s ease-out';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update row numbers
        updateRowNumbers();
        
        // Show notification
        if (visibleCount === 0) {
            showNoResultsMessage();
            showNotification('No results match your filters', 'info');
        } else {
            showNotification(`✓ Showing ${visibleCount} result${visibleCount > 1 ? 's' : ''}`, 'success');
        }
        
        // Close filter panel
        toggleFilterPanel();
    }

    /**
     * Get all filter values
     */
    function getFilterValues() {
        return {
            questionsMin: elements.filterQuestionsMin.value ? parseInt(elements.filterQuestionsMin.value) : null,
            questionsMax: elements.filterQuestionsMax.value ? parseInt(elements.filterQuestionsMax.value) : null,
            datePreset: elements.filterDatePreset.value,
            dateStart: elements.filterDateStart.value,
            dateEnd: elements.filterDateEnd.value,
            c1: elements.filterC1.checked,
            c2: elements.filterC2.checked,
            c3: elements.filterC3.checked,
            c4: elements.filterC4.checked,
            c5: elements.filterC5.checked,
            c6: elements.filterC6.checked
        };
    }

    /**
     * Check if row matches all active filters
     */
    function checkRowMatchesFilters(row, filters) {
        // Questions filter
        if (filters.questionsMin !== null || filters.questionsMax !== null) {
            const questions = parseInt(row.dataset.questions);
            
            if (filters.questionsMin !== null && questions < filters.questionsMin) {
                return false;
            }
            
            if (filters.questionsMax !== null && questions > filters.questionsMax) {
                return false;
            }
        }
        
        // Date filter
        if (filters.datePreset || filters.dateStart || filters.dateEnd) {
            const rowDate = new Date(row.dataset.date);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (filters.datePreset === 'today') {
                const rowDateOnly = new Date(rowDate);
                rowDateOnly.setHours(0, 0, 0, 0);
                if (rowDateOnly.getTime() !== today.getTime()) {
                    return false;
                }
            } else if (filters.datePreset === '7days') {
                const sevenDaysAgo = new Date(today);
                sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                if (rowDate < sevenDaysAgo) {
                    return false;
                }
            } else if (filters.datePreset === '30days') {
                const thirtyDaysAgo = new Date(today);
                thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                if (rowDate < thirtyDaysAgo) {
                    return false;
                }
            } else if (filters.datePreset === 'custom') {
                if (filters.dateStart) {
                    const startDate = new Date(filters.dateStart);
                    if (rowDate < startDate) {
                        return false;
                    }
                }
                if (filters.dateEnd) {
                    const endDate = new Date(filters.dateEnd);
                    endDate.setHours(23, 59, 59, 999);
                    if (rowDate > endDate) {
                        return false;
                    }
                }
            }
        }
        
        // Bloom's Taxonomy filter (C1-C6)
        const anyBloomChecked = filters.c1 || filters.c2 || filters.c3 || 
                               filters.c4 || filters.c5 || filters.c6;
        
        if (anyBloomChecked) {
            let hasMatchingBloom = false;
            
            if (filters.c1 && parseInt(row.dataset.c1) > 0) hasMatchingBloom = true;
            if (filters.c2 && parseInt(row.dataset.c2) > 0) hasMatchingBloom = true;
            if (filters.c3 && parseInt(row.dataset.c3) > 0) hasMatchingBloom = true;
            if (filters.c4 && parseInt(row.dataset.c4) > 0) hasMatchingBloom = true;
            if (filters.c5 && parseInt(row.dataset.c5) > 0) hasMatchingBloom = true;
            if (filters.c6 && parseInt(row.dataset.c6) > 0) hasMatchingBloom = true;
            
            if (!hasMatchingBloom) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Reset all filters
     */
    function resetFilters() {
        // Clear filter inputs
        elements.filterQuestionsMin.value = '';
        elements.filterQuestionsMax.value = '';
        elements.filterDatePreset.value = '';
        elements.filterDateStart.value = '';
        elements.filterDateEnd.value = '';
        elements.customDateRange.classList.add('hidden');
        
        // Uncheck all Bloom's taxonomy checkboxes
        elements.filterC1.checked = false;
        elements.filterC2.checked = false;
        elements.filterC3.checked = false;
        elements.filterC4.checked = false;
        elements.filterC5.checked = false;
        elements.filterC6.checked = false;
        
        // Show all rows
        allRows.forEach(row => {
            row.style.display = '';
        });
        
        // Remove "no results" message
        const existingMsg = elements.tableBody.querySelector('.no-results-row');
        if (existingMsg) existingMsg.remove();
        
        // Update row numbers
        updateRowNumbers();
        
        // Close filter panel if open
        if (elements.filterPanel.classList.contains('active')) {
            toggleFilterPanel();
        }
        
        showNotification('✓ Filters reset successfully', 'success');
        window.resetFilters = resetFilters;
    }

    /**
     * Show "no results" message
     */
    function showNoResultsMessage() {
        const noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `
            <td colspan="11" class="px-6 py-12 text-center">
                <i class="bi bi-funnel text-5xl text-gray-300 dark:text-gray-600 mb-3 block"></i>
                <p class="text-lg font-medium text-gray-700 dark:text-gray-300">No results match your filters</p>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Try adjusting your filter criteria</p>
                <button onclick="window.resetFilters()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all">
                    Reset Filters
                </button>
            </td>
        `;
        elements.tableBody.appendChild(noResultsRow);
    }

    // ==========================================
    // 4. PROFILE DROPDOWN
    // ==========================================
    function setupProfileDropdown() {
        if (!elements.profileMenuButton || !elements.profileMenuDropdown) {
            return;
        }

        elements.profileMenuButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isHidden = elements.profileMenuDropdown.classList.contains('hidden');
            elements.profileMenuDropdown.classList.toggle('hidden');
            
            // Close mobile menu if open
            if (elements.mobileMenu && !elements.mobileMenu.classList.contains('hidden')) {
                elements.mobileMenu.classList.add('hidden');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!elements.profileMenuButton.contains(e.target) && 
                !elements.profileMenuDropdown.contains(e.target)) {
                if (!elements.profileMenuDropdown.classList.contains('hidden')) {
                    elements.profileMenuDropdown.classList.add('hidden');
                }
            }
        });
    }

    // ==========================================
    // 5. MOBILE MENU
    // ==========================================
    function toggleMobileMenu() {
        if (elements.mobileMenu) {
            elements.mobileMenu.classList.toggle('hidden');
        }
    }

    // ==========================================
    // 6. SEARCH FUNCTIONALITY
    // ==========================================
    function handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        // Debounce search
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(searchTerm);
        }, 300);
    }

    function performSearch(searchTerm) {
        const rows = elements.tableBody.querySelectorAll('tr[data-id]');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const filename = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
            const isVisible = filename.includes(searchTerm);
            
            if (isVisible) {
                row.style.display = '';
                row.style.animation = 'fadeIn 0.3s ease-out';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Show "no results" message if needed
        updateNoResultsMessage(visibleCount, searchTerm);
    }

    function updateNoResultsMessage(visibleCount, searchTerm) {
        // Remove existing message
        const existingMsg = elements.tableBody.querySelector('.no-results-row');
        if (existingMsg) {
            existingMsg.remove();
        }

        // Add message if no results
        if (visibleCount === 0 && searchTerm) {
            const noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            noResultsRow.innerHTML = `
                <td colspan="11" class="px-6 py-12 text-center">
                    <i class="bi bi-search text-5xl text-gray-300 mb-3 block"></i>
                    <p class="text-lg font-medium text-gray-700">No results found for "${searchTerm}"</p>
                    <p class="text-sm text-gray-500 mt-2">Try adjusting your search terms</p>
                </td>
            `;
            elements.tableBody.appendChild(noResultsRow);
        }
    }

    // ==========================================
    // 7. SORT FUNCTIONALITY
    // ==========================================
    function handleSort() {
        const sortValue = elements.sortSelect.value;
        const rows = Array.from(elements.tableBody.querySelectorAll('tr[data-id]'));
        
        rows.sort((a, b) => {
            switch(sortValue) {
                case 'date-desc':
                    return compareElements(b, a, 4, 'date');
                case 'date-asc':
                    return compareElements(a, b, 4, 'date');
                case 'questions-desc':
                    return compareElements(b, a, 3, 'number');
                case 'questions-asc':
                    return compareElements(a, b, 3, 'number');
                case 'name-asc':
                    return compareElements(a, b, 2, 'text');
                case 'name-desc':
                    return compareElements(b, a, 2, 'text');
                default:
                    return 0;
            }
        });
        
        // Clear and re-append sorted rows
        rows.forEach(row => elements.tableBody.appendChild(row));
        
        // Update row numbers
        updateRowNumbers();
        
        // Show notification
        showNotification('✓ Table sorted successfully', 'success');
    }

    function compareElements(a, b, columnIndex, type) {
        const aText = a.querySelector(`td:nth-child(${columnIndex})`)?.textContent.trim() || '';
        const bText = b.querySelector(`td:nth-child(${columnIndex})`)?.textContent.trim() || '';
        
        if (type === 'number') {
            const aNum = parseInt(aText.replace(/\D/g, ''));
            const bNum = parseInt(bText.replace(/\D/g, ''));
            return aNum - bNum;
        } else if (type === 'date') {
            return new Date(bText) - new Date(aText);
        } else {
            return aText.localeCompare(bText);
        }
    }

    function updateRowNumbers() {
        const visibleRows = Array.from(elements.tableBody.querySelectorAll('tr[data-id]'))
            .filter(row => row.style.display !== 'none');
        
        visibleRows.forEach((row, index) => {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell) {
                firstCell.textContent = index + 1;
            }
        });
    }

    // ==========================================
    // 8. DELETE FUNCTIONALITY
    // ==========================================
    function setupDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-btn');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentDeleteId = this.getAttribute('data-id');
                const filename = this.getAttribute('data-filename');
                
                if (elements.deleteFilename) {
                    elements.deleteFilename.textContent = filename;
                }
                
                openDeleteModal();
            });
        });
    }

    function openDeleteModal() {
        if (elements.deleteModal) {
            elements.deleteModal.classList.remove('hidden');
            elements.deleteModal.style.animation = 'fadeIn 0.3s ease-out';
        }
    }

    function closeDeleteModal() {
        if (elements.deleteModal) {
            elements.deleteModal.classList.add('hidden');
            currentDeleteId = null;
        }
    }

    function handleModalBackdropClick(e) {
        if (e.target === elements.deleteModal) {
            closeDeleteModal();
        }
    }

    function confirmDelete() {
        if (!currentDeleteId) return;
        
        // Show loading state
        elements.confirmDeleteBtn.disabled = true;
        elements.confirmDeleteBtn.innerHTML = `
            <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Deleting...
        `;
        
        // Create form and submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/klasifikasi/delete/${currentDeleteId}/`;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    }

    // ==========================================
    // 9. TABLE ENHANCEMENTS
    // ==========================================
    function enhanceTableRows() {
        const rows = elements.tableBody?.querySelectorAll('tr[data-id]');
        
        rows?.forEach(row => {
            // Add hover animation
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.01)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    function checkTableScroll() {
        const tableContainer = document.querySelector('.overflow-x-auto');
        if (!tableContainer) return;
        
        const table = tableContainer.querySelector('table');
        if (!table) return;
        
        const isScrollable = table.scrollWidth > tableContainer.clientWidth;
        
        if (isScrollable) {
            tableContainer.classList.add('shadow-inner');
            // Show scroll indicator
            if (!tableContainer.querySelector('.scroll-indicator')) {
                const indicator = document.createElement('div');
                indicator.className = 'scroll-indicator text-center text-xs text-gray-500 py-2';
                indicator.innerHTML = '<i class="bi bi-arrow-left-right"></i> Scroll horizontally to see more';
                tableContainer.appendChild(indicator);
            }
        } else {
            tableContainer.classList.remove('shadow-inner');
            const indicator = tableContainer.querySelector('.scroll-indicator');
            if (indicator) indicator.remove();
        }
    }

    // ==========================================
    // 10. MESSAGES HANDLING
    // ==========================================
    function setupMessages() {
        // Close message buttons
        const closeMessageButtons = document.querySelectorAll('.close-message');
        closeMessageButtons.forEach(button => {
            button.addEventListener('click', function() {
                const alert = this.closest('[role="alert"]');
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => alert.remove(), 300);
            });
        });

        // Auto-hide messages after 5 seconds
        const messages = document.querySelectorAll('[role="alert"]');
        messages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }

    /**
     * Show notification message
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'info'
     */
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 max-w-md p-4 rounded-xl shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
            type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
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
        
        // Auto-remove after 3 seconds
        const timer = setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
        
        // Remove on click
        notification.querySelector('button').addEventListener('click', () => {
            clearTimeout(timer);
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        });
    }

    // ==========================================
    // 11. KEYBOARD SHORTCUTS
    // ==========================================
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modal
            if (e.key === 'Escape') {
                if (elements.deleteModal && !elements.deleteModal.classList.contains('hidden')) {
                    closeDeleteModal();
                }
            }
            
            // Ctrl/Cmd + F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f' && elements.searchInput) {
                e.preventDefault();
                elements.searchInput.focus();
                elements.searchInput.select();
            }

            // Ctrl/Cmd + K to focus search (alternative)
            if ((e.ctrlKey || e.metaKey) && e.key === 'k' && elements.searchInput) {
                e.preventDefault();
                elements.searchInput.focus();
                elements.searchInput.select();
            }
        });
    }

    // ==========================================
    // 12. UTILITY FUNCTIONS
    // ==========================================

    /**
     * Export table to CSV
     */
    window.exportToCSV = function() {
        const rows = document.querySelectorAll('#history-table tr');
        let csv = [];
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const rowData = Array.from(cells).map(cell => {
                return '"' + cell.textContent.trim().replace(/"/g, '""') + '"';
            });
            csv.push(rowData.join(','));
        });
        
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `classification_history_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('✓ Table exported to CSV successfully', 'success');
    };

    /**
     * Print table
     */
    window.printTable = function() {
        window.print();
    };

    /**
     * Refresh page
     */
    window.refreshPage = function() {
        const icon = document.querySelector('.bi-arrow-clockwise');
        if (icon) {
            icon.classList.add('animate-spin');
        }
        setTimeout(() => location.reload(), 500);
    };

    // ==========================================
    // 13. INITIALIZATION
    // ==========================================
    
    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();