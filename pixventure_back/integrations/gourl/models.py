# integrations/gourl/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GoURLConfig(models.Model):
    """
    Stores GoURL provider configuration data such as private keys,
    associated with a PaymentProvider record and keyed by coin.
    """
    coin = models.CharField(max_length=10)  # e.g. BTC, BCH, DOGE
    box_id = models.IntegerField(null=True)
    private_key = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.coin} config"


class PaymentCallbackLog(models.Model):
    """
    Logs payment callback data from integrations such as GoURL.

    Fields:
      - transaction: Related transaction.
      - user: The user associated with the transaction.
      - status: An integer indicating callback status.
                For example, 0 for "payment_received" and 1 for "payment_received_unrecognised".
      - confirmed: Boolean indicating if the callback indicates confirmed payment.
      - raw_data: JSON field storing the raw callback data.
      - created_at: Timestamp of when the callback was logged.
    """
    STATUS_CHOICES = (
        (0, "payment_received"),
        (1, "payment_received_unrecognised"),
    )

    transaction = models.ForeignKey('payments.Transaction', on_delete=models.CASCADE, related_name='callback_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_callback_logs')
    status = models.IntegerField(choices=STATUS_CHOICES)
    confirmed = models.BooleanField(default=False)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CallbackLog for Transaction {self.transaction.id} by {self.user.username}"