/**
 * Task Tracker Pro - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Task status update confirmation
    const statusForms = document.querySelectorAll('.status-update-form');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const newStatus = this.querySelector('input[name="status"]').value;
            if (!confirm(`Are you sure you want to change the status to "${newStatus}"?`)) {
                e.preventDefault();
            }
        });
    });

    // Task filter functionality
    const filterButtons = document.querySelectorAll('.task-filter');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.dataset.filter;
            const taskRows = document.querySelectorAll('.task-row');
            
            // Update active filter button
            document.querySelectorAll('.task-filter').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Show/hide tasks based on filter
            if (filter === 'all') {
                taskRows.forEach(row => {
                    row.style.display = '';
                });
            } else if (filter === 'priority') {
                const priority = this.dataset.priority;
                taskRows.forEach(row => {
                    if (row.dataset.priority === priority) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            } else if (filter === 'status') {
                const status = this.dataset.status;
                taskRows.forEach(row => {
                    if (row.dataset.status === status) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            } else if (filter === 'overdue') {
                taskRows.forEach(row => {
                    if (row.dataset.overdue === 'true') {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Task search functionality
    const searchInput = document.getElementById('task-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const taskRows = document.querySelectorAll('.task-row');
            
            taskRows.forEach(row => {
                const title = row.querySelector('.task-title').textContent.toLowerCase();
                const description = row.dataset.description.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Due date picker enhancement
    const dueDateInputs = document.querySelectorAll('input[type="date"]');
    dueDateInputs.forEach(input => {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });

    // Task detail page - toggle history log
    const historyToggle = document.getElementById('history-toggle');
    if (historyToggle) {
        historyToggle.addEventListener('click', function() {
            const historyLog = document.getElementById('history-log');
            if (historyLog.style.display === 'none') {
                historyLog.style.display = 'block';
                this.textContent = 'Hide History';
            } else {
                historyLog.style.display = 'none';
                this.textContent = 'Show History';
            }
        });
    }
});
