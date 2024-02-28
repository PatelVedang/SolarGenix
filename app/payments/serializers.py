from rest_framework import serializers
from .models import PaymentHistory

class PaymentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentHistory
        fields = ['id', 'user','stripe_subscription_id','price_id','status','created_at','current_period_start','current_period_end','ip_limit']


class SubscriptionPayloadSerializer(serializers.Serializer):
    price_id = serializers.CharField()
    class Meta:
        fields = ["price_id"]

class CancelSubscriptionSerializer(serializers.Serializer):
    
    class Meta:
        pass