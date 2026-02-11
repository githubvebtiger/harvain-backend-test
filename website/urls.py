from django.conf import settings, urls
from django.conf.urls import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as django_auth_views
from django.urls import include, path
from django.views.generic import TemplateView, base
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt import views as auth_views
from rest_framework import permissions as rest_permissions

# Custom token view that allows anyone to login
class CustomTokenObtainPairView(auth_views.TokenObtainPairView):
    permission_classes = [rest_permissions.AllowAny]

from bets import views as bets_views
from user.client.api.frontend.views.views import (
    CreateClient,
    CreatePayment,
    CreateSupportTicket,
    GetPlan,
    EmailVerification,
    ActivateEmailAPIView,
    StartVerificationSession,
    StartBlockedSatelliteVerification,
    VeriffWebhook,
    VerificationStatusAPIView,
    BlockedVerificationStatusAPIView,
)

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("logout/", django_auth_views.LogoutView.as_view(), name="logout"),
    path("i18n", include("django.conf.urls.i18n")),
    path("finance/", include("finance.urls")),
    path("news/", bets_views.NewsView.as_view(), name="news"),
    path("", include("football.urls")),
    path("", include("bets.urls")),
    path("", include("user.urls")),
) + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

api_urlpatterns = [
    path("api/frontend/client/register/", CreateClient.as_view(), name="create-client"),
    path(
        "api/frontend/client/send-email-verification/",
        EmailVerification.as_view(),
        name="email-verification",
    ),
    path(
        "api/frontend/client/verify-email/<str:uid64>/<str:token>/",
        ActivateEmailAPIView.as_view(),
        name="email-activate",
    ),
    path(
        "api/frontend/client/start-verification-session/",
        StartVerificationSession.as_view(),
        name="start-verification-session",
    ),
    path(
        "api/frontend/satellite/start-blocked-verification/",
        StartBlockedSatelliteVerification.as_view(),
        name="start-blocked-satellite-verification",
    ),
    path(
        "api/frontend/client/verify-document/",
        VeriffWebhook.as_view(),
        name="verify-document",
    ),
    path(
        "api/frontend/client/verification-status/",
        VerificationStatusAPIView.as_view(),
        name="verification-status",
    ),
    path(
        "api/frontend/satellite/blocked-verification-status/",
        BlockedVerificationStatusAPIView.as_view(),
        name="blocked-verification-status",
    ),
    path(
        "api/frontend/support-ticket/",
        CreateSupportTicket.as_view(),
        name="create-support-ticket",
    ),
    path("api/frontend/payment-plan/", GetPlan.as_view(), name="get-payment-plan"),
    path("api/frontend/payment/", CreatePayment.as_view(), name="create-payment"),
    path("api/", include("user.api.urls")),
    path("api/", include("bets.api.urls")),
    path("api/", include("finance.api.urls")),
    path("api/", include("football.api.urls")),
    path("api/", include("history.urls")),
    path("api/", include("news.api.urls")),
]

auth_urlpatterns = [
    path(
        "api/frontend/token/client/refresh/",
        auth_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/frontend/token/client/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/frontend/token/client",
        CustomTokenObtainPairView.as_view(),
    ),
]

swagger_api = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

media_urlpatterns = static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += media_urlpatterns + api_urlpatterns + auth_urlpatterns + swagger_api

if settings.DEBUG:
    urlpatterns += static.static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
