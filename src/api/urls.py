# ================== Standard Library ==================
# 

# ================== Django ============================
from django.urls import include, path

# ================== DRF ===============================
from rest_framework.routers import DefaultRouter

# ================== Third-Party =======================
# 

# ================== Local / App Imports =================
from .views import (
    ClassCreateView,
    FirebaseLoginView,
    LogoutView,
    UserByEmailView,
    UserProfileView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path(
        "api/users/email/<str:email>/", UserByEmailView.as_view(), name="user-by-email"
    ),
    path("api/", include(router.urls)),  # This creates all ID-based routes
    path("api/login/", FirebaseLoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", UserProfileView.as_view(), name="user-profile"),

    path("api/class/",ClassCreateView.as_view(),name="create-class"),
]
