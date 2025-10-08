from rest_framework import permissions

class IsCreatorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False
            
        return obj.created_by == request.user or request.user in obj.admins.all()
     
