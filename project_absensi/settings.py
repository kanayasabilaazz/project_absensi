"""
Django settings for project_absensi project.
"""

from pathlib import Path

# ==============================================================================
# CORE SETTINGS
# Konfigurasi dasar project
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY SETTINGS
# Konfigurasi keamanan aplikasi
# ==============================================================================

SECRET_KEY = 'django-insecure-1-a9xs0&a+@0-0*c#c#m_)!(l=wpno@y7=&w+)$6vp_lchph$1!5'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.100']


# ==============================================================================
# APPLICATION DEFINITION
# Daftar aplikasi yang digunakan
# ==============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'django.contrib.humanize', 
    'widget_tweaks',
    
    # Local app
    'absensi_app',
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

ROOT_URLCONF = 'project_absensi.urls'

# ==============================================================================
# TEMPLATES
# Konfigurasi template dan context processors
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'absensi_app.context_processors.cabang_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'project_absensi.wsgi.application'

# ==============================================================================
# DATABASE
# Konfigurasi koneksi database PostgreSQL
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'absensi_db',
        'USER': 'postgres',
        'PASSWORD': 'Azzahra16@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ==============================================================================
# PASSWORD VALIDATION
# Validator untuk password user
# ==============================================================================

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


# ==============================================================================
# INTERNATIONALIZATION & TIME
# Pengaturan bahasa dan zona waktu
# ==============================================================================

LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# STATIC & MEDIA FILES
# Konfigurasi file statis dan media
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# AUTHENTICATION & SESSIONS
# ✅ UPDATED: Pengaturan session persisten untuk cabang
# ==============================================================================

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ========================================
# ✅ FIX: SESSION PERSISTEN (30 HARI)
# ========================================
SESSION_COOKIE_AGE = 86400 * 30
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# MESSAGES FRAMEWORK
# Konfigurasi pesan notifikasi
# ==============================================================================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}


# ==============================================================================
# DEFAULT SETTINGS & CUSTOM CONFIG
# Pengaturan tambahan dan kustom
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Format tanggal dan waktu Indonesia
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'd/m/Y H:i'

DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d']
TIME_INPUT_FORMATS = ['%H:%M', '%H:%M:%S']

# Konfigurasi mesin fingerprint
FINGERPRINT_DEVICE_IP = '15.59.254.211'
FINGERPRINT_DEVICE_PORT = 4370