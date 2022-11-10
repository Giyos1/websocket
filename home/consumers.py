import json

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from models import get_audio


class TestConsumer(AsyncWebsocketConsumer):
    # ws://
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            "notification",
            self.channel_name,
        )
        await self.send(text_data=json.dumps({'status': 'connected from django channels'}))

    # async def receive(self, text_data):
    #     print(text_data)
    #     self.send(text_data=json.dumps({'status': 'we got you'}))

    async def disconnect(self, *args, **kwargs):
        await self.channel_layer.group_discard(
            "notification",
            self.channel_name,
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_notification',
            'value': event['value']
        }))

    async def ws_data(self, event):
        # Send data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'data',
            'data': event['data']
        }))


class AudioConsumer(AsyncConsumer):

    async def process(self, message):
        text = message.get('text')

        text_list = text.split()
        await self.channel_layer.group_send(
            'notification', {
                'type': 'send.notification',
                'value': 'sozlarni bolib oldi'
            }
        )
        for i in range(0, len(text_list) - 3, 3):
            audio = get_audio(" ".join(text_list[i:i + 3]))
            await self.channel_layer.group_send(
                'notification',
                {
                    'type': 'ws.data',
                    'data': {
                        'type': 'new_chunk',
                        'number': f"{i}-word",
                        'audio': audio
                    }
                }
            )
