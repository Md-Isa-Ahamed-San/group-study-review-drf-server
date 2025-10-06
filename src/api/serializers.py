from rest_framework import serializers

from .models import Submission, User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken



class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"


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
