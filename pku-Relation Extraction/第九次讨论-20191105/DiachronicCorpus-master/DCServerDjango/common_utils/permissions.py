from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrPOSTOnly(BasePermission):
    """
    The request is authenticated as a user, or is a post-only request.
    """

    def has_permission(self, request, view):
        return (
            request.method in ['POST'] or
            request.user and
            request.user.is_authenticated
        )


class BelongsToYouOrReadOnly(BasePermission):
    message = '你不是这个实体的所有者，没有修改权限。'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            obj.user == request.user
        )
