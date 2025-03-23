# memberships/urls.py
from django.urls import path
from .views import MembershipPlanViewSet

urlpatterns = [
    path('plans/', MembershipPlanViewSet.as_view({'get': 'list'}), name='membership-plans'),
]