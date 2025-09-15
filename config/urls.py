from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("core_apps.user_auth.urls")),
    path("api/v1/profiles/", include("core_apps.user_profile.urls")),
    path("api/v1/accounts/", include("core_apps.accounts.urls")),
    path("api/v1/cards/", include("core_apps.cards.urls")),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))

admin.site.site_header = "SecureBank Admin"
admin.site.site_title = "SecureBank Admin Portal"
admin.site.index_title = "Welcome to SecureBank Admin Portal"
