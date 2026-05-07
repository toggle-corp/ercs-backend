class ReadOnlyMixin:
    """Mixin for models that should never be modified through the admin UI.

    Use on models seeded via import scripts (AdminArea) or populated by
    external sync jobs (Emergency) where admin edits would be incorrect.
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
