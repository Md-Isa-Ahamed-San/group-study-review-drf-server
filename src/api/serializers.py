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
from .models import Class, Submission, User


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"


#! ==================== USER SERIALIZERS ====================
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


class ClassDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    experts = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    admins = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

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
        ]
        read_only_fields = ["id", "class_code", "created_by", "created_at"]
