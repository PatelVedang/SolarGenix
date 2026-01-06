from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom storage backend for media files.
    Ensures files are stored in a 'media/' subdirectory in the S3 bucket,
    remain private, and are served using pre-signed URLs.
    """

    location = "media"
    file_overwrite = False
    default_acl = "private"
    custom_domain = False
    querystring_auth = True  # Required for pre-signed URLs