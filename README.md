# REST API для контактів

Цей проєкт є REST API для зберігання та керування контактами, створений за допомогою FastAPI та SQLAlchemy.

## Функціональність

*   Автентифікація та авторизація користувачів за допомогою JWT.
*   Верифікація електронної пошти.
*   Завантаження та оновлення аватара користувача.
*   Створення, читання, оновлення та видалення контактів.
*   Пошук контактів за іменем, прізвищем або електронною поштою.
*   Отримання списку контактів з днями народження на найближчі 7 днів.
*   Обмеження кількості запитів до маршруту.
*   Підтримка CORS.
*   Автоматична документація Swagger.

## Вимоги

*   Python 3.7+
*   PostgreSQL
*   Pipenv
*   Docker

## Встановлення

1.  **Клонуйте репозиторій:**
    ```bash
    git clone <repository-url>
    cd goit-pythonweb-hw-10
    ```

2.  **Створіть файл `.env`:**
    Створіть файл `.env` у кореневій папці проекту та додайте наступні змінні:
    ```
    SECRET_KEY=mysecretkey
    CLOUDINARY_NAME=my_cloudinary_name
    CLOUDINARY_API_KEY=my_cloudinary_api_key
    CLOUDINARY_API_SECRET=my_cloudinary_api_secret
    SQLALCHEMY_DATABASE_URL=postgresql://postgres:mysecretpassword@localhost/contacts_db
    ```

3.  **Запустіть додаток за допомогою Docker Compose:**
    ```bash
    docker-compose up -d
    ```

## Використання

1.  **Доступ до документації API:**
    Відкрийте браузер і перейдіть за адресою `http://127.0.0.1:8000/docs`.

## Кінцеві точки API

### Автентифікація

*   `POST /api/signup`: Реєстрація нового користувача.
*   `POST /api/login`: Вхід користувача.
*   `GET /api/users/me/`: Отримати деталі поточного користувача.
*   `PATCH /api/users/avatar`: Оновити аватар користувача.

### Верифікація електронної пошти

*   `GET /api/verifyemail/{token}`: Підтвердити електронну пошту.
*   `POST /api/resend-verification-email/`: Повторно надіслати лист для верифікації.

### Контакти

*   `POST /api/contacts/`: Створити новий контакт.
*   `GET /api/contacts/`: Отримати список усіх контактів.
*   `GET /api/contacts/search`: Пошук контактів.
*   `GET /api/contacts/birthdays`: Отримати контакти з майбутніми днями народження.
*   `GET /api/contacts/{contact_id}`: Отримати один контакт за ідентифікатором.
*   `PUT /api/contacts/{contact_id}`: Оновити існуючий контакт.
*   `DELETE /api/contacts/{contact_id}`: Видалити контакт.
