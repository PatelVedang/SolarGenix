from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

def send(room, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room,
        {
            'type': 'send_notification',
            'message': json.dumps(data)
        }
    )