// ===================================
// FILE: history.js
// ===================================

document.addEventListener('DOMContentLoaded', function() {
    // ========== Elements ==========
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const refreshBtn = document.getElementById('refresh-btn');
    const tableBody = document.getElementById('table-body');
    const deleteModal = document.getElementById('delete-modal');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const deleteFilename = document.getElementById('delete-filename');
    
    let currentDeleteId = null;

    // ========== Mobile Menu ==========
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // ========== Search Functionality ==========
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = tableBody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const filename = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase();
                if (filename && filename.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // ========== Sort Functionality ==========
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const rows = Array.from(tableBody.querySelectorAll('tr[data-id]'));
            
            rows.sort((a, b) => {
                switch(sortValue) {
                    case 'date-desc':
                        return compareDates(
                            b.querySelector('td:nth-child(4)').textContent,
                            a.querySelector('td:nth-child(4)').textContent
                        );
                    case 'date-asc':
                        return compareDates(
                            a.querySelector('td:nth-child(4)').textContent,
                            b.querySelector('td:nth-child(4)').textContent
                        );
                    case 'questions-desc':
                        return parseInt(b.querySelector('td:nth-child(3)').textContent) - 
                               parseInt(a.querySelector('td:nth-child(3)').textContent);
                    case 'questions-asc':
                        return parseInt(a.querySelector('td:nth-child(3)').textContent) - 
                               parseInt(b.querySelector('td:nth-child(3)').textContent);
                    default:
                        return 0;
                }
            });
            
            // Clear and re-append sorted rows
            rows.forEach(row => tableBody.appendChild(row));
            
            // Update row numbers
            updateRowNumbers();
        });
    }

    // ========== Date Comparison Helper ==========
    function compareDates(dateStr1, dateStr2) {
        const date1 = parseDate(dateStr1);
        const date2 = parseDate(dateStr2);
        return date1 - date2;
    }

    function parseDate(dateStr) {
        // Assuming format: DD/MM/YYYY
        const parts = dateStr.split('/');
        if (parts.length === 3) {
            return new Date(parts[2], parts[1] - 1, parts[0]);
        }
        return new Date(dateStr);
    }

    // ========== Update Row Numbers ==========
    function updateRowNumbers() {
        const rows = tableBody.querySelectorAll('tr[data-id]');
        rows.forEach((row, index) => {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell) {
                firstCell.textContent = index + 1;
            }
        });
    }

    // ========== Refresh Button ==========
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            // Add spinning animation
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('animate-spin');
            
            // Reload page after short delay for visual feedback
            setTimeout(() => {
                location.reload();
            }, 500);
        });
    }

    // ========== Delete Functionality ==========
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentDeleteId = this.getAttribute('data-id');
            const filename = this.getAttribute('data-filename');
            
            if (deleteFilename) {
                deleteFilename.textContent = filename;
            }
            
            deleteModal.classList.remove('hidden');
        });
    });

    // Cancel delete
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            deleteModal.classList.add('hidden');
            currentDeleteId = null;
        });
    }

    // Close modal when clicking outside
    if (deleteModal) {
        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) {
                deleteModal.classList.add('hidden');
                currentDeleteId = null;
            }
        });
    }

    // Confirm delete
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => {
            if (currentDeleteId) {
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
        });
    }

    // ========== Close Messages ==========
    const closeMessageButtons = document.querySelectorAll('.close-message');
    closeMessageButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('[role="alert"]').remove();
        });
    });

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('[role="alert"]');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });

    // ========== Keyboard Shortcuts ==========
    document.addEventListener('keydown', (e) => {
        // Escape key to close modal
        if (e.key === 'Escape' && !deleteModal.classList.contains('hidden')) {
            deleteModal.classList.add('hidden');
            currentDeleteId = null;
        }
        
        // Ctrl/Cmd + F to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            searchInput?.focus();
        }
    });

    // ========== Tooltips Enhancement ==========
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.setAttribute('data-title', this.title);
            this.removeAttribute('title');
        });
        
        element.addEventListener('mouseleave', function() {
            this.title = this.getAttribute('data-title');
        });
    });

    // ========== Table Row Hover Effect Enhancement ==========
    const tableRows = document.querySelectorAll('tbody tr[data-id]');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // ========== Responsive Table Scroll Indicator ==========
    const tableContainer = document.querySelector('.overflow-x-auto');
    if (tableContainer) {
        const table = tableContainer.querySelector('table');
        
        function updateScrollIndicator() {
            const isScrollable = table.scrollWidth > tableContainer.clientWidth;
            if (isScrollable) {
                tableContainer.classList.add('shadow-inner');
            } else {
                tableContainer.classList.remove('shadow-inner');
            }
        }
        
        updateScrollIndicator();
        window.addEventListener('resize', updateScrollIndicator);
    }

    // ========== Print Functionality (Optional) ==========
    window.printTable = function() {
        window.print();
    };

    // ========== Export to CSV (Optional) ==========
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
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'classification_history.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    };

    console.log('History page JavaScript loaded successfully');
});