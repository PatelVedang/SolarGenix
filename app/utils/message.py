from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

def send(room, data):
    """
    It gets the channel layer, and then sends a message to the group with the given room name
    
    :param room: The name of the group to send the message to
    :param data: The data to send to the client
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room,
        {
            'type': 'send_notification',
            'message': json.dumps(data)
        }
    )