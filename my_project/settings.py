"""
Django settings for my_project project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# -------------------------------------------------------------------
# [1. BASE_DIR 정의] 이것이 가장 먼저 나와야 합니다.
BASE_DIR = Path(__file__).resolve().parent.parent
# -------------------------------------------------------------------



# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1-zid060+np8u2opd0y(@1yb%3ht#fa@2ls6pltv4qdh!-wycl'

# SECURITY WARNING: don't run with debug turned on in production!

# 환경 변수에서 DEBUG 값을 읽고, 문자열 'True'일 때만 True로 설정합니다.
# 로컬 테스트용 EC2 IP 주소를 여기에 추가하세요. (예: '3.35.11.230')

DEBUG = True

ALLOWED_HOSTS = [
    '3.35.11.230',  # 고객님의 EC2 공인 IP 주소
    'ec2-3-35-11-230.ap-northeast-2.compute.amazonaws.com',  # 고객님의 EC2 퍼블릭 DNS 주소
    '127.0.0.1',  # 로컬 및 서버 내부 테스트용
    '192.168.0.6', # 사용자의 맥북 내부 IP 주소
]
# ----------------------------------------------------


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'channels',
    'main',
    # 팀 프로젝트 앱들을 여기에 추가하세요 (예: 'board', 'market')
]

ASGI_APPLICATION = 'my_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # 프로젝트 전역 템플릿 경로
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.unread_counts', # For unread counts
            ],
        },
    },
]

WSGI_APPLICATION = 'my_project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# 배포를 위한 정적 파일 수집 경로 (Nginx가 서빙할 최종 경로)
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom/Merged settings ---

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SITE_ID = 1

AUTH_USER_MODEL = 'main.User'
LOGIN_URL = 'login'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'