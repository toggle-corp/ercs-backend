import typing

from django.core.files import File
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from utils.validators import validate_report_file_size

from .models import PmerReport

ALLOWED_FILE_EXTENSIONS: list[str] = ["pdf", "doc", "docx", "xlsx", "xlsm", "png", "jpg", "jpeg"]

validate_file_extension = FileExtensionValidator(
    allowed_extensions=ALLOWED_FILE_EXTENSIONS,
    message="Unsupported file type. Allowed file types are: %(allowed_extensions)s.",
)


class PmerReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmerReport
        fields = [
            "title",
            "description",
            "file",
            "category",
            "report_type",
            "created_by",
            "region",
            "department",
            "project",
            "visibility",
        ]
        extra_kwargs = {
            "created_by": {"required": False},
        }

    def validate_file(self, value: File) -> File:
        validate_report_file_size(value)
        validate_file_extension(value)
        return value

    @typing.override
    def create(self, validated_data: dict) -> PmerReport:
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)
