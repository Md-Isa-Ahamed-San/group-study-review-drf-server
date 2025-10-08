# ================== Standard Library ==================
import random
import string

from django.conf import settings

# ================== Django ============================
from django.shortcuts import get_object_or_404
from django.db.models import Q

# ================== DRF-Spectacular ===================
from drf_spectacular.utils import OpenApiParameter, extend_schema
from firebase_admin import auth

# ================== DRF ===============================
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# ================== Third-Party =======================
from rest_framework_simplejwt.views import TokenRefreshView
from api.utils import generate_tokens_for_user

# ================== Local / App Imports =================
from .models import Class, User
from .serializers import ClassCreateSerializer, ClassDetailSerializer, UserSerializer


#! ==================== AUTH MODEL VIEWS ====================
class FirebaseLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        firebase_token = request.data.get("token")
        print("ALL DATA:", request.data)

        if not firebase_token:
            return Response(
                {"error": "Firebase token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(firebase_token)
            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email")
            username = decoded_token.get("name", email)  # Use name, fallback to email

        except Exception as e:
            # Token is invalid or expired
            return Response(
                {"error": f"Invalid Firebase token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get or create the user in your Django database
        # We match by firebase_uid to ensure uniqueness
        user, created = User.objects.get_or_create(
            firebase_uid=firebase_uid, defaults={"email": email, "username": username}
        )

        # If the user was just created, you might want to set a default password
        # or mark them as having no usable password.
        if created:
            user.set_unusable_password()
            user.save()

        # Now, generate your OWN backend's tokens for this user
        tokens = generate_tokens_for_user(user)
        # print("🔑 ACCESS TOKEN:", tokens["access"])
        # print("🔁 REFRESH TOKEN:", tokens["refresh"])
        response = Response()

        # Set the refresh token in a secure, HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=False,  # Set to False for local HTTP development
            samesite="Lax",
        )

        # Send the access token and user data in the response body
        response.data = {
            "authToken": tokens["access"],
            "user": UserSerializer(user).data,
        }
        response.status_code = status.HTTP_200_OK
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)

        response.delete_cookie("refresh_token", path="/api/")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    # permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {
                    "detail": "Refresh token not found. Please login again.",
                    "code": "REFRESH_TOKEN_NOT_FOUND",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                access_token = response.data.get("access")
                if new_refresh_token := response.data.get("refresh"):
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        secure=settings.SECURE_COOKIES,
                        samesite="Lax",
                        max_age=int(
                            settings.SIMPLE_JWT[
                                "REFRESH_TOKEN_LIFETIME"
                            ].total_seconds()
                        ),
                        path="/api/",
                    )
                    del response.data["refresh"]

                response.data = {
                    "access": access_token,
                    "detail": "Token refreshed successfully",
                }

            return response

        except InvalidToken:
            return Response(
                {
                    "detail": "Refresh token is invalid or expired. Please login again.",
                    "code": "TOKEN_EXPIRED",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except TokenError as e:
            return Response(
                {"detail": f"Token error: {str(e)}", "code": "TOKEN_ERROR"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


#! ==================== USER MODEL VIEWS ====================
@extend_schema(tags=["Authentication"])
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's profile",
        description="Retrieves the profile data for the user authenticated by the access token.",
    )
    def get(self, request):
        # request.user is automatically populated by DRF's authentication classes
        # when a valid access token is provided.
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

    #! add permissions later for faster development
    # permission_classes = [IsAuthenticated]
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


#! ==================== CLASS MODEL VIEWS ====================


class ClassViewSet(viewsets.ModelViewSet):
    """
    Automatic CRUD by Class Code:
    GET    /api/class/                - List all classes of a user
    POST   /api/class/                - Create a new class
    GET    /api/class/{class_code}/   - Retrieve a class by its code
    PATCH  /api/class/{class_code}/   - Partially update a class by its code
    PUT    /api/class/{class_code}/   - Fully update a class by its code
    DELETE /api/class/{class_code}/   - Delete a class by its code

    Custom Actions:
    POST   /api/class/{class_code}/join/        - Join a class
    POST   /api/class/{class_code}/leave/       - Leave a class
    PATCH  /api/class/{class_code}/change_role/ - (Admin) Change a user's role in the class
    """

    queryset = Class.objects.all()
    # permission_classes = [IsAuthenticated,IsCreatorOrAdminOrReadOnly]
    lookup_field = "class_code"

    def get_queryset(self):
        """
        Overrides the default queryset. 
        - For the 'list' action, it returns only classes the user is a part of.
        - For all other actions, it uses the default queryset (Class.objects.all()),
          allowing actions like 'join' to find any class.
        """
        # Get the original queryset
        queryset = super().get_queryset()

        # If the action is to list classes, filter it by the current user.
        if self.action == 'list':
            user = self.request.user
            if user.is_authenticated:
                return queryset.filter(
                    Q(members=user) | Q(experts=user) | Q(admins=user)
                ).distinct()
            return queryset.none() # Or handle unauthenticated users as you see fit

        # For 'retrieve', 'update', 'join', 'leave', etc., return the full queryset.
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ClassCreateSerializer
        return ClassDetailSerializer



    # ================== HELPER METHODS ==================
    def _is_user_in_class(self, user, class_obj):
        is_member = class_obj.members.filter(pk=user.pk).exists()
        is_expert = class_obj.experts.filter(pk=user.pk).exists()
        is_admin = class_obj.admins.filter(pk=user.pk).exists()
        return is_member or is_expert or is_admin

    def _remove_user_from_all_roles(self, user, class_obj):
        class_obj.members.remove(user)
        class_obj.experts.remove(user)
        class_obj.admins.remove(user)

    # ================== DEFAULT ACTIONS ==================

    def generate_unique_class_code(self, length=7):
        while True:
            code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=length)
            )
            if not Class.objects.filter(class_code=code).exists():
                return code

    def perform_create(self, serializer):
        class_code = self.generate_unique_class_code()
        class_instance = serializer.save(
            created_by=self.request.user, class_code=class_code
        )
        class_instance.admins.add(self.request.user)

    # ================== CUSTOM ACTIONS ==================

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, class_code=None):
        class_obj = self.get_object()
        user = request.user

        if self._is_user_in_class(user, class_obj):
            return Response(
                {"detail": "You are already a member of this class."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        class_obj.members.add(user)
        return Response(
            {"detail": "You have successfully joined the class."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def leave(self, request, class_code=None):
        class_obj = self.get_object()
        user = request.user

        if not self._is_user_in_class(user, class_obj):
            return Response(
                {"detail": "You are not a member of this class."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self._remove_user_from_all_roles(user, class_obj)
        return Response(
            {"detail": "You have successfully left the class."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def change_role(self, request, class_code=None):
        """
        Allows a class admin to change the role of another user in the class.
        Expects a body with: {"user_id": "<uuid>", "new_role": "expert"}
        """
        class_obj = self.get_object()
        requesting_user = request.user

        if requesting_user not in class_obj.admins.all():
            return Response(
                {"detail": "You do not have permission to change roles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user_id")
        new_role = request.data.get("new_role")

        if not user_id or not new_role:
            return Response(
                {"detail": "Both 'user_id' and 'new_role' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_role not in ["member", "expert", "admin"]:
            return Response(
                {"detail": "Invalid role. Choose from 'member', 'expert', or 'admin'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not self._is_user_in_class(target_user, class_obj):
            return Response(
                {"detail": "This user is not a member of the class."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self._remove_user_from_all_roles(target_user, class_obj)

        if new_role == "member":
            class_obj.members.add(target_user)
        elif new_role == "expert":
            class_obj.experts.add(target_user)
        elif new_role == "admin":
            class_obj.admins.add(target_user)

        return Response(
            {
                "detail": f"Successfully changed {target_user.username}'s role to {new_role}."
            },
            status=status.HTTP_200_OK,
        )
