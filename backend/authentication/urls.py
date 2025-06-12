from django.urls import path
from .views import RegistrationView, LoginView, BoardListCreateView, BoardDetailUpdateView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:board_id>/', BoardDetailUpdateView.as_view(), name='board-detail-update'),
]
