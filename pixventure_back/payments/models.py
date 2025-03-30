# payments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from memberships.models import MembershipPlan

User = get_user_model()

class PaymentProvider(models.Model):
    """
    Model representing a payment provider.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    """
    Model representing a payment method associated with a provider.
    """
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, related_name='payment_methods')
    name = models.CharField(max_length=100)
    icon = models.ImageField(null=True, upload_to='payment_icons/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']  # Order by 'order' field, then by id.

    def __str__(self):
        return f"{self.name} ({self.provider.name})"

class Transaction(models.Model):
    """
    Transaction model for handling payment transactions.
    """
    STATUS_PENDING = 0
    STATUS_COMPLETED = 1
    STATUS_FAILED = 2
    STATUS_EXPIRED = 3

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_EXPIRED, 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    payment_method = models.ForeignKey('payments.PaymentMethod', on_delete=models.PROTECT, related_name='transactions')
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    external_order_id = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def is_expired(self):
        """Check if the transaction has expired."""
        return self.expires_at and timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Transaction {self.id} for user {self.user.username}"