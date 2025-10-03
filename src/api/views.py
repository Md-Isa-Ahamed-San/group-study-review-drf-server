
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get','patch','put',"delete"], url_path='(?P<email>.+)')
    def by_email(self, request, email=None):
        user = get_object_or_404(User, email=email)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
