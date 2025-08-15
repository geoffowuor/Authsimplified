# AuthSimplified

**AuthSimplified** is a Django authentication package designed to give you a ready-to-use OTP-based email verification and token authentication system in minutes.  
It includes user registration, login, logout, OTP verification, and OTP resend without having to write the code yourself.

## Features

- User registration with OTP email verification
- Login with Django REST Framework Token authentication
- Logout with JWT refresh token blacklisting
- OTP verification with expiry checks
- Resend OTP functionality
- Customizable SMTP email sending
- Lightweight and easy to integrate into existing Django projects


## Installation

Install via pip:

```bash
pip install authsimplified
```


## Setup & Configuration

After installing, you need to integrate it into your Django project.

### 1. Add to Installed Apps

In your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'authsimplified',
]
```

### 2. Configure Authentication Backends

```python
AUTH_USER_MODEL = 'authsimplified.User'
```

### 3. Configure Django REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

### 4. Configure SMTP for Email Sending

AuthSimplified sends OTPs via email.  
You need to configure SMTP settings in your `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourmailprovider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

#### Using Gmail SMTP

If you want to use Gmail:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yourgmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

> **Note:** For Gmail, you need to create an App Password from your Google account settings.  
> Go to **Google Account → Security → App passwords** and generate one.

### 5. Include AuthSimplified URLs

In your project’s `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('auth/', include('authsimplified.urls')),
]
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```



## API Endpoints

| Endpoint             | Method | Description                        |
|----------------------|--------|------------------------------------|
| `/auth/register/`    | POST   | Register a user and send OTP       |
| `/auth/login/`       | POST   | Login user with token authentication|
| `/auth/logout/`      | POST   | Logout user and blacklist JWT token|
| `/auth/verify/`      | POST   | Verify OTP and activate user       |
| `/auth/resend-otp/`  | POST   | Resend OTP to user’s email         |


## Example Usage

### Register

**POST** `/auth/register/`  
Content-Type: `application/json`

```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Verify OTP

**POST** `/auth/verify/`  
Content-Type: `application/json`

```json
{
  "otp": "123456"
}
```

### Login

**POST** `/auth/login/`  
Content-Type: `application/json`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
