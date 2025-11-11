/* ===================================
   TIP MDS EMR - Utility Functions
   =================================== */

// Get current date formatted
function getCurrentDate() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date().toLocaleDateString('en-US', options);
}

// Update date display in top bar
function updateDateDisplay() {
    const dateDisplays = document.querySelectorAll('.date-display');
    dateDisplays.forEach(display => {
        display.textContent = getCurrentDate();
    });
}

// Show notification/alert
function showNotification(message, type = 'success') {
    alert(message); // Replace with custom notification system
}

// Format date to readable format
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate phone number (Philippine format)
function isValidPhone(phone) {
    const phoneRegex = /^(\+63|0)?[0-9]{10}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Get element by ID safely
function getElement(id) {
    return document.getElementById(id);
}

// Get elements by class name
function getElements(className) {
    return document.querySelectorAll(className);
}

// Add event listener safely
function addEvent(element, event, handler) {
    if (element) {
        element.addEventListener(event, handler);
    }
}

// Remove all active classes
function removeActiveClasses(elements) {
    elements.forEach(element => {
        element.classList.remove('active');
    });
}

// Toggle class
function toggleClass(element, className) {
    if (element) {
        element.classList.toggle(className);
    }
}

// Show element
function showElement(element) {
    if (element) {
        element.style.display = 'block';
        element.classList.add('active');
    }
}

// Hide element
function hideElement(element) {
    if (element) {
        element.style.display = 'none';
        element.classList.remove('active');
    }
}

// Initialize tooltips (if needed)
function initTooltips() {
    // Tooltip initialization code
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateDateDisplay();
    console.log('TIP MDS EMR System Initialized');
});