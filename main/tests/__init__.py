from .base import TestCase


class FakeTest(TestCase):
    """Used by CI to run migrations without running real tests.
    docker compose exec web ./manage.py test --keepdb -v 2 main.tests.FakeTest.
    """

    def test_fake(self):
        pass


__all__ = ["FakeTest", "TestCase"]
