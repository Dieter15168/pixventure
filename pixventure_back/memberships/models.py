# memberships/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class MembershipPlan(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, unique=True)
    duration_days = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"
    
    def get_expiration_date(self, start_date):
        return start_date + timedelta(days=self.duration_days)

class UserMembership(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='user_memberships')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Membership of {self.user.username} for {self.plan.name}"

    def save(self, *args, **kwargs):
        # If the instance is new and end_date hasn't been provided,
        # ensure that start_date is set before computing end_date.
        if not self.pk and not self.end_date:
            if self.start_date is None:
                self.start_date = timezone.now()
            self.end_date = self.plan.get_expiration_date(self.start_date)
        super().save(*args, **kwargs)

    @property
    def is_currently_active(self):
        if not self.is_active:
            return False
        elif self.end_date:
            return self.end_date > timezone.now()
        else:
            return False
        