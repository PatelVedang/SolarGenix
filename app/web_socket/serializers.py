from rest_framework import serializers

class SendMessageSerializer(serializers.Serializer):
    room = serializers.CharField()
    data = serializers.JSONField()