import logging
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger("django")

class SMSService:
    """
    Service class to handle sending SMS via Twilio.
    """
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials missing. SMS sending will be disabled.")

    def send_sms(self, to_number, message):
        """
        Sends an SMS message to a specified phone number.
        """
        if not self.client:
            logger.error("Twilio client not initialized.")
            return False

        # Check if the number has a country code, if not add +91
        if not to_number.startswith("+"):
            to_number = f"+91{to_number}"
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return False

    def send_otp(self, to_number, otp):
        """
        Sends an OTP message via SMS.
        """
        message = f"Your OTP for SolarGenix is: {otp}. It will expire in {settings.OTP_EXPIRY_MINUTES} minutes."
        return self.send_sms(to_number, message)
