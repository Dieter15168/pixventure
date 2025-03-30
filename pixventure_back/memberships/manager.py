# memberships/manager.py

from django.utils import timezone
from memberships.models import UserMembership, MembershipPlan

class MembershipManager:
    """
    Manager for handling user memberships.
    Provides methods to create and manage memberships in a modular way.
    """

    def create_membership(self, user, membership_plan: MembershipPlan):
        """
        Create a new membership for the user using the specified membership plan.
        
        If the user already has an active membership, this method could be extended to
        either extend the current membership or replace it.
        
        Args:
            user: The user for whom the membership is created.
            membership_plan: The membership plan selected by the user.
            
        Returns:
            The newly created UserMembership instance.
        """
        # Future improvement: Check if the user has an active membership and handle accordingly.
        membership = UserMembership.objects.create(
            user=user,
            plan=membership_plan
        )
        # Optionally, trigger notifications or logging here.
        return membership
