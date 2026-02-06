"""
Telegram Login Widget Authentication Utilities

This module provides functions to validate and process Telegram Login Widget data.
Official documentation: https://core.telegram.org/widgets/login
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from .models import TelegramUser


def verify_telegram_authentication(auth_data):
    """
    Verify that the authentication data is valid and came from Telegram.

    Args:
        auth_data: Dictionary containing authentication data from Telegram widget

    Returns:
        bool: True if authentication is valid, False otherwise
    """
    check_hash = auth_data.get('hash')
    if not check_hash:
        return False

    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured in settings")

    # Create a copy without the hash
    auth_data_copy = {k: v for k, v in auth_data.items() if k != 'hash'}

    # Create data-check-string
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data_copy.items())]
    data_check_string = '\n'.join(data_check_arr)

    # Create secret key from bot token
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    # Verify hash matches
    if calculated_hash != check_hash:
        return False

    # Check auth_date is recent (within 24 hours)
    auth_date = int(auth_data.get('auth_date', 0))
    current_timestamp = datetime.now().timestamp()

    # Allow 24 hours for auth validity
    if current_timestamp - auth_date > 86400:
        return False

    return True


def get_or_create_user_from_telegram(auth_data):
    """
    Get or create a Django user from Telegram authentication data.

    Args:
        auth_data: Dictionary containing validated authentication data from Telegram

    Returns:
        tuple: (User object, created boolean)
    """
    telegram_id = int(auth_data['id'])
    first_name = auth_data['first_name']
    last_name = auth_data.get('last_name', '')
    username = auth_data.get('username', '')
    photo_url = auth_data.get('photo_url', '')
    auth_date_timestamp = int(auth_data['auth_date'])
    auth_date = datetime.fromtimestamp(auth_date_timestamp)

    # Try to find existing TelegramUser
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
        user = telegram_user.user
        created = False

        # Update user information
        telegram_user.first_name = first_name
        telegram_user.last_name = last_name
        telegram_user.username = username
        telegram_user.photo_url = photo_url
        telegram_user.auth_date = auth_date
        telegram_user.save()

    except TelegramUser.DoesNotExist:
        # Create new Django user
        # Use telegram_id as username since it's guaranteed to be unique
        django_username = f"tg_{telegram_id}"

        user = User.objects.create_user(
            username=django_username,
            first_name=first_name,
            last_name=last_name,
        )

        # Create TelegramUser
        telegram_user = TelegramUser.objects.create(
            user=user,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            photo_url=photo_url,
            auth_date=auth_date
        )
        created = True

    return user, created
