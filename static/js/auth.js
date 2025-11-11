/* ===================================
   TIP MDS EMR - Authentication
   =================================== */

let currentRole = 'student';
let currentUser = null;

// Role selection
function selectRole(role) {
    currentRole = role;
    const roleButtons = document.querySelectorAll('.role-btn');
    roleButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.role === role) {
            btn.classList.add('active');
        }
    });
}

// Login function
function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Basic validation
    if (!username || !password) {
        showNotification('Please enter username and password', 'error');
        return;
    }
    
    // Simulate login (replace with actual API call)
    performLogin(username, password);
}

// Perform login
function performLogin(username, password) {
    // This is a placeholder - replace with actual authentication
    currentUser = {
        username: username,
        role: currentRole,
        name: currentRole === 'student' ? 'Juan Dela Cruz' : 'Dr. Maria Santos',
        id: currentRole === 'student' ? '2025-001' : 'DOC-001'
    };
    
    // Store in sessionStorage (or use proper token management)
    sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
    
    // Redirect to appropriate dashboard
    redirectToDashboard();
}

// Redirect to dashboard
function redirectToDashboard() {
    if (currentRole === 'student') {
        window.location.href = 'student/student-dashboard.html';
    } else {
        window.location.href = 'doctor/doctor-dashboard.html';
    }
}

// Logout function
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear session
        sessionStorage.removeItem('currentUser');
        currentUser = null;
        
        // Redirect to login
        window.location.href = '../index.html';
    }
}

// Check if user is authenticated
function isAuthenticated() {
    const user = sessionStorage.getItem('currentUser');
    return user !== null;
}

// Get current user
function getCurrentUser() {
    const userStr = sessionStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
}

// Protect page (call this on dashboard pages)
function protectPage() {
    if (!isAuthenticated()) {
        window.location.href = '../index.html';
    }
}

// Initialize auth on login page
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Role button handlers
    const roleButtons = document.querySelectorAll('.role-btn');
    roleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            selectRole(this.dataset.role);
        });
    });
}