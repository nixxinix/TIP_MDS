/* ===================================
   TIP MDS EMR - Navigation & Routing
   =================================== */

// Show specific section
function showSection(sectionId) {
    // Hide all content sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update active nav link
    updateActiveNavLink(event);
}

// Update active navigation link
function updateActiveNavLink(event) {
    if (event && event.target) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => link.classList.remove('active'));
        
        const clickedLink = event.target.closest('.nav-link');
        if (clickedLink) {
            clickedLink.classList.add('active');
        }
    }
}

// Switch tabs within a section
function switchTab(event, tabId) {
    // Get parent container to scope tabs
    const container = event.target.closest('.table-container, .form-container');
    
    if (!container) return;
    
    // Hide all tab contents in this container
    const tabContents = container.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs in this container
    const tabs = container.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// Toggle mobile sidebar
function toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('mobile-open');
    }
    
    if (overlay) {
        overlay.classList.toggle('active');
    }
}

// Close mobile sidebar when clicking overlay
function closeMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.remove('mobile-open');
    }
    
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Initialize navigation
function initNavigation() {
    // Add click handlers to nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const sectionId = this.getAttribute('onclick');
            if (sectionId) {
                e.preventDefault();
            }
        });
    });
    
    // Add click handler to mobile overlay
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', closeMobileSidebar);
    }
}

// Go back function
function goBack() {
    window.history.back();
}

// Navigate to specific page
function navigateTo(page) {
    window.location.href = page;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initNavigation);