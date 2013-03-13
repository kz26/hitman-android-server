from rest_framework import permissions

class IsInGame(permissions.BasePermission):
    def has_permission(self, request, view):
        games = request.user.games.all()
        return games.exists() and not games[0].has_ended()
