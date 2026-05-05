import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class IframeUrlInput:
    url: str


@strawberry.input
class ResourceCreateInput:
    title: str
    content_type: int
    description: str | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_urls: list[IframeUrlInput] | None = strawberry.UNSET
    is_published: bool = False
    region: strawberry.ID | None = strawberry.UNSET


@strawberry.input
class ResourceUpdateInput:
    title: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_urls: list[IframeUrlInput] | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET