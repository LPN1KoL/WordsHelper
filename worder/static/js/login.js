/**
 * Telegram Login Widget JavaScript Handler
 *
 * This script handles the Telegram authentication callback and form submission.
 */

// This function will be called by Telegram widget when user authenticates
function onTelegramAuth(user) {
    console.log('Telegram auth data received:', user);

    // Show loading state
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.classList.add('active');
    }

    // Hide any previous error messages
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.classList.remove('active');
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('id', user.id);
    formData.append('first_name', user.first_name);
    if (user.last_name) formData.append('last_name', user.last_name);
    if (user.username) formData.append('username', user.username);
    if (user.photo_url) formData.append('photo_url', user.photo_url);
    formData.append('auth_date', user.auth_date);
    formData.append('hash', user.hash);

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Send authentication data to server
    fetch('/telegram-callback/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Authentication failed');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Authentication successful:', data);

        // Redirect to the appropriate page
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            // Default redirect to home page
            window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('Authentication error:', error);

        // Hide loading state
        if (loadingElement) {
            loadingElement.classList.remove('active');
        }

        // Show error message
        if (errorElement) {
            errorElement.textContent = error.message || 'Authentication failed. Please try again.';
            errorElement.classList.add('active');
        }
    });
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Login page loaded');

    // Check if user is already authenticated
    // This is a fallback - the server should handle redirects
    if (window.location.search.includes('error=')) {
        const errorElement = document.getElementById('error-message');
        if (errorElement) {
            const urlParams = new URLSearchParams(window.location.search);
            const errorMsg = urlParams.get('error');
            errorElement.textContent = errorMsg || 'An error occurred during authentication.';
            errorElement.classList.add('active');
        }
    }
});
