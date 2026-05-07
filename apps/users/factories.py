# pyright: reportRedeclaration=false
# pyright: reportIncompatibleVariableOverride=false
# pyright: reportMissingTypeArgument=false
# pyright: reportPrivateImportUsage=false
import typing

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from .models import User


class UserFactory(DjangoModelFactory):
    email = factory.Sequence(lambda n: f"user{n}@ercs.org")
    full_name = factory.Faker("name")
    role = User.Role.VIEWER
    is_active = True

    class Meta:
        model = User

    @factory.post_generation
    def password(
        obj: User,  # type: ignore[reportGeneralTypeIssues]
        create: bool,
        password: str,
        **_,
    ):
        if not create:
            return
        password_text = password or fuzzy.FuzzyText(length=15).fuzz()
        obj.set_password(password_text)
        obj.password_text = password_text  # type: ignore[reportUninitializedInstanceVariable]
        obj.save()


if typing.TYPE_CHECKING:
    UserFactory: type[DjangoModelFactory[User]]
