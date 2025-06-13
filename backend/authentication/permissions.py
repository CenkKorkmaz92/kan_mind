"""
Custom permissions for the authentication app (Kanban backend).
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardMember(BasePermission):
    """
    Allows access only to members of the board (including the owner).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # obj can be Board, Task, or Comment (with .board)
        board = getattr(obj, 'board', obj)
        return board.owner == user or board.members.filter(id=user.id).exists()


class IsBoardOwner(BasePermission):
    """
    Allows access only to the owner of the board.
    """

    def has_object_permission(self, request, view, obj):
        board = getattr(obj, 'board', obj)
        return board.owner == request.user


class IsCommentAuthor(BasePermission):
    """
    Allows access only to the author of the comment.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
