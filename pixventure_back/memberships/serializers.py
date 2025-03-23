# memberships/serializers.py

from rest_framework import serializers
from .models import MembershipPlan

class MembershipPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for MembershipPlan model.
    """
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'duration_days', 'price', 'currency']
