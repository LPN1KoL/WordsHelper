from django.urls import path
from .views import home, login_view, logout_view, telegram_callback

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('telegram-callback/', telegram_callback, name='telegram_callback'),
]