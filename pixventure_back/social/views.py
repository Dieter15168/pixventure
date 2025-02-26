# social/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .utils import toggle_like

class LikeToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        target_type = request.data.get('target_type')
        target_id = request.data.get('target_id')
        action = request.data.get('action')  # "like" or "unlike"

        if not target_type or not target_id or not action:
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action not in ['like', 'unlike']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        like_flag = True if action == 'like' else False

        try:
            toggle_like(user, target_type, int(target_id), like=like_flag)
            return Response({'success': f"{action}d successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
