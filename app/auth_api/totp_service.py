import pyotp
import qrcode
import io
import base64


class TOTPService:
    def __init__(self, user):
        self.user = user
        self.secret = user.totp_secret or pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret)

    def generate_secret(self):
        self.user.totp_secret = self.secret
        self.user.save(update_fields=["totp_secret"])
        return self.secret

    def get_provisioning_uri(self):
        return self.totp.provisioning_uri(name=self.user.email)

    def generate_qr_code_url(self):
        otp_uri = self.get_provisioning_uri()
        qr = qrcode.make(otp_uri)

        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{qr_base64}"

    def verify_code(self, code):
        return self.totp.verify(code)
