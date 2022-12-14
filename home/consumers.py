import json

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from models import get_audio


class TestConsumer(AsyncWebsocketConsumer):
    # ws://
    async def connect(self):
        await self.accept()
        # await self.channel_layer.group_add(
        #     self.channel_group,
        #     self.channel_name,
        # )
        # await self.send(text_data=json.dumps({'status': 'connected from django channels'}))

    async def disconnect(self, *args, **kwargs):
        pass
        # await self.channel_layer.group_discard(
        #     "notification",
        #     self.channel_name,
        # )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        await self.channel_layer.send('audio', {
            'type': 'process',
            'text': text_data,
            'response_channel': self.channel_name,
        })

    async def ws_data(self, event):
        # Send data to WebSocket
        await self.send(bytes_data=event['audio'])


class AudioConsumer(AsyncConsumer):

    async def process(self, message):
        response_channel = message.get('response_channel')
        text = message.get('text')

        text_list = text.split()

        while len(text_list) > 5:
            audio = get_audio(" ".join(text_list[0:3]))
            text_list = text_list[3:]
            await self.channel_layer.send(
                response_channel,
                {
                    'type': 'ws.data',
                    'audio': audio,
                }
            )
        if len(text_list) > 0:
            audio = get_audio(" ".join(text_list))
            await self.channel_layer.send(
                response_channel,
                {
                    'type': 'ws.data',
                    'audio': audio,
                }
            )

    async def speechtotext(self, message):
        pass


class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, *args, **kwargs):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not bytes_data:
            return
        await self.channel_layer.send('audio', {
            'type': 'speechtotext',
            'bytes': bytes_data,
            'response_channel': self.channel_name,
        })

    async def ws_data(self, event):
        await self.send(text_data=event['text'])
