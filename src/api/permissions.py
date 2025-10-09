from rest_framework import permissions

from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsCreatorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False
            
        return obj.created_by == request.user or request.user in obj.admins.all()
     
class IsTaskCreatorOrClassExpert(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the creator of the task or a class admin.
        is_creator = obj.created_by == request.user
        is_class_expert = request.user in obj.class_obj.experts.all()
        return is_creator or is_class_expert

class IsClassMember(BasePermission):
    """
    Allows access only to users who are members, experts, or admins of the class.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any member of the class
        if request.method in SAFE_METHODS:
            return request.user in obj.class_obj.members.all() or \
                   request.user in obj.class_obj.experts.all() or \
                   request.user in obj.class_obj.admins.all()
        return False

