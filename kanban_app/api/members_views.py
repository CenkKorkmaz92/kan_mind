from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from users_app.api.serializers import UserSerializer


class BoardMembersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        """
        Retrieve the list of members for a given board if the user is the owner or a member.
        Returns 403 if the user is not authorized or the board does not exist.
        """
        from kanban_app.models import Board
        board = Board.objects.filter(id=board_id).first()
        if not board or (request.user != board.owner and request.user not in board.members.all()):
            return Response({'detail': 'Forbidden.'}, status=403)
        members = board.members.all()
        data = UserSerializer(members, many=True).data
        return Response(data)
