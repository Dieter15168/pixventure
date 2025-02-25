# views.py

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from memberships.utils import check_if_user_is_paying

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            is_active_member = check_if_user_is_paying(user)

            return Response({
                'token': token.key,
                'id': user.id,
                'username': user.username,
                'is_active_member': is_active_member,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class CheckAuthAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_active_member = check_if_user_is_paying(request.user)

        # Pass the success status, respond with the id of the logged in user and serialized avatar data
        return Response({
            'username': request.user.username,
            'is_active_member': is_active_member,
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Check for unique email and username
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create user if all validations pass
            user = serializer.save()

            # Create user profile for this user
            user_profile = UserProfile(user=user).save()

            return Response({'success': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)