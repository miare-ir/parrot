INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'parrot',
    'drftest',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "Dummy"
TEST_RUNNER = 'drftest.TestRunner'
ROOT_URLCONF = 'parrot.tests.test_urls'
DRF_TEST_AUTH_PROVIDER_CLASS = 'parrot.token_auth_provider.TokenAuthProvider'
PARROT_LISTENER_HOST = 'http://localhost:8111'
PARROT_NAMESPACE = 'parrot'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
