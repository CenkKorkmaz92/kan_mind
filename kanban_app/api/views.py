"""
Views for Kanban app API endpoints: boards, tasks, comments, and related permissions.
Implements CRUD operations, assignment, and permission enforcement for Kanban resources.
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import BoardSerializer, BoardDetailSerializer, TaskSerializer, CommentSerializer
from .permissions import IsBoardOwnerOrMember, IsBoardOwner, IsTaskOwnerOrBoardOwner, IsCommentAuthor, IsBoardMemberAndAssigneeReviewerValid
from kanban_app.models import Board, Task, Comment
from rest_framework.exceptions import PermissionDenied


class BoardListCreateView(generics.ListCreateAPIView):
    """
    API view to list all boards for the user or create a new board.
    Only authenticated users can access this view.
    """
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return all boards where the user is a member or owner.
        """
        return Board.objects.filter(members=self.request.user) | Board.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new board, set the current user as owner and member, and add any additional members.
        """
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)
        members = self.request.data.get('members', [])
        if members:
            users = User.objects.filter(id__in=members)
            board.members.add(*users)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a board.
    Only board owners or members can retrieve; only owners can delete.
    """
    queryset = Board.objects.all()
    permission_classes = [IsBoardOwnerOrMember]

    def get_serializer_class(self):
        """
        Use detailed serializer for GET, basic serializer for PATCH/DELETE.
        """
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardSerializer

    def patch(self, request, *args, **kwargs):
        """
        Update board title or members. Only owner or members can update.
        """
        board = self.get_object()
        if not (request.user == board.owner or request.user in board.members.all()):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        title = request.data.get('title')
        members = request.data.get('members')
        if title:
            board.title = title
        if members is not None:
            users = User.objects.filter(id__in=members)
            board.members.set(users)
        board.save()
        from users_app.api.serializers import UserSerializer
        response_data = {
            "id": board.id,
            "title": board.title,
            "owner_data": UserSerializer(board.owner).data,
            "members_data": UserSerializer(board.members.all(), many=True).data,
        }
        return Response(response_data)

    def delete(self, request, *args, **kwargs):
        """
        Delete the board. Only the owner can delete.
        """
        board = self.get_object()
        if request.user != board.owner:
            return Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    """
    API view to check if an email exists in the system.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Return user info if email exists, else 404. Requires 'email' query param.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'Email required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            return Response({'id': user.id, 'email': user.email, 'fullname': user.first_name})
        except User.DoesNotExist:
            return Response({'detail': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)


class TaskAssignedToMeView(generics.ListAPIView):
    """
    API view to list all tasks assigned to the current user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return all tasks where the user is the assignee.
        """
        return Task.objects.filter(assignee=self.request.user)


class TaskReviewingView(generics.ListAPIView):
    """
    API view to list all tasks where the current user is the reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return all tasks where the user is the reviewer.
        """
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """
    API view to create a new task on a board.
    Only board members can create tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMemberAndAssigneeReviewerValid]

    def perform_create(self, serializer):
        """
        Create a new task, ensuring assignee and reviewer are board members.
        Return 404 if the board does not exist (per API spec).
        """
        board_id = self.request.data.get('board')
        if not board_id:
            from rest_framework.exceptions import NotFound
            raise NotFound('Board not found.')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Board not found.')
        assignee_id = self.request.data.get('assignee_id')
        reviewer_id = self.request.data.get('reviewer_id')
        assignee = User.objects.filter(
            id=assignee_id).first() if assignee_id else None
        reviewer = User.objects.filter(
            id=reviewer_id).first() if reviewer_id else None
        serializer.save(board=board, created_by=self.request.user,
                        assignee=assignee, reviewer=reviewer)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a task.
    Only the task creator or board owner can update/delete.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsTaskOwnerOrBoardOwner]

    def patch(self, request, *args, **kwargs):
        """
        Update a task. Only board members can update. Board cannot be changed.
        """
        task = self.get_object()
        board = task.board
        if request.user not in board.members.all():
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if 'board' in data:
            data.pop('board')
        serializer = TaskSerializer(task, data=data, partial=True)
        if serializer.is_valid():
            assignee_id = data.get('assignee_id')
            reviewer_id = data.get('reviewer_id')
            if assignee_id:
                assignee = User.objects.filter(id=assignee_id).first()
                if assignee and assignee not in board.members.all():
                    return Response({'detail': 'Assignee must be a board member.'}, status=status.HTTP_400_BAD_REQUEST)
                serializer.validated_data['assignee'] = assignee
            if reviewer_id:
                reviewer = User.objects.filter(id=reviewer_id).first()
                if reviewer and reviewer not in board.members.all():
                    return Response({'detail': 'Reviewer must be a board member.'}, status=status.HTTP_400_BAD_REQUEST)
                serializer.validated_data['reviewer'] = reviewer
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Delete a task. Only the creator or board owner can delete.
        """
        task = self.get_object()
        if request.user != task.created_by and request.user != task.board.owner:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentsView(generics.ListCreateAPIView):
    """
    API view to list or create comments for a task.
    Only board members can view or comment.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return all comments for a task if the user is a board member.
        """
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        if self.request.user not in task.board.members.all():
            raise PermissionDenied(
                'You must be a board member to view comments.')
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        """
        Create a comment on a task if the user is a board member.
        """
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        if self.request.user not in task.board.members.all():
            raise PermissionDenied('You must be a board member to comment.')
        serializer.save(task=task, author=self.request.user)


class TaskCommentDeleteView(generics.DestroyAPIView):
    """
    API view to delete a comment. Only the comment author can delete.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthor]
    lookup_url_kwarg = 'comment_id'
