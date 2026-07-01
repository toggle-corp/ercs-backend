from django.core.files import File
from rest_framework import serializers

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_REPORT_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image_size[F: File | None](value: F) -> F:
    if value is not None and value.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError("Image size must not exceed 2 MB.")
    return value


def validate_report_file_size[F: File | None](value: F) -> F:
    if value is not None and value.size > MAX_REPORT_FILE_SIZE:
        raise serializers.ValidationError("File size must not exceed 5 MB.")
    return value
