"""
Custom middleware for enforcing Telegram authentication on all routes.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class TelegramAuthenticationMiddleware:
    """
    Middleware to enforce authentication on all routes except login-related pages.

    This middleware ensures that all users must be authenticated via Telegram
    to access any part of the site, except for the login page itself and
    authentication callback endpoints.
    """

    # URLs that don't require authentication
    EXEMPT_URLS = [
        '/login/',
        '/telegram-callback/',
        '/admin/login/',  # Allow admin login separately if needed
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the current path is exempt from authentication
        path = request.path_info

        # Allow exempt URLs
        if any(path.startswith(url) for url in self.EXEMPT_URLS):
            return self.get_response(request)

        # Allow static and media files
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Redirect to login page
            login_url = reverse('login')
            return redirect(f"{login_url}?next={path}")

        # User is authenticated, continue processing
        response = self.get_response(request)
        return response
