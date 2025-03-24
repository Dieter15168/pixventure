import hashlib
from decimal import Decimal
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from integrations.gourl.models import GoURLConfig
from payments.models import Transaction
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
      3. Delegates transaction updates to the generic PaymentManager:
         - For unconfirmed payment (confirmed == "0" and status == "payment_received"):
             * If the received amount (amountusd) matches the transaction amount,
               updates the transaction's metadata to mark payment as received.
         - For confirmed payment (confirmed == "1"):
             * Updates the transaction.status to STATUS_COMPLETED and updates metadata accordingly.
      4. Returns the appropriate response string required by the GoURL system.
         ("cryptobox_newrecord", "cryptobox_updated", or "cryptobox_nochanges")
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
    
    # Retrieve GoURL configuration for the coin (e.g. "BTC").
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
    
    current_time = timezone.now().isoformat()
    payment_manager = PaymentManager()

    # Process unconfirmed payment (confirmed == "0" and status == "payment_received").
    if confirmed == "0" and status_field == "payment_received":
        if transaction.amount == amountusd:
            metadata = {
                "payment_received": True,
                "received_at": current_time,
                "raw_amountusd": str(amountusd)
            }
            # Do not change the status (remains pending).
            payment_manager.update_transaction(transaction, target_status=None, metadata_updates=metadata)
            return HttpResponse("cryptobox_newrecord")
        else:
            return HttpResponse("cryptobox_nochanges")
    
    # Process confirmed payment (confirmed == "1").
    elif confirmed == "1":
        metadata = {
            "payment_confirmed": True,
            "confirmed_at": current_time,
            "raw_amountusd": str(amountusd),
            "additional_info": {
                "addr": post_data.get("addr", ""),
                "tx": post_data.get("tx", "")
            }
        }
        payment_manager.update_transaction(transaction, target_status=Transaction.STATUS_COMPLETED, metadata_updates=metadata)
        return HttpResponse("cryptobox_updated")
    
    # Default: no changes.
    else:
        return HttpResponse("cryptobox_nochanges")
