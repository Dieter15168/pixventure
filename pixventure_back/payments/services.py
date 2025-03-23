# payments/services.py

from payments.models import Transaction, PaymentMethod
from django.contrib.auth import get_user_model
from integrations.gourl.integration import GoUrlIntegration

User = get_user_model()

# Simple registry mapping payment method names to integration instances.
INTEGRATION_REGISTRY = {
    'gourl': GoUrlIntegration(),  # Ensure the PaymentMethod.name matches "GoUrl"
}

def get_or_create_transaction(user: User, payment_method: PaymentMethod, amount, external_order_id=None) -> Transaction:
    """
    Retrieve an existing pending transaction or create a new one.
    """
    transaction, created = Transaction.objects.get_or_create(
        user=user,
        payment_method=payment_method,
        amount=amount,
        status=Transaction.STATUS_PENDING,
        defaults={'external_order_id': external_order_id}
    )
    return transaction

def process_payment(user, payment_method: PaymentMethod, amount):
    """
    Process the payment by retrieving or creating a transaction and interfacing with the appropriate integration.
    Returns the context required by the frontend.
    """
    transaction = get_or_create_transaction(user, payment_method, amount)
    # Look up the integration based on the payment method name.
    integration = INTEGRATION_REGISTRY.get(payment_method.provider.name)
    if not integration:
        raise Exception("Payment integration not found for this method")
    
    context = integration.create_transaction_context(transaction)
    return context
