from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and (
                obj.author == request.user
                or request.user.is_superuser
            )
        )
