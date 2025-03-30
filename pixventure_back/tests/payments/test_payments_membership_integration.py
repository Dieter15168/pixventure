# test_payments_membership_integration.py

import pytest
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
User = get_user_model()

# Import models from memberships and payments apps.
from memberships.models import MembershipPlan, UserMembership
from payments.models import PaymentProvider, PaymentMethod, Transaction
from payments.services import get_or_create_transaction, process_payment
from payments.manager import PaymentManager
from memberships.manager import MembershipManager


# Dummy integration for unit testing process_payment.
class DummyIntegration:
    def create_transaction_context(self, transaction, request=None):
        """
        Dummy integration that returns a simple payment context.
        """
        return {"dummy": "context", "transaction_id": transaction.id}


@pytest.mark.django_db
def test_get_or_create_transaction():
    """
    Unit test for get_or_create_transaction:
    Verifies that a transaction is created with the correct membership plan,
    and that repeated calls with the same parameters yield the same transaction.
    """
    user = User.objects.create_user(username="testuser", password="password")
    plan = MembershipPlan.objects.create(name="Basic", duration_days=30, price=Decimal("10.00"))
    provider = PaymentProvider.objects.create(name="gourl", description="Test Provider")
    payment_method = PaymentMethod.objects.create(provider=provider, name="Test Method", is_active=True)
    
    transaction = get_or_create_transaction(user, payment_method, plan.price, plan)
    assert transaction.user == user, "Transaction user should match the test user."
    assert transaction.membership_plan == plan, "Transaction should be linked to the correct membership plan."

    # Calling the function again should return the same transaction.
    transaction2 = get_or_create_transaction(user, payment_method, plan.price, plan)
    assert transaction.pk == transaction2.pk, (
        "Repeated call with the same parameters should return the same transaction."
    )


@pytest.mark.django_db
def test_process_payment(monkeypatch):
    """
    Unit test for process_payment:
    Uses a dummy integration to verify that the payment context is created correctly.
    """
    user = User.objects.create_user(username="testuser2", password="password")
    plan = MembershipPlan.objects.create(name="Premium", duration_days=30, price=Decimal("20.00"))
    provider = PaymentProvider.objects.create(name="gourl", description="Test Provider")
    payment_method = PaymentMethod.objects.create(provider=provider, name="Test Method", is_active=True)
    
    # Monkey-patch the integration registry to use the DummyIntegration.
    from payments import services
    dummy_integration = DummyIntegration()
    monkeypatch.setitem(services.INTEGRATION_REGISTRY, 'gourl', dummy_integration)
    
    context = process_payment(user, payment_method, plan.price, plan)
    assert context.get("dummy") == "context", (
        "Dummy integration should return a context with key 'dummy' set to 'context'."
    )
    assert "transaction_id" in context and context["transaction_id"] > 0, (
        "Payment context should include a valid transaction ID."
    )


@pytest.mark.django_db
def test_membership_manager_create_membership():
    """
    Unit test for MembershipManager.create_membership:
    Checks that a membership is created correctly and is active.
    """
    user = User.objects.create_user(username="membershiptest", password="password")
    plan = MembershipPlan.objects.create(name="Gold", duration_days=60, price=Decimal("50.00"))
    
    membership_manager = MembershipManager()
    membership = membership_manager.create_membership(user, plan)
    
    assert membership.user == user, "Membership user should match the provided user."
    assert membership.plan == plan, "Membership plan should match the provided plan."
    assert membership.is_currently_active, "Newly created membership should be active."
    assert membership.end_date > timezone.now(), (
        "Membership end_date should be in the future."
    )


@pytest.mark.django_db
def test_payment_manager_update_transaction_creates_membership():
    """
    Unit test for PaymentManager.update_transaction:
    Verifies that when a transaction is updated to completed status,
    a corresponding user membership is created.
    """
    user = User.objects.create_user(username="integrationtest", password="password")
    plan = MembershipPlan.objects.create(name="Silver", duration_days=30, price=Decimal("30.00"))
    provider = PaymentProvider.objects.create(name="gourl", description="Test Provider")
    payment_method = PaymentMethod.objects.create(provider=provider, name="Test Method", is_active=True)
    
    # Create a transaction using the service.
    transaction = get_or_create_transaction(user, payment_method, plan.price, plan)
    
    pm = PaymentManager()
    pm.update_transaction(transaction.id, target_status=Transaction.STATUS_COMPLETED)
    
    # Check that a membership is created for the user.
    membership = UserMembership.objects.filter(user=user, plan=plan).first()
    assert membership is not None, "A membership should be created when the transaction is marked completed."
    assert membership.is_currently_active, "The created membership should be active."


@pytest.mark.django_db
def test_full_payment_flow(monkeypatch):
    """
    Integration test for the complete payment flow:
    Simulates a full cycle from transaction creation via process_payment,
    to an external integration callback that triggers PaymentManager.update_transaction,
    resulting in a new user membership.
    """
    user = User.objects.create_user(username="fullflowtest", password="password")
    plan = MembershipPlan.objects.create(name="Platinum", duration_days=90, price=Decimal("100.00"))
    provider = PaymentProvider.objects.create(name="gourl", description="Test Provider")
    payment_method = PaymentMethod.objects.create(provider=provider, name="Test Method", is_active=True)
    
    # Define a dummy integration that simulates the external payment process.
    class FullFlowDummyIntegration:
        def create_transaction_context(self, transaction, request=None):
            # Simulate the external callback by immediately updating the transaction.
            pm = PaymentManager()
            pm.update_transaction(transaction.id, target_status=Transaction.STATUS_COMPLETED)
            return {"dummy": "context", "transaction_id": transaction.id}
    
    from payments import services
    monkeypatch.setitem(services.INTEGRATION_REGISTRY, 'gourl', FullFlowDummyIntegration())
    
    # Process payment which creates a transaction and calls the dummy integration.
    context = process_payment(user, payment_method, plan.price, plan)
    assert "transaction_id" in context, (
        "The payment context should contain the transaction_id after processing payment."
    )
    
    # Verify that the membership was created as a result of the integration callback.
    membership = UserMembership.objects.filter(user=user, plan=plan).first()
    assert membership is not None, "Membership should be created in the full payment flow."
    assert membership.is_currently_active, "Membership should be active in the full payment flow."
