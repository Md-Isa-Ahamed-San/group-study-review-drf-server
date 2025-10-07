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
            'firebase_uid'
        ]
        read_only_fields = ["id", "date_joined",'firebase_uid']


#! ==================== CLASS SERIALIZER ====================

class ClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"
        read_only_fields = ["id", "class_code", "created_by", "created_at"]
