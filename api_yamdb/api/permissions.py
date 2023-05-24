from rest_framework import permissions


class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    """"Права для автора комментария, модератора или администратора."""
    def has_permission(self, request, view):

        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if (request.user.is_staff or request.user.role == 'admin'
                    or request.user.role == 'moderator'
                    or obj.author == request.user
                    or request.method == 'POST'
                    and request.user.is_authenticated):
                return True
        elif request.method in permissions.SAFE_METHODS:
            return True


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Предоставляет права только Авторам."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user and request.user.is_authenticated
                )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                )


class IsAdmin(permissions.BasePermission):
    """Предоставляет права только Админам."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return bool(request.user.is_superuser or request.user.is_staff
                        or request.user.role == 'admin')


class IsAdminOrReadOnly(permissions.BasePermission):
    """"
    Предоставляет полные права только Админу,
    в ином случае только Чтение.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return bool(request.user.is_superuser or request.user.is_staff
                        or request.user.role == 'admin')
