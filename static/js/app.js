/**
 * Omnify Application JavaScript
 * Professional, Enterprise-Grade UI Interactions
 */

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Omnify initialized');
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add active class to current nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Utility functions
const Omnify = {
    // Show toast notification
    showToast: function(message, type = 'info') {
        // TODO: Implement toast notifications
        console.log(`[${type.toUpperCase()}] ${message}`);
    },
    
    // Confirm action
    confirm: function(message) {
        return window.confirm(message);
    },
    
    // Format currency
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Format date
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }
};

// Export for use in other scripts
window.Omnify = Omnify;
