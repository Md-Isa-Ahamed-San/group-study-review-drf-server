# ================== Standard Library ==================
# 

# ================== Django ============================
from django.urls import include, path

# ================== DRF ===============================
from rest_framework.routers import DefaultRouter

# ================== Third-Party =======================

# ================== Local / App Imports =================
from .views import (
    # You no longer need ClassListCreateView or ClassRetrieveUpdateDestroyView

    ClassViewSet,
    FirebaseLoginView,
    LogoutView,
    UserByEmailView,
    UserProfileView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"class", ClassViewSet, basename="class")

urlpatterns = [
    path("api/", include(router.urls)),#this will handle all class(viewsets) and user(viewsets) endpoints.

    path("api/users/email/<str:email>/", UserByEmailView.as_view(), name="user-by-email"),
    path("api/login/", FirebaseLoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", UserProfileView.as_view(), name="user-profile"),
]