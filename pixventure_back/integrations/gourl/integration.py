import hashlib
import base64
import random
import requests
import json
from datetime import timedelta
from django.utils import timezone

from payments.integrations.base import PaymentIntegration
from payments.models import Transaction
from integrations.gourl.models import GoURLConfig

class GoUrlIntegration(PaymentIntegration):
    """
    Real implementation of the GoURL payment integration.
    This class constructs a request to the GoURL API using configuration data stored in the GoURLConfig model,
    sends the request, and returns the payment context needed by the frontend.
    """

    def create_transaction_context(self, transaction: Transaction) -> dict:
        # For this example, assume the coin type is 'BTC'. Extend as needed for other coins.
        coin = "BTC"
        
        # Retrieve GoURL configuration for the specified coin.
        try:
            config = GoURLConfig.objects.get(coin=coin)
        except GoURLConfig.DoesNotExist:
            raise Exception(f"GoURL configuration for coin '{coin}' not found.")
        
        # Retrieve configuration values from the model.
        boxID = config.box_id
        private_key = config.private_key
        public_key = config.public_key  # Now coming directly from the model.
        
        # Define static parameters.
        coin_code = coin
        coin_name = "bitcoin"  # Adjust if supporting other coins like BCH or DOGE.
        webdev_key = ''        # Legacy integration uses an empty webdev_key.
        amount = 0             # The amount in crypto is determined by GoURL.
        period = 'NOEXPIRY'
        amountUSD = str(transaction.amount)  # Transaction amount in USD as string.
        userID = str(transaction.user.id)
        language = 'en'
        orderID = str(transaction.id)
        ip = "127.0.0.1"       # Use a default IP; in production, use the actual client IP.
        
        # Helper function to compute the required MD5 hash.
        def compute_hash(boxID, coin_name, public_key, private_key, webdev_key,
                         amount, period, amountUSD, userID, language, orderID, ip):
            user_format = 'MANUAL'
            values = [
                str(boxID), coin_name, public_key, private_key, webdev_key,
                str(amount), str(amountUSD), period, language,
                orderID, userID, user_format, ip
            ]
            string = '|'.join(values)
            m = hashlib.md5(string.encode('utf-8'))
            return m.hexdigest()

        calculated_hash = compute_hash(boxID, coin_name, public_key, private_key, webdev_key,
                                       amount, period, amountUSD, userID, language, orderID, ip)
        
        # Base64-encode the IP address.
        base64_ip = base64.b64encode(ip.encode('ascii')).decode('utf-8')
        
        # Random integer for cache-busting.
        z = random.randint(0, 10000000)
        
        # Construct the API request URL following GoURL specification.
        request_url = (
            f"https://coins.gourl.io/b/{boxID}/c/{coin_name}/p/{public_key}/a/{amount}"
            f"/au/{amountUSD}/pe/{period}/l/{language}/o/{orderID}/u/{userID}/us/MANUAL"
            f"/j/1/d/{base64_ip}/h/{calculated_hash}/z/{z}"
        )
        
        try:
            response = requests.get(request_url, verify=False, timeout=10)
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            raise Exception(f"Error communicating with GoURL API: {e}")
        
        # Extract fields from the response.
        status_response = response_json.get('status')
        crypto_amount = response_json.get('amount')
        wallet_url = response_json.get('wallet_url')
        addr = response_json.get('addr')
        confirmed = response_json.get('confirmed')
        
        # Build the payment context to return.
        context = {
            'payment_address': addr,
            'crypto_amount': crypto_amount,
            'wallet_url': wallet_url,
            'transaction_status': status_response,
            # Set expiration 15 minutes from now.
            'expires_at': (timezone.now() + timedelta(minutes=15)).isoformat()
        }
        
        return context
