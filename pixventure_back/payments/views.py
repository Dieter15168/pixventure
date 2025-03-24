# payments/views.py

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from memberships.models import MembershipPlan
from memberships.serializers import MembershipPlanSerializer
from payments.models import PaymentMethod
from payments.serializers import PaymentMethodSerializer
from payments.services import process_payment
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving active payment methods.
    """
    serializer_class = PaymentMethodSerializer
    pagination_class = None

    def get_queryset(self):
        # Only return active payment methods.
        return PaymentMethod.objects.filter(is_active=True)


class PaymentSetupView(APIView):
    """
    API endpoint that aggregates membership plans, payment methods, and generates the payment context
    for the default selections.
    """

    @method_decorator(login_required)
    def get(self, request, format=None):
        # Fetch active membership plans and payment methods
        membership_plans = MembershipPlan.objects.filter(is_active=True)
        payment_methods = PaymentMethod.objects.filter(is_active=True)

        if not membership_plans.exists() or not payment_methods.exists():
            return Response({'error': 'No available membership plans or payment methods.'}, status=status.HTTP_400_BAD_REQUEST)

        # Select default membership plan and payment method (first in each queryset)
        default_plan = membership_plans.first()
        default_method = payment_methods.first()

        # Create or retrieve a transaction and generate payment context using the default selection.
        # We use the plan's price as the amount.
        try:
            payment_context = process_payment(request.user, default_method, default_plan.price)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize membership plans and payment methods for response
        membership_serializer = MembershipPlanSerializer(membership_plans, many=True)
        payment_method_serializer = PaymentMethodSerializer(payment_methods, many=True)

        data = {
            'membership_plans': membership_serializer.data,
            'payment_methods': payment_method_serializer.data,
            'default_selected': {
                'membership_plan': membership_serializer.data[0],
                'payment_method': payment_method_serializer.data[0],
                'payment_context': payment_context
            }
        }
        return Response(data, status=status.HTTP_200_OK)
    

class PaymentUpdateView(APIView):
    """
    API endpoint to update the payment context when the user changes the selection
    of a membership plan or payment method.
    
    It creates (or reuses) a transaction for the given user + sum + payment method combination
    and returns the updated payment context.
    """
    def post(self, request, format=None):
        user = request.user
        membership_plan_id = request.data.get('membership_plan_id')
        payment_method_id = request.data.get('payment_method_id')

        if not membership_plan_id or not payment_method_id:
            return Response(
                {'error': 'Missing membership plan or payment method.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership_plan = MembershipPlan.objects.get(id=membership_plan_id, is_active=True)
        except MembershipPlan.DoesNotExist:
            return Response(
                {'error': 'Invalid membership plan.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
        except PaymentMethod.DoesNotExist:
            return Response(
                {'error': 'Invalid payment method.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use the membership plan's price as the amount.
        amount = membership_plan.price

        try:
            # process_payment() uses get_or_create_transaction to either reuse an existing
            # transaction (if one exists for the same user, sum, and payment method) or creates a new one.
            payment_context = process_payment(user, payment_method, amount, request=request)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'payment_context': payment_context}, status=status.HTTP_200_OK)