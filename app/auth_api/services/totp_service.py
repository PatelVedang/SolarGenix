import pyotp
import qrcode
import io
import base64


class TOTPService:
    """Service for managing TOTP (Time-based One-Time Password) for user authentication."""
    def __init__(self, user):
        self.user = user
        self.secret = user.totp_secret or pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret)

    def generate_secret(self):
        """Generates a new TOTP secret for the user. If the user already has a secret, it will not change it."""
        self.user.totp_secret = self.secret
        self.user.save(update_fields=["totp_secret"])
        return self.secret

    def get_provisioning_uri(self):
        """Generates a provisioning URI for the TOTP secret, which can be used to set up the TOTP in an authenticator app."""
        return self.totp.provisioning_uri(name=self.user.email)

    def generate_qr_code_url(self):
        """Generates a QR code URL for the TOTP secret, which can be scanned by an authenticator app."""
        otp_uri = self.get_provisioning_uri()
        qr = qrcode.make(otp_uri)

        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{qr_base64}"

    def verify_code(self, code):
        """Verifies the provided TOTP code against the user's secret."""
        return self.totp.verify(code)
