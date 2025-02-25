# urls.py
from django.urls import path
from .views import UserLoginAPIView, CheckAuthAPIView, UserRegisterAPIView

urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('check-auth/', CheckAuthAPIView.as_view(), name='check-auth'),
    path('signup/', UserRegisterAPIView.as_view(), name='signup'),
]
