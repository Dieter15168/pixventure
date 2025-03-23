import hashlib
from decimal import Decimal
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from integrations.gourl.models import GoURLConfig
from payments.models import Transaction

@csrf_exempt
def callback(request, *args, **kwargs):
    """
    Handles the GoURL IPN callback.

    Expects POST data with fields such as status, private_key_hash, order, amountusd, coinlabel, confirmed, etc.
    
    Behavior:
      - Verifies the incoming private_key_hash using the stored GoURLConfig.
      - Retrieves the corresponding Transaction by external_order_id.
      - For unconfirmed payment (confirmed == "0" and status == "payment_received"):
          * If the received amount (amountusd) matches the transaction amount,
            record in transaction.metadata that the payment was received (with timestamp).
      - For confirmed payment (confirmed == "1"):
          * Update the transaction.status to STATUS_COMPLETED and update metadata.
      - In all other cases, returns "cryptobox_nochanges".
    """
    if request.method != 'POST':
        return HttpResponse("Only POST Data Allowed")
    
    post_data = request.POST

    # Extract required fields from the POST data.
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
    
    # Compute expected hash using SHA512 on the stored private key.
    expected_hash = hashlib.sha512(config.private_key.encode('utf-8')).hexdigest()
    if received_private_key_hash != expected_hash:
        return HttpResponse("cryptobox_nochanges")
    
    # Retrieve the transaction using the external order id.
    try:
        transaction = Transaction.objects.get(external_order_id=order)
    except Transaction.DoesNotExist:
        return HttpResponse("cryptobox_nochanges")
    
    # Prepare metadata updates.
    metadata = transaction.metadata or {}
    current_time = timezone.now().isoformat()
    
    # Case 1: Unconfirmed payment received (confirmed == "0" and status == "payment_received")
    if confirmed == "0" and status_field == "payment_received":
        # Compare the received USD amount to the transaction amount.
        if transaction.amount == amountusd:
            metadata.update({
                "payment_received": True,
                "received_at": current_time,
                "raw_amountusd": str(amountusd)
            })
            transaction.metadata = metadata
            transaction.save(update_fields=["metadata", "updated_at"])
            return HttpResponse("cryptobox_newrecord")
        else:
            return HttpResponse("cryptobox_nochanges")
    
    # Case 2: Payment confirmed (confirmed == "1")
    elif confirmed == "1":
        metadata.update({
            "payment_confirmed": True,
            "confirmed_at": current_time,
            "raw_amountusd": str(amountusd),
            "additional_info": {
                "addr": post_data.get("addr", ""),
                "tx": post_data.get("tx", "")
            }
        })
        transaction.metadata = metadata
        transaction.status = Transaction.STATUS_COMPLETED
        transaction.save(update_fields=["metadata", "status", "updated_at"])
        return HttpResponse("cryptobox_updated")
    
    # Default: No changes.
    else:
        return HttpResponse("cryptobox_nochanges")
