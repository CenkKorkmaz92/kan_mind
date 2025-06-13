from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer, BoardSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardUpdateSerializer, BoardUpdateResponseSerializer, TaskSerializer, CommentSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Board, Task, Comment
from django.db import models
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework import serializers
from .permissions import IsBoardMember, IsBoardOwner, IsCommentAuthor


class RegistrationView(APIView):
    """
    Handles user registration.
    """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "fullname": user.first_name,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Handles user login.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "fullname": user.first_name,
                    "email": user.email,
                    "user_id": user.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardListCreateView(generics.ListCreateAPIView):
    """
    Lists all boards the user is a member of, or creates a new board.
    """
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(models.Q(owner=user) | models.Q(members=user)).distinct()

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


class BoardDetailUpdateView(RetrieveUpdateAPIView):
    """
    Retrieve, update a board. Only owner or members can access.
    """
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    lookup_url_kwarg = 'board_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get(self, request, *args, **kwargs):
        board_id = kwargs.get('board_id')
        try:
            board = Board.objects.prefetch_related(
                'members', 'tasks__assignee', 'tasks__reviewer').get(id=board_id)
        except Board.DoesNotExist:
            return Response({'detail': 'Board not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(board)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        board_id = kwargs.get('board_id')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({'detail': 'Board not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            board, data=request.data, partial=True)
        if serializer.is_valid():
            updated_board = serializer.save()
            response_serializer = BoardUpdateResponseSerializer(updated_board)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDeleteView(DestroyAPIView):
    """
    Deletes a board. Only the owner can delete.
    """
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    lookup_url_kwarg = 'board_id'

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.owner != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the owner can delete this board.')
        instance.delete()


class EmailCheckView(APIView):
    """
    Checks if an email is registered and returns user details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'E-Mail-Adresse fehlt.'}, status=status.HTTP_400_BAD_REQUEST)
        from django.core.validators import validate_email
        try:
            validate_email(email)
        except Exception:
            return Response({'detail': 'Ungültiges E-Mail-Format.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Email nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        fullname = f"{user.first_name} {user.last_name}".strip()
        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': fullname
        }, status=status.HTTP_200_OK)


class TasksAssignedToMeView(ListAPIView):
    """
    Lists all tasks assigned to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user)


class TasksReviewingView(ListAPIView):
    """
    Lists all tasks where the authenticated user is a reviewer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)


class TaskListCreateView(ListCreateAPIView):
    """
    Lists all tasks for boards the user is a member of, or creates a new task.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user)

    def perform_create(self, serializer):
        user = self.request.user
        board_id = self.request.data.get('board')
        assignee_id = self.request.data.get('assignee_id')
        reviewer_id = self.request.data.get('reviewer_id')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise serializers.ValidationError({'board': 'Board not found.'})
        if not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                {'detail': 'Forbidden. Must be a board member.'})
        assignee = User.objects.filter(
            id=assignee_id).first() if assignee_id else None
        reviewer = User.objects.filter(
            id=reviewer_id).first() if reviewer_id else None
        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                {'assignee_id': 'Assignee must be a board member.'})
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError(
                {'reviewer_id': 'Reviewer must be a board member.'})
        serializer.save(board=board, assignee=assignee, reviewer=reviewer)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a task. Only board members can access. Only board owner can delete.
    """
    permission_classes = [IsAuthenticated, IsBoardMember]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        if 'board' in data and int(data['board']) != instance.board.id:
            return Response({'board': 'Changing board is not allowed!'}, status=status.HTTP_400_BAD_REQUEST)
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        board = instance.board
        assignee = User.objects.filter(
            id=assignee_id).first() if assignee_id else None
        reviewer = User.objects.filter(
            id=reviewer_id).first() if reviewer_id else None
        if assignee and not board.members.filter(id=assignee.id).exists():
            return Response({'assignee_id': 'Assignee must be a board member.'}, status=status.HTTP_400_BAD_REQUEST)
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            return Response({'reviewer_id': 'Reviewer must be a board member.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(assignee=assignee, reviewer=reviewer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.board.owner != user:
            return Response({'detail': 'Only the board owner can delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentsListCreateView(ListCreateAPIView):
    """
    List or create comments for a task. Only board members can access.
    """
    permission_classes = [IsAuthenticated, IsBoardMember]
    serializer_class = CommentSerializer

    def get_queryset(self):
        user = self.request.user
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        return Comment.objects.filter(task=task).order_by('created_at')

    def perform_create(self, serializer):
        user = self.request.user
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        serializer.save(task=task, author=user)


class TaskCommentDeleteView(DestroyAPIView):
    """
    Delete a comment from a task. Only the author can delete.
    """
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    serializer_class = CommentSerializer

    def get_object(self):
        user = self.request.user
        task_id = self.kwargs['task_id']
        comment_id = self.kwargs['comment_id']
        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        self.check_object_permissions(self.request, comment)
        return comment
