# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DevGetTokenView,
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
    path("api/dev/get-token/", DevGetTokenView.as_view()),
    path("api/login/", FirebaseLoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", UserProfileView.as_view(), name="user-profile"),
]
