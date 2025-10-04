# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserByEmailView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")


urlpatterns = [
    path('api/users/email/<str:email>/', UserByEmailView.as_view(), name='user-by-email'),
    path('api/', include(router.urls)),  # This creates all ID-based routes
]