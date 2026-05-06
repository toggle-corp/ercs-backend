import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class EmergencyALertIframeUrlInput:
    url: str


@strawberry.input
class EmergencyAlertCreateInput:
    title: str
    content_type: int
    description: str | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_urls: list[EmergencyALertIframeUrlInput] | None = strawberry.UNSET
    is_published: bool = False
    region: strawberry.ID | None = strawberry.UNSET


@strawberry.input
class EmergencyAlertUpdateInput:
    title: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_urls: list[EmergencyALertIframeUrlInput] | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
