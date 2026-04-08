from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from main.graphql.schema import CustomAsyncGraphQLView, schema as graphql_schema

admin.site.site_header = "ERCS-EOC Admin"

base_graphql_kwargs = dict(
    schema=graphql_schema,
    multipart_uploads_enabled=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health-check/", include("health_check.urls")),
    path(
        "graphql/",
        csrf_exempt(
            CustomAsyncGraphQLView.as_view(**base_graphql_kwargs),
        ),
        name="graphql",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "graphiql/",
            csrf_exempt(
                CustomAsyncGraphQLView.as_view(
                    **base_graphql_kwargs,
                    graphql_ide="graphiql",
                ),
            ),
            name="graphiql",
        ),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
