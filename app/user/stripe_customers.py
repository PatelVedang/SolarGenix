import stripe
from django.conf import settings
stripe.api_key=settings.STRIPE_SECRET_KEY
from user.models import User

users = User.objects.all()
for u in users:
    u.stripe_customer_id=""
    u.save()