# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User
from .serializers import UserSerializer


@extend_schema(tags=["Users (by ID)"])
class UserViewSet(viewsets.ModelViewSet):
    """
    Automatic CRUD by ID:
    GET    /api/users/          - List all
    POST   /api/users/          - Create
    GET    /api/users/{id}/     - Retrieve by ID
    PATCH  /api/users/{id}/     - Partial update by ID
    PUT    /api/users/{id}/     - Full update by ID
    DELETE /api/users/{id}/     - Delete by ID
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary="List and search all users",
        description="Retrieve a list of all users. A `search` parameter can be used to filter users by their username.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search term for username",
                required=False,
                type=str,
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        # The parent class's list method will be called, but the schema is customized here.
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new user",
        description="Create a new user by providing username, email, and other required fields.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a user by ID",
        description="Get the details of a specific user by their unique ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a user by ID",
        description="Fully update all fields of a specific user by their ID.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a user by ID",
        description="Partially update one or more fields of a specific user by their ID.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a user by ID",
        description="Permanently delete a specific user by their ID.",
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@extend_schema(tags=["Users (by Email)"])
class UserByEmailView(APIView):
    """
    GET    /api/users/email/{email}/  - Retrieve by email
    PATCH  /api/users/email/{email}/  - Partial update by email
    PUT    /api/users/email/{email}/  - Full update by email
    DELETE /api/users/email/{email}/  - Delete by email
    """

    @extend_schema(
        summary="Retrieve a user by email",
        description="Get the details of a specific user by their email address.",
    )
    def get(self, request, email):
        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        summary="Partially update a user by email",
        description="Partially update one or more fields of a specific user by their email address.",
    )
    def patch(self, request, email):
        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(user, data=request.data, partial=True)
        return self._validate_and_save_serializer(serializer)

    @extend_schema(
        summary="Update a user by email",
        description="Fully update all fields of a specific user by their email address.",
    )
    def put(self, request, email):
        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(user, data=request.data)
        return self._validate_and_save_serializer(serializer)

    def _validate_and_save_serializer(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Delete a user by email",
        description="Permanently delete a specific user by their email address.",
    )
    def delete(self, request, email):
        user = get_object_or_404(User, email=email)
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
