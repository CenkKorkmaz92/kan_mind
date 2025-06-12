from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer, BoardSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardUpdateSerializer, BoardUpdateResponseSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Board
from django.db import models
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.exceptions import ValidationError

class RegistrationView(APIView):
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
            board = Board.objects.prefetch_related('members', 'tasks__assignee', 'tasks__reviewer').get(id=board_id)
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
        serializer = self.get_serializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            updated_board = serializer.save()
            response_serializer = BoardUpdateResponseSerializer(updated_board)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BoardDeleteView(DestroyAPIView):
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
