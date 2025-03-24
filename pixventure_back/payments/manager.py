"""
Payment Manager Module

This module provides a generic PaymentManager class that offers a generic interface
for processing payment callbacks from various integrations. Instead of receiving
a Transaction entity directly, it now accepts a transaction ID. This reduces coupling
and ensures that the most current version of the Transaction is retrieved from the database.
"""

from payments.models import Transaction
from django.utils import timezone

class PaymentManager:
    """
    A generic Payment Manager for processing payment callbacks.
    """

    def update_transaction(self, transaction_id: int, target_status: int = None, metadata_updates: dict = None):
        """
        Update the Transaction identified by transaction_id with the provided status and metadata.

        Args:
            transaction_id (int): The ID of the Transaction to update.
            target_status (int, optional): The new status to set for the Transaction.
                                           If None, the status remains unchanged.
            metadata_updates (dict, optional): Additional metadata to merge into the Transaction's metadata.

        Returns:
            None
        """
        # Retrieve the latest transaction instance.
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise Exception(f"Transaction with id {transaction_id} does not exist.")
        
        if metadata_updates:
            current_metadata = transaction.metadata or {}
            current_metadata.update(metadata_updates)
            transaction.metadata = current_metadata
        
        if target_status is not None:
            transaction.status = target_status
        
        transaction.save(update_fields=["metadata", "status", "updated_at"])
        # Placeholder for additional business logic, e.g. notifying membership manager.
