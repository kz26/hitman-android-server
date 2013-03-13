from rest_framework import permissions

class IsInGame(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.games.all().exists()
