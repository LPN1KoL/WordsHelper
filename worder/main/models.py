from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    """
    Model to store Telegram user data.
    Linked to Django's User model for authentication.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_user')
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    auth_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return f"{self.first_name} (@{self.username})" if self.username else self.first_name
