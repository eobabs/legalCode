import requests
import json
from django.conf import settings
import secrets
import string

class PaystackPayment:
    def __init__(self ):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"

    def generate_reference(self ):
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    def initialize_payment(self, email, amount, case_id, user_id, message="", is_anonymous=False):
        url = f"{self.base_url}/transaction/initialize"


        amount_in_kobo = int(float(amount) * 100)

        reference = self.generate_reference()

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": amount_in_kobo,
            "reference": reference,
            "callback_url": f"{settings.SITE_URL}/payment/callback/",
            "metadata": {
                "case_id": case_id,
                "user_id": user_id,
                "message": message,
                "is_anonymous": is_anonymous,
                "original_amount": str(amount)
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json(), reference

    def verify_payment(self, reference):
        url = f"{self.base_url}/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
        }

        response = requests.get(url, headers=headers)
        return response.json()