// Main JavaScript for Missing Person Detection System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File upload validation
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('File size must be less than 16MB', 'danger');
                    e.target.value = '';
                    return;
                }

                // Check file type
                var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    showAlert('Please upload a valid image file (PNG, JPG, JPEG, or GIF)', 'danger');
                    e.target.value = '';
                    return;
                }

                // Show file info
                showFileInfo(file, e.target);
            }
        });
    });

    // Search functionality
    var searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            var inputs = searchForm.querySelectorAll('input, select');
            var hasValue = false;
            
            inputs.forEach(function(input) {
                if (input.value.trim() !== '') {
                    hasValue = true;
                }
            });

            if (!hasValue) {
                e.preventDefault();
                showAlert('Please enter at least one search criteria', 'warning');
            }
        });
    }

    // Loading states for forms
    var submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
            button.disabled = true;
        });
    });

    // Smooth scrolling for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Copy to clipboard functionality
    var copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var text = this.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(function() {
                showAlert('Copied to clipboard!', 'success');
            });
        });
    });

    // Auto-refresh for admin dashboard
    if (window.location.pathname.includes('/admin/dashboard')) {
        setInterval(function() {
            // Refresh detection data every 30 seconds
            fetch('/admin/dashboard')
                .then(response => response.text())
                .then(html => {
                    // Update only the detection table
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var newTable = doc.querySelector('.table');
                    var currentTable = document.querySelector('.table');
                    if (newTable && currentTable) {
                        currentTable.parentNode.replaceChild(newTable, currentTable);
                    }
                })
                .catch(error => console.log('Auto-refresh failed:', error));
        }, 30000);
    }
});

// Utility functions
function showAlert(message, type) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    var container = document.querySelector('.container:first-of-type') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        var alert = container.querySelector('.alert:first-child');
        if (alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function showFileInfo(file, input) {
    var fileSize = (file.size / 1024 / 1024).toFixed(2);
    var fileName = file.name;
    
    // Create or update file info display
    var infoDiv = input.parentNode.querySelector('.file-info') || document.createElement('div');
    infoDiv.className = 'file-info mt-2 text-muted small';
    infoDiv.innerHTML = `
        <i class="fas fa-file-image me-1"></i>
        ${fileName} (${fileSize} MB)
    `;
    
    if (!input.parentNode.querySelector('.file-info')) {
        input.parentNode.appendChild(infoDiv);
    }
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Image preview functionality
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Export functions for global use
window.showAlert = showAlert;
window.confirmAction = confirmAction;
window.previewImage = previewImage;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;

// Handle network errors
window.addEventListener('online', function() {
    showAlert('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showAlert('Connection lost. Some features may not work properly.', 'warning');
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            var loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            if (loadTime > 3000) {
                console.warn('Page load time:', loadTime + 'ms');
            }
        }, 0);
    });
}

// Error handling for AJAX requests
function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    showAlert('An error occurred. Please try again.', 'danger');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+/ or Cmd+/ to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        var searchInput = document.querySelector('input[name="search"], input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        var openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(function(modal) {
            var bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

// Lazy loading for images
if ('IntersectionObserver' in window) {
    var imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(function(img) {
        imageObserver.observe(img);
    });
}
