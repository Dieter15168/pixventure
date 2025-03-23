# memberships/views.py

from rest_framework import viewsets
from .models import MembershipPlan
from .serializers import MembershipPlanSerializer

class MembershipPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving active membership plans.
    """
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    pagination_class = None
