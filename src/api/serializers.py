# ================== Standard Library ==================
#

# ================== Django ============================
#

# ================== DRF ===============================p
from rest_framework import serializers

# ================== Third-Party =======================
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# ================== Local / App Imports =================
from .models import Class, Submission, User, Task


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"


#! ==================== USER SERIALIZERS ====================
class BasicUserSerializer(serializers.ModelSerializer): #this serializer is for to get the username in the admin,members, expert field of class details
    """
    A simplified User serializer that only includes essential public information.
    Perfect for nesting within other serializers like ClassDetailSerializer.
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
        ]
class UserSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
            "is_active",
            "date_joined",
            "submissions",
            "firebase_uid",
        ]
        read_only_fields = ["id", "date_joined", "firebase_uid"]


#! ==================== CLASS SERIALIZER ====================


class ClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        # Only including those fields that the user should provide upon creation.
        fields = ["class_name", "description"]


class TaskSerializer(serializers.ModelSerializer):
    # Use a read-only serializer to show user details instead of just the ID
    created_by = UserSerializer(read_only=True)

    # Allows us to set the class object by its UUID on creation
    class_obj_id = serializers.UUIDField(write_only=True, source="class_obj")

    class Meta:
        model = Task
        fields = [
            "id",
            "class_obj_id",  # Write-only field for creating a task
            "title",
            "description",
            "created_by",
            "created_at",
            "updated_at",
            "dueDate",
            "status",
            "document",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_class_obj_id(self, value):
        """
        Check that the class exists and the user is an expert or creator.
        """
        request = self.context.get("request")
        user = request.user

        try:
            class_instance = Class.objects.get(id=value)
        except Class.DoesNotExist as e:
            raise serializers.ValidationError("Class not found.") from e

        # Check if the user has permission to create a task in this class (e.g., must be an expert)
        if not (
            class_instance.experts.filter(id=user.id).exists()
            or class_instance.admins.filter(id=user.id).exists()
        ):
            raise serializers.ValidationError(
                "You do not have permission to create a task in this class."
            )

        return class_instance


class ClassDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)

    members = BasicUserSerializer(many=True, read_only=True)
    experts = BasicUserSerializer(many=True, read_only=True)
    admins = BasicUserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = [
            "id",
            "class_name",
            "description",
            "class_code",
            "created_by",
            "created_at",
            "members",
            "experts",
            "admins",
            "tasks"
        ]
        read_only_fields = ["id", "class_code", "created_by", "created_at"]


#! ==================== TASK SERIALIZER ====================
