import strawberry
import strawberry_django

from apps.content.models import NewsPost, NewsPostReport
from apps.content.serializers import NewsPostReportSerializer, NewsPostSerializer
from main.graphql.context import Info
from main.graphql.permissions import (
    IsAuthenticatedDelete,
    IsAuthenticatedMutation,
    IsStaffOrAboveDelete,
    IsStaffOrAboveMutation,
)
from utils.graphql.mutations import ModelMutation, handle_delete_mutation
from utils.graphql.types import DeleteMutationResponseType, MutationResponseType

from .inputs import NewsPostCreateInput, NewsPostReportInput, NewsPostUpdateInput
from .types import NewsPostReportType, NewsPostType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def create_news_post(
        self,
        info: Info,
        data: NewsPostCreateInput,
    ) -> MutationResponseType[NewsPostType]:
        return await ModelMutation(NewsPostSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def update_news_post(
        self,
        info: Info,
        id: strawberry.ID,
        data: NewsPostUpdateInput,
    ) -> MutationResponseType[NewsPostType]:
        instance = await NewsPost.objects.aget(id=id)
        return await ModelMutation(NewsPostSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedMutation])
    async def create_news_post_report(
        self,
        info: Info,
        data: NewsPostReportInput,
    ) -> MutationResponseType[NewsPostReportType]:
        return await ModelMutation(NewsPostReportSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedDelete], handle_django_errors=False)
    async def delete_news_post_report(
        self,
        info: Info,
        newspost: strawberry.ID,
        report: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(NewsPostReport, newspost_id=newspost, report_id=report)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveDelete], handle_django_errors=False)
    async def delete_news_post(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(NewsPost, id=id)
