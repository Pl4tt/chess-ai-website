from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION
    default_acl = settings.AWS_DEFAULT_ACL
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

class MediaStorage(S3Boto3Storage):
    location = settings.AWS_MEDIA_LOCATION
    default_acl = settings.AWS_DEFAULT_ACL
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN