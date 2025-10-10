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
    def has_object_permission(self, request, view, obj):
        # The 'obj' passed here is the Task instance.
        # We need to check if the user is a member of that task's class.

        # Ensure the object has a class_obj attribute before proceeding
        if not hasattr(obj, "class_obj"):
            return False

        class_instance = obj.class_obj

        is_member = request.user in class_instance.members.all()
        is_expert = request.user in class_instance.experts.all()
        is_admin = request.user in class_instance.admins.all()

        # If the user has any of these roles, grant permission.
        return is_member or is_expert or is_admin


class IsSubmissionOwner(permissions.BasePermission):
    """
    Allow only the owner of a submission to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
