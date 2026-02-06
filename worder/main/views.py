from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import logging

from .telegram_auth import verify_telegram_authentication, get_or_create_user_from_telegram

logger = logging.getLogger(__name__)


def login_view(request):
    """
    Display the login page with Telegram widget.
    If user is already authenticated, redirect to home.
    """
    if request.user.is_authenticated:
        return redirect('home')

    telegram_bot_username = settings.TELEGRAM_BOT_USERNAME

    context = {
        'telegram_bot_username': telegram_bot_username,
    }
    return render(request, 'login.html', context)


@require_http_methods(["POST"])
def telegram_callback(request):
    """
    Handle Telegram authentication callback.
    This view receives authentication data from the Telegram widget via AJAX.
    """
    try:
        # Extract authentication data from POST request
        auth_data = {
            'id': request.POST.get('id'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name', ''),
            'username': request.POST.get('username', ''),
            'photo_url': request.POST.get('photo_url', ''),
            'auth_date': request.POST.get('auth_date'),
            'hash': request.POST.get('hash'),
        }

        # Remove empty values
        auth_data = {k: v for k, v in auth_data.items() if v}

        # Verify authentication
        if not verify_telegram_authentication(auth_data):
            logger.warning(f"Invalid Telegram authentication attempt: {auth_data.get('id')}")
            return JsonResponse({
                'error': 'Неверные данные аутентификации. Попробуйте снова.'
            }, status=400)

        # Get or create user
        user, created = get_or_create_user_from_telegram(auth_data)

        # Log the user in
        login(request, user)

        logger.info(f"User {user.username} authenticated via Telegram (created={created})")

        # Return success response with redirect URL
        return JsonResponse({
            'success': True,
            'redirect_url': '/',
            'message': 'Аутентификация успешна'
        })

    except ValueError as e:
        logger.error(f"Configuration error in Telegram authentication: {str(e)}")
        return JsonResponse({
            'error': 'Ошибка конфигурации сервера. Свяжитесь с администратором.'
        }, status=500)

    except Exception as e:
        logger.error(f"Error during Telegram authentication: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Произошла ошибка при аутентификации. Попробуйте снова.'
        }, status=500)


@login_required
def logout_view(request):
    """
    Log out the current user and redirect to login page.
    """
    logout(request)
    return redirect('login')


@login_required
def home(request):
    """
    Home page - requires authentication.
    """
    return render(request, 'main.html')
