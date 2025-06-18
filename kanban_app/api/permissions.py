"""
Custom permission classes for Kanban app API.
Enforce board, task, and comment ownership and membership rules.
"""

from rest_framework import permissions
from kanban_app.models import Board, Task, Comment
from django.contrib.auth.models import User


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission: allow if user is board owner or member.
    """

    def has_object_permission(self, request, view, obj):
        """Return True if user is owner or member of the board."""
        return request.user == obj.owner or request.user in obj.members.all()


class IsBoardOwner(permissions.BasePermission):
    """
    Permission: allow only if user is board owner.
    """

    def has_object_permission(self, request, view, obj):
        """Return True if user is the owner of the board."""
        return request.user == obj.owner


class IsTaskOwnerOrBoardOwner(permissions.BasePermission):
    """
    Permission: allow if user is task creator or board owner.
    """

    def has_object_permission(self, request, view, obj):
        """Return True if user is task creator or board owner."""
        return request.user == obj.created_by or request.user == obj.board.owner


class IsCommentAuthor(permissions.BasePermission):
    """
    Permission: allow only if user is comment author.
    """

    def has_object_permission(self, request, view, obj):
        """Return True if user is the author of the comment."""
        return request.user == obj.author


class IsBoardMemberAndAssigneeReviewerValid(permissions.BasePermission):
    """
    Custom permission: Only board members can create tasks, and assignee/reviewer (if given) must also be board members.
    """

    def has_permission(self, request, view):
        board_id = request.data.get('board')
        if not board_id:
            return False
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Board not found.')
        if request.user not in board.members.all():
            return False
        assignee_id = request.data.get('assignee_id')
        reviewer_id = request.data.get('reviewer_id')
        if assignee_id:
            assignee = User.objects.filter(id=assignee_id).first()
            if not assignee:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'assignee_id': 'Assignee does not exist.'})
            if assignee not in board.members.all():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Assignee must be a board member.')
        if reviewer_id:
            reviewer = User.objects.filter(id=reviewer_id).first()
            if not reviewer:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'reviewer_id': 'Reviewer does not exist.'})
            if reviewer not in board.members.all():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Reviewer must be a board member.')
        return True
