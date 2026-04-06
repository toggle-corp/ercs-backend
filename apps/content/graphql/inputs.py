import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class NewsPostCreateInput:
    title: str
    content: str
    description: str | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    is_published: bool = False


@strawberry.input
class NewsPostUpdateInput:
    title: str | None = strawberry.UNSET
    content: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET


@strawberry.input
class NewsPostReportInput:
    newspost: strawberry.ID
    report: strawberry.ID
    order: int = 0
