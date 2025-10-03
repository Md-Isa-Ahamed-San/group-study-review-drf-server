from rest_framework import serializers

from .models import Submission, User


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
        ]
        read_only_fields = ["id", "date_joined"]
