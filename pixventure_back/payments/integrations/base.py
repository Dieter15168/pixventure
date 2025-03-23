# payments/integrations/base.py

from abc import ABC, abstractmethod
from payments.models import Transaction
from typing import Dict

class PaymentIntegration(ABC):
    """
    Abstract base class for payment integrations.
    """

    @abstractmethod
    def create_transaction_context(self, transaction: Transaction) -> Dict:
        """
        Generate and return the context necessary for processing the payment.
        This should include details like payment address, native crypto amount, etc.
        """
        pass
