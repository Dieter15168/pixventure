# payments/urls.py
from django.urls import path
from .views import PaymentSetupView, PaymentMethodViewSet, PaymentUpdateView

urlpatterns = [
    path('setup/', PaymentSetupView.as_view(), name='payment-setup'),
    path('update/', PaymentUpdateView.as_view(), name='payment-update'),
    path('methods/', PaymentMethodViewSet.as_view({'get': 'list'}), name='payment-methods'),
]