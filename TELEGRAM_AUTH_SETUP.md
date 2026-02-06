# Настройка авторизации через Telegram

Этот документ описывает, как настроить авторизацию через Telegram для приложения WordsHelper.

## Требования

- Python 3.8+
- Django 6.0.1
- Telegram аккаунт
- Telegram бот (создается через @BotFather)

## Шаг 1: Создание Telegram бота

1. Откройте Telegram и найдите бота [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя для вашего бота (например, "WordsHelper Bot")
   - Введите username для бота (должен заканчиваться на "bot", например, "WordsHelperBot")
4. @BotFather отправит вам **токен бота** - сохраните его!

Пример токена: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Шаг 2: Настройка домена для бота

Чтобы Telegram Login Widget работал, необходимо указать домен:

1. В чате с @BotFather отправьте команду `/setdomain`
2. Выберите вашего бота
3. Введите домен вашего сайта (например, `https://yourdomain.com` или `http://localhost:8000` для локальной разработки)

**Важно:** Для локальной разработки можно использовать `http://localhost:8000`, но для production необходим HTTPS!

## Шаг 3: Настройка переменных окружения

1. Скопируйте файл `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` и заполните переменные:
   ```env
   # Токен бота из @BotFather
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

   # Username бота без символа @ (например, WordsHelperBot)
   TELEGRAM_BOT_USERNAME=WordsHelperBot
   ```

## Шаг 4: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 5: Применение миграций

```bash
cd worder
python manage.py makemigrations
python manage.py migrate
```

## Шаг 6: Создание суперпользователя (опционально)

Для доступа к админ-панели Django:

```bash
python manage.py createsuperuser
```

## Шаг 7: Запуск сервера

```bash
python manage.py runserver
```

## Шаг 8: Тестирование

1. Откройте браузер и перейдите на `http://localhost:8000`
2. Вы будете перенаправлены на страницу `/login/`
3. Нажмите кнопку "Login with Telegram"
4. Авторизуйтесь через Telegram
5. После успешной авторизации вы будете перенаправлены на главную страницу

## Как это работает

### Архитектура аутентификации

1. **Middleware защиты**: `TelegramAuthenticationMiddleware` проверяет, что пользователь авторизован на всех страницах (кроме `/login/` и статических файлов)

2. **Telegram Login Widget**: Официальный виджет Telegram встроен в страницу `/login/`

3. **Верификация данных**:
   - При успешной авторизации через виджет, данные отправляются на `/telegram-callback/`
   - Сервер проверяет подлинность данных с помощью HMAC-SHA256
   - Проверяется, что данные не старше 24 часов

4. **Создание пользователя**:
   - Если пользователь новый, создается Django User и связанный TelegramUser
   - Если пользователь уже существует, обновляется его информация

5. **Сессия**: Django создает сессию для авторизованного пользователя

### Файловая структура

```
worder/
├── main/
│   ├── models.py              # Модель TelegramUser
│   ├── views.py               # Представления для login, logout, callback
│   ├── telegram_auth.py       # Утилиты для проверки Telegram данных
│   ├── middleware.py          # Middleware для защиты всех страниц
│   └── admin.py               # Регистрация модели в админ-панели
├── templates/
│   ├── login.html             # Страница авторизации с Telegram виджетом
│   └── main.html              # Главная страница (показывает инфо о пользователе)
├── static/
│   ├── css/
│   │   └── login.css          # Стили для страницы авторизации
│   └── js/
│       └── login.js           # JavaScript для обработки Telegram callback
└── worder/
    └── settings.py            # Настройки Django с конфигурацией Telegram
```

## Безопасность

### Проверка подлинности данных

Все данные от Telegram проверяются на сервере:

1. Создается строка проверки данных из всех полученных параметров (кроме hash)
2. Вычисляется HMAC-SHA256 с использованием SHA256 хеша токена бота
3. Полученный hash сравнивается с hash из Telegram
4. Проверяется время авторизации (не более 24 часов назад)

### Защита от несанкционированного доступа

- Middleware проверяет авторизацию на всех страницах
- CSRF защита для всех POST запросов
- Токен бота хранится в переменных окружения, не в коде

## Production Deployment

Для production окружения:

1. **HTTPS обязателен**: Telegram Login Widget требует HTTPS
2. Установите правильный домен в @BotFather через `/setdomain`
3. Используйте безопасный `SECRET_KEY` в Django
4. Установите `DEBUG=False` в settings.py
5. Настройте переменные окружения на сервере:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_BOT_USERNAME="your_bot_username"
   ```

## Troubleshooting

### Проблема: "TELEGRAM_BOT_TOKEN not configured"
**Решение**: Убедитесь, что переменная окружения `TELEGRAM_BOT_TOKEN` установлена

### Проблема: Telegram виджет не загружается
**Решение**:
- Проверьте, что домен настроен в @BotFather через `/setdomain`
- Убедитесь, что `TELEGRAM_BOT_USERNAME` указан правильно (без @)

### Проблема: "Неверные данные аутентификации"
**Решение**:
- Проверьте правильность токена бота
- Убедитесь, что время на сервере синхронизировано

### Проблема: После авторизации показывается ошибка 404
**Решение**: Убедитесь, что все URL маршруты настроены правильно в `urls.py`

## Документация

- [Telegram Login Widget Documentation](https://core.telegram.org/widgets/login)
- [Django Authentication Documentation](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [Python Telegram Bot Library](https://python-telegram-bot.org/)

## Примечания

- Использован официальный Telegram Login Widget вместо `drf_social_oauth2`, так как виджет проще в интеграции и не требует Django REST Framework
- Виджет поддерживает несколько режимов отображения (small, medium, large)
- Пользователи автоматически создаются при первой авторизации
- Информация о пользователе обновляется при каждой авторизации
