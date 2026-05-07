import strawberry


@strawberry.input
class ExternalDashboardCreateInput:
    title: str
    url: str
    page: int
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    show_on_home: bool = False
    order: int = 0
    is_active: bool = True


@strawberry.input
class ExternalDashboardUpdateInput:
    title: str | None = strawberry.UNSET
    url: str | None = strawberry.UNSET
    page: int | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    show_on_home: bool | None = strawberry.UNSET
    order: int | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET


@strawberry.input
class CapacityAndResourceIframeUrlInput:
    dashboard: strawberry.ID
    order: int = 0


@strawberry.input
class CapacityAndResourceCreateInput:
    title: str
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    is_active: bool = True
    order: int = 0
    iframe_urls: list[CapacityAndResourceIframeUrlInput] = strawberry.UNSET


@strawberry.input
class CapacityAndResourceUpdateInput:
    title: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
    order: int | None = strawberry.UNSET
    iframe_urls: list[CapacityAndResourceIframeUrlInput] | None = strawberry.UNSET
