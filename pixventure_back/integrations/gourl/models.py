# integrations/gourl/models.py

from django.db import models
from payments.models import PaymentProvider

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
