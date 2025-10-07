# ================== Standard Library ==================
# 

# ================== Django ============================
from django.contrib import admin
from django.urls import include, path

# ================== DRF ===============================
# 

# ================== Third-Party =======================
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# ================== Local / App Imports =================
from api.views import CookieTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("api.urls")),
    path("silk/", include("silk.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
