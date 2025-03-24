"""
Payment Manager Module

This module provides a generic PaymentManager class which offers a generic interface
for processing payment callbacks from various integrations. The PaymentManager is designed
to be modular and independent of integration-specific details. It receives a transaction,
a target status, and metadata updates, then performs the necessary updates on the transaction
and (optionally) triggers additional business logic (such as calling the membership manager).
"""

from payments.models import Transaction
from django.utils import timezone

class PaymentManager:
    """
    A generic Payment Manager for processing payment callbacks.

    This manager updates the transaction's status and metadata based on the callback result.
    It does not need to know the peculiarities of any specific integration.
    It simply requires:
      - The transaction to update.
      - The target status (if any) to set.
      - A dictionary of metadata updates.
    Optionally, it can execute additional logic (e.g. notify the membership manager).
    """

    def update_transaction(self, transaction: Transaction, target_status: int = None, metadata_updates: dict = None):
        """
        Update the given transaction with the provided status and metadata.

        Args:
            transaction (Transaction): The transaction to update.
            target_status (int, optional): The new status to set for the transaction.
                                           If None, the status remains unchanged.
            metadata_updates (dict, optional): Additional metadata to merge into the transaction's metadata.

        Returns:
            None
        """
        if metadata_updates:
            current_metadata = transaction.metadata or {}
            current_metadata.update(metadata_updates)
            transaction.metadata = current_metadata
        
        if target_status is not None:
            transaction.status = target_status
        
        # Update the transaction (this also refreshes the updated_at timestamp).
        transaction.save(update_fields=["metadata", "status", "updated_at"])
        
        # Placeholder: Trigger additional business logic here if needed.
        # For example, notify the membership manager.
        # self.notify_membership_manager(transaction)
    
    # Optional: Additional methods for future business logic can be added here.
    # def notify_membership_manager(self, transaction: Transaction):
    #     """
    #     Notify the membership manager to update the user's membership status.
    #     (Not implemented yet.)
    #     """
    #     pass
