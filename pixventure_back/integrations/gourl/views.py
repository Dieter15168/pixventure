import hashlib
from decimal import Decimal
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from integrations.gourl.models import GoURLConfig
from payments.models import Transaction
from integrations.gourl.models import PaymentCallbackLog
from payments.manager import PaymentManager

@csrf_exempt
def callback(request, *args, **kwargs):
    """
    Handles the GoURL IPN callback.

    Expects POST data with fields such as:
      - status
      - private_key_hash
      - order
      - amountusd
      - coinlabel
      - confirmed
      - (and other optional fields)

    Behavior:
      1. Verifies the incoming private_key_hash against the stored GoURL configuration.
      2. Retrieves the corresponding Transaction using the external_order_id (order).
      3. Logs the callback in PaymentCallbackLog with:
            - status: 0 if status=="payment_received", else 1.
            - confirmed: True if confirmed=="1", else False.
            - raw_data: All received callback data.
      4. Processes the callback:
         - For unconfirmed payment (confirmed == "0" and status == "payment_received"):
             * If the received amount (amountusd) matches the transaction amount, update the transaction's
               metadata and set its status to success (STATUS_COMPLETED).
         - For confirmed payment (confirmed == "1"):
             * Only log the callback without changing the transaction's status.
      5. Returns the appropriate response string ("cryptobox_newrecord", "cryptobox_updated", or "cryptobox_nochanges").
    """
    if request.method != 'POST':
        return HttpResponse("Only POST Data Allowed")
    
    post_data = request.POST

    # Extract required fields.
    status_field = post_data.get("status", "")
    received_private_key_hash = post_data.get("private_key_hash", "")
    order = post_data.get("order", "")
    coinlabel = post_data.get("coinlabel", "")
    amountusd_str = post_data.get("amountusd", "0")
    try:
        amountusd = Decimal(amountusd_str)
    except Exception:
        amountusd = Decimal("0")
    confirmed = post_data.get("confirmed", "")

    # Retrieve GoURL configuration for the coin.
    try:
        config = GoURLConfig.objects.get(coin=coinlabel)
    except GoURLConfig.DoesNotExist:
        return HttpResponse("cryptobox_nochanges")
    
    # Compute expected private key hash using SHA512.
    expected_hash = hashlib.sha512(config.private_key.encode('utf-8')).hexdigest()
    if received_private_key_hash != expected_hash:
        return HttpResponse("cryptobox_nochanges")
    
    # Retrieve the transaction using the external order id.
    try:
        transaction = Transaction.objects.get(external_order_id=order)
    except Transaction.DoesNotExist:
        return HttpResponse("cryptobox_nochanges")
    
    # Log the callback.
    # Determine status code: 0 for "payment_received", 1 for "payment_received_unrecognised"
    log_status = 0 if status_field == "payment_received" else 1
    log_confirmed = True if confirmed == "1" else False
    # Convert QueryDict to a standard dict (values become lists).
    raw_data = { key: post_data.getlist(key) if len(post_data.getlist(key)) > 1 else post_data.get(key) for key in post_data }
    
    PaymentCallbackLog.objects.create(
        transaction=transaction,
        user=transaction.user,
        status=log_status,
        confirmed=log_confirmed,
        raw_data=raw_data
    )
    
    current_time = timezone.now().isoformat()
    payment_manager = PaymentManager()

    # Process unconfirmed payment: treat as successful.
    if confirmed == "0" and status_field == "payment_received":
        if transaction.amount == amountusd:
            metadata = {
                "payment_received": True,
                "received_at": current_time,
                "raw_amountusd": str(amountusd)
            }
            # Set transaction status to success.
            payment_manager.update_transaction(transaction, target_status=Transaction.STATUS_COMPLETED, metadata_updates=metadata)
            return HttpResponse("cryptobox_newrecord")
        else:
            return HttpResponse("cryptobox_nochanges")
    
    # For confirmed payment, simply log and do not update transaction.
    elif confirmed == "1":
        # Optionally, you might update metadata for logging purposes only.
        metadata = {
            "payment_confirmed": True,
            "confirmed_at": current_time,
            "raw_amountusd": str(amountusd),
            "additional_info": {
                "addr": post_data.get("addr", ""),
                "tx": post_data.get("tx", "")
            }
        }
        # For confirmed callbacks, we do not change the transaction status.
        payment_manager.update_transaction(transaction, target_status=None, metadata_updates=metadata)
        return HttpResponse("cryptobox_updated")
    
    else:
        return HttpResponse("cryptobox_nochanges")
