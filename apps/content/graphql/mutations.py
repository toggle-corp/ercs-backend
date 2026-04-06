import strawberry
import strawberry_django

from apps.content.models import NewsPost, NewsPostReport
from apps.content.serializers import NewsPostReportSerializer, NewsPostSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated, IsStaffOrAbove
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import NewsPostCreateInput, NewsPostReportInput, NewsPostUpdateInput
from .types import NewsPostReportType, NewsPostType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_news_post(
        self,
        info: Info,
        data: NewsPostCreateInput,
    ) -> MutationResponseType[NewsPostType]:
        return await ModelMutation(NewsPostSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_news_post(
        self,
        info: Info,
        id: strawberry.ID,
        data: NewsPostUpdateInput,
    ) -> MutationResponseType[NewsPostType]:
        instance = await NewsPost.objects.aget(id=id)
        return await ModelMutation(NewsPostSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_news_post_report(
        self,
        info: Info,
        data: NewsPostReportInput,
    ) -> MutationResponseType[NewsPostReportType]:
        return await ModelMutation(NewsPostReportSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def delete_news_post_report(
        self,
        info: Info,
        newspost: strawberry.ID,
        report: strawberry.ID,
    ) -> MutationResponseType[NewsPostReportType]:
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _delete() -> MutationResponseType:
            try:
                obj = NewsPostReport.objects.get(newspost_id=newspost, report_id=report)
                obj.delete()
                return MutationResponseType(ok=True)
            except NewsPostReport.DoesNotExist:
                return MutationResponseType(ok=False)

        return await _delete()
