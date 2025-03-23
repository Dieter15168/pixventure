# payments/serializers.py

from rest_framework import serializers
from .models import PaymentMethod, PaymentProvider

class PaymentProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentProvider model.
    """
    class Meta:
        model = PaymentProvider
        fields = ['id', 'name', 'description']

class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentMethod model including provider details.
    """
    provider = PaymentProviderSerializer(read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'icon', 'is_active', 'provider']
