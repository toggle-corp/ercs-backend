import logging
import typing
from collections import Counter

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from rest_framework import serializers

from main.graphql.context import Info

from .common import DataclassInstance, InputDataType, parse_input_data
from .drf import MutationCustomErrorType, mutation_is_not_valid
from .types import CustomErrorType, DeleteMutationResponseType, MutationResponseType

logger = logging.getLogger(__name__)


def _describe_related(objects: typing.Iterable[models.Model]) -> str:
    """Summarise blocking objects as e.g. "3 Reports and 1 News Post"."""
    counts = Counter(type(obj)._meta for obj in objects)
    parts = [f"{count} {meta.verbose_name if count == 1 else meta.verbose_name_plural}" for meta, count in counts.items()]
    if len(parts) == 1:
        return parts[0]
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


def _in_use_message(model: type[models.Model], error: ProtectedError | RestrictedError) -> str:
    related = error.protected_objects if isinstance(error, ProtectedError) else error.restricted_objects
    return (
        f"This is still linked to {_describe_related(related)}. Remove or reassign them first, then try deleting it again."
    )


async def handle_delete_mutation(
    model: type[models.Model],
    **lookup: typing.Any,
) -> DeleteMutationResponseType:
    """Delete a single object, reporting every failure on the mutation payload.

    Every branch returns; nothing escapes to the top-level GraphQL `errors`, where a
    client can only render it as a generic failure. All ORM work happens inside
    `sync_to_async`, and the payload holds only scalars, so no Django object is left
    for the async resolver to touch.
    """

    @sync_to_async
    def _delete() -> DeleteMutationResponseType:
        try:
            instance = model.objects.get(**lookup)
        except (model.DoesNotExist, ValidationError, ValueError, TypeError):
            # A malformed id (e.g. "" against a UUID pk) is the same situation for the
            # caller as a missing one: there is nothing here to delete.
            return DeleteMutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message(
                    f"This {model._meta.verbose_name} no longer exists. It may already have been deleted.",
                ),
            )
        except model.MultipleObjectsReturned:
            logger.error("Ambiguous delete lookup for %s: %s", model._meta.label, lookup)
            return DeleteMutationResponseType(ok=False, errors=MutationCustomErrorType.generate_message())
        try:
            with transaction.atomic():
                instance.delete()
        except (ProtectedError, RestrictedError) as error:
            return DeleteMutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message(_in_use_message(model, error)),
            )
        except Exception:
            logger.error("Failed to delete %s", model._meta.label, exc_info=True)
            return DeleteMutationResponseType(ok=False, errors=MutationCustomErrorType.generate_message())
        return DeleteMutationResponseType(ok=True)

    return await _delete()


def _get_serializer_context(
    info: Info,
    extra_context: dict[typing.Any, typing.Any] | None,
) -> dict[str, typing.Any]:
    return {
        "graphql_info": info,
        "request": info.context.request,
        "extra_context": extra_context,
    }


class ModelMutation:
    def __init__(self, serializer_class: type[serializers.Serializer]):
        self.serializer_class = serializer_class

    @staticmethod
    @sync_to_async
    def handle_mutation(
        serializer_class: type[serializers.Serializer],
        data: typing.Any,
        info: Info,
        extra_context: dict[typing.Any, typing.Any] | None,
        **kwargs: typing.Any,
    ) -> tuple[CustomErrorType | None, models.Model | None]:
        serializer = serializer_class(
            data=data,
            context=_get_serializer_context(info, extra_context=extra_context),
            **kwargs,
        )
        if errors := mutation_is_not_valid(serializer):
            return errors, None
        try:
            with transaction.atomic():
                instance = serializer.save()
        except Exception:
            logger.error("Failed to handle mutation", exc_info=True)
            return MutationCustomErrorType.generate_message(), None
        return None, instance

    async def handle_create_mutation(
        self,
        data: typing.Any,
        info: Info,
        extra_context: dict[typing.Any, typing.Any] | None = None,
    ) -> MutationResponseType:  # type: ignore[reportMissingTypeArgument]
        errors, saved_instance = await self.handle_mutation(
            self.serializer_class,
            parse_input_data(data),
            info,
            extra_context,
        )
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=saved_instance)

    @staticmethod
    @sync_to_async
    def handle_bulk_mutation(
        serializer_class: type[serializers.Serializer],
        data_list: list[typing.Any],
        info: Info,
        extra_context: dict[typing.Any, typing.Any] | None,
    ) -> tuple[CustomErrorType | None, list[models.Model] | None]:
        context = _get_serializer_context(info, extra_context=extra_context)
        validated_serializers = []
        for data in data_list:
            serializer = serializer_class(data=data, context=context)
            if errors := mutation_is_not_valid(serializer):
                return errors, None
            validated_serializers.append(serializer)
        try:
            with transaction.atomic():
                instances = [serializer.save() for serializer in validated_serializers]
        except Exception:
            logger.error("Failed to handle bulk mutation", exc_info=True)
            return MutationCustomErrorType.generate_message(), None
        return None, instances

    async def handle_bulk_create_mutation(
        self,
        data: typing.Any,
        info: Info,
        extra_context: dict[typing.Any, typing.Any] | None = None,
    ) -> MutationResponseType:  # type: ignore[reportMissingTypeArgument]
        errors, saved_instances = await self.handle_bulk_mutation(
            self.serializer_class,
            parse_input_data(data),
            info,
            extra_context,
        )
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=saved_instances)

    async def handle_update_mutation(
        self,
        data: typing.Any,
        info: Info,
        instance: models.Model,
        extra_context: dict[typing.Any, typing.Any] | None = None,
        dataclass_transformer: typing.Callable[[DataclassInstance], tuple[bool, InputDataType]] | None = None,
    ) -> MutationResponseType:  # type: ignore[reportMissingTypeArgument]
        parsed_dict = parse_input_data(data, dataclass_transformer)
        errors, saved_instance = await self.handle_mutation(
            self.serializer_class,
            parsed_dict,
            info,
            extra_context,
            instance=instance,
            partial=True,
        )
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=saved_instance)
