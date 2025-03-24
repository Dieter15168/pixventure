import hashlib
import base64
import random
import requests
from datetime import timedelta
from django.utils import timezone
from django.http import HttpRequest

from payments.integrations.base import PaymentIntegration
from payments.models import Transaction
from integrations.gourl.models import GoURLConfig

class GoUrlIntegration(PaymentIntegration):
    """
    Real implementation of the GoURL payment integration.
    Dynamically determines the coin type from the PaymentMethod,
    constructs a request to the GoURL API using configuration data stored in GoURLConfig,
    and returns the payment context.
    """

    def get_client_ip(self, request: HttpRequest = None) -> str:
        """
        Attempts to extract the real user IP address from the incoming request.
        Falls back to 127.0.0.1 if unavailable or request is None.
        """
        if request:
            print(request)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
                if ip:
                    return ip
            ip = request.META.get('REMOTE_ADDR')
            if ip:
                return ip
        return "127.0.0.1"

    def create_transaction_context(self, transaction: Transaction, request: HttpRequest = None) -> dict:
        method_name = transaction.payment_method.name.upper() if transaction.payment_method else None
        coin = method_name or "BTC"

        try:
            config = GoURLConfig.objects.get(coin=coin)
        except GoURLConfig.DoesNotExist:
            raise Exception(f"GoURL configuration for coin '{coin}' not found.")

        boxID = config.box_id
        private_key = config.private_key
        public_key = config.public_key
        coin_code = coin
        coin_name = (
            "bitcoin" if coin == "BTC"
            else "dogecoin" if coin == "DOGE"
            else "bitcoincash" if coin == "BCH"
            else coin.lower()
        )

        webdev_key = ''
        amount = 0
        period = 'NOEXPIRY'
        amountUSD = str(transaction.amount)
        userID = str(transaction.user.id)
        language = 'en'
        orderID = str(transaction.id)
        ip = self.get_client_ip(request)

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

        calculated_hash = compute_hash(
            boxID, coin_name, public_key, private_key, webdev_key,
            amount, period, amountUSD, userID, language, orderID, ip
        )

        base64_ip = base64.b64encode(ip.encode('ascii')).decode('utf-8')
        z = random.randint(0, 10000000)

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

        context = {
            'payment_address': response_json.get('addr'),
            'crypto_amount': response_json.get('amount'),
            'wallet_url': response_json.get('wallet_url'),
            'transaction_status': response_json.get('status'),
            'expires_at': (timezone.now() + timedelta(minutes=15)).isoformat()
        }

        return context
