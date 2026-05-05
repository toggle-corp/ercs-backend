import strawberry
from asgiref.sync import sync_to_async
from django.core.files.uploadedfile import UploadedFile
from strawberry.django.views import AsyncGraphQLView
from strawberry.file_uploads import Upload
from strawberry_django.optimizer import DjangoOptimizerExtension

from apps.content.graphql import mutations as content_mutations
from apps.content.graphql import queries as content_queries
from apps.dashboards.graphql import mutations as dashboard_mutations
from apps.dashboards.graphql import queries as dashboard_queries
from apps.emergency.graphql import queries as emergency_queries
from apps.gallery.graphql import mutations as gallery_mutations
from apps.gallery.graphql import queries as gallery_queries
from apps.geo.graphql import queries as geo_queries
from apps.reports.graphql import mutations as report_mutations
from apps.reports.graphql import queries as report_queries
from apps.resources.graphql import mutations as resource_mutations
from apps.resources.graphql import queries as resource_queries
from apps.teams.graphql import mutations as team_mutations
from apps.teams.graphql import queries as team_queries
from apps.users.graphql import queries as user_queries

from .context import GraphQLContext
from .enums import AppEnumCollection, AppEnumCollectionData


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, *args, **kwargs) -> GraphQLContext:  # type: ignore[reportIncompatibleMethodOverride]
        context = GraphQLContext(*args, **kwargs)
        await sync_to_async(lambda: context.request.user.is_authenticated)()
        return context


@strawberry.type
class Query(
    geo_queries.Query,
    user_queries.Query,
    report_queries.Query,
    resource_queries.Query,
    content_queries.Query,
    dashboard_queries.Query,
    emergency_queries.Query,
    gallery_queries.Query,
    team_queries.Query,
):
    enums: AppEnumCollection = strawberry.field(  # type: ignore[reportGeneralTypeIssues]
        resolver=lambda: AppEnumCollectionData(),  # noqa: PLW0108
    )


@strawberry.type
class Mutation(
    report_mutations.Mutation,
    resource_mutations.Mutation,
    content_mutations.Mutation,
    dashboard_mutations.Mutation,
    gallery_mutations.Mutation,
    team_mutations.Mutation,
): ...


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ],
    scalar_overrides={
        UploadedFile: Upload,
    },
)