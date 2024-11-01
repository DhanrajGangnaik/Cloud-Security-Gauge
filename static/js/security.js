// security.js

// Basic Input Validation Function
function validateInput(value, type) {
    const patterns = {
        username: /^[a-zA-Z0-9_]{3,30}$/,  // Alphanumeric and underscores for usernames, 3-30 characters
        password: /^.{8,30}$/,  // Minimum 8 and maximum 30 characters for passwords
    };

    return patterns[type].test(value);
}

// Function to escape HTML characters to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Function to get CSRF token from meta tag
function getCsrfToken() {
    const csrfMetaTag = document.querySelector('meta[name="csrf-token"]');
    return csrfMetaTag ? csrfMetaTag.getAttribute('content') : '';
}

// Form Validation Handler
function validateForm(form) {
    let username = form.username.value;
    let password = form.password.value;

    // Escape HTML characters to prevent XSS attacks
    username = escapeHtml(username);
    password = escapeHtml(password);

    if (!validateInput(username, 'username')) {
        alert("Username can only contain letters, numbers, and underscores, and must be 3-30 characters.");
        return false;
    }

    if (!validateInput(password, 'password')) {
        alert("Password must be between 8 and 30 characters.");
        return false;
    }

    return true;
}

// Attach CSRF token to form submission
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            // Add CSRF token to form if present
            const csrfToken = getCsrfToken();
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }

            if (!validateForm(form)) {
                event.preventDefault(); // Prevent form submission if validation fails
            }
        });
    }
});
