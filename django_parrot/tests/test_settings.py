INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_parrot',
    'drftest',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

SECRET_KEY = "Dummy"
TEST_RUNNER = 'drftest.TestRunner'
ROOT_URLCONF = 'django_parrot.tests.test_urls'
DRF_TEST_AUTH_PROVIDER_CLASS = 'django_parrot.token_auth_provider.TokenAuthProvider'

PARROT_LISTENER_HOST = 'http://example.com'
PARROT_NAMESPACE = 'parrot'
