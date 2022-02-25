"""production settings"""

from decouple import config

ALLOWED_HOSTS = ["namastenepal.com", "www.namastenepal.com", "15.207.248.153", "app.jetadmin.io"]

# AWS SETTINGS ---------------------------------------------
AWS_ACCESS_KEY_ID = config("S3_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("S3_SECRET")
AWS_STORAGE_BUCKET_NAME = "namaste-nepal"
AWS_S3_CUSTOM_DOMAIN = "s3.ap-south-1.amazonaws.com/{}".format(AWS_STORAGE_BUCKET_NAME)

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
# AWS_LOCATION = 'static'

# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# -----------------------------------------

EMAIL_BACKEND = "django_smtp_ssl.SSLEmailBackend"
EMAIL_HOST = "email-smtp.ap-south-1.amazonaws.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = config("S3_KEY_ID")
EMAIL_HOST_PASSWORD = config("S3_SECRET")
EMAIL_USE_SSL = True

CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = "https://"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True
PREPEND_WWW = True

SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"

X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
