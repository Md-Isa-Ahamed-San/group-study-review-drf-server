# ================== Standard Library ==================
# 

# ================== Django ============================
from django.urls import include, path

# ================== DRF ===============================
from rest_framework.routers import DefaultRouter

# ================== Third-Party =======================
from rest_framework_nested import routers 
# ================== Local / App Imports =================
from .views import (
    # You no longer need ClassListCreateView or ClassRetrieveUpdateDestroyView

    ClassViewSet,
    FirebaseLoginView,
    LogoutView,
    SubmissionViewSet,
    UserByEmailView,
    UserProfileView,
    UserViewSet,
        TaskViewSet,
    ClassTaskViewSet
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"class", ClassViewSet, basename="class")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"submissions", SubmissionViewSet, basename="submissions")

# Create a nested router for class tasks
class_router = routers.NestedSimpleRouter(router, r"class", lookup="class")
class_router.register(r"tasks", ClassTaskViewSet, basename="class-tasks")

urlpatterns = [
    path("api/", include(router.urls)),#this will handle all class(viewsets) and user(viewsets) endpoints.
path("api/", include(class_router.urls)), 
    path("api/users/email/<str:email>/", UserByEmailView.as_view(), name="user-by-email"),
    path("api/login/", FirebaseLoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", UserProfileView.as_view(), name="user-profile"),
]