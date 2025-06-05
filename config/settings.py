from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load SECRET_KEY from environment variable, with a fallback for local development.
# IMPORTANT: The fallback key is insecure and should ONLY be used for local development.
# Set a strong, unique DJANGO_SECRET_KEY environment variable in production.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'z)hbbbnyho+56=n0*$an5rnk1xr0vfly8f&%&)n2je@r#yis92')

# Load DEBUG status from environment variable, defaulting to True for development.
# IMPORTANT: Set DJANGO_DEBUG=False in your production environment.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Load ALLOWED_HOSTS from environment variable.
# Example for production: DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = allowed_hosts_env.split(',')
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1'] # Default for local development

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog_app.apps.BlogAppConfig',
    'django.contrib.postgres',
    'taggit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # No project-level 'templates' directory specified
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Default local database configuration (can be overridden by DATABASE_URL env var)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog',
        'USER': 'postgres',
        'PASSWORD': '1', # Replace with your local DB password if different
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Docker-friendly database configuration using DATABASE_URL environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=os.environ.get('DJANGO_DB_SSL_REQUIRE', 'False').lower() == 'true'
    )
else: # Fallback for local development if DATABASE_URL is not set
    print("INFO: DATABASE_URL not set, using default local PostgreSQL settings from DATABASES dict.")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# Directory where 'collectstatic' will gather all static files for deployment.
STATIC_ROOT = BASE_DIR / 'staticfiles_collected'
# If you have project-level static files (not tied to a specific app),
# you can uncomment and use STATICFILES_DIRS:
# STATICFILES_DIRS = [BASE_DIR / "static_project_level"]

# Media files (user-uploaded content)
MEDIA_URL = '/media/'
# Directory where user-uploaded files will be stored on the server.
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'blog_app.CustomUser'

LOGIN_URL = 'blog_app:login'
LOGOUT_REDIRECT_URL = 'blog_app:post_list'
LOGIN_REDIRECT_URL = 'blog_app:post_list'