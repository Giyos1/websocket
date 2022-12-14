
from io import BytesIO
from home.utils import split_on_silence, rechunk
from pydub import AudioSegment
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
        print("got")
        print(message)
        pass


class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.audio_segment = None
        await self.accept()

    async def disconnect(self, *args, **kwargs):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not bytes_data:
            return
        audio_segment = AudioSegment(bytes_data, sample_width=2, frame_rate=16000, channels=1)

        if self.audio_segment is None:
            self.audio_segment = audio_segment
        else:
            self.audio_segment += audio_segment

        if len(self.audio_segment) > 4000:
            chunks = split_on_silence(self.audio_segment)
            rechunks = [v for v in rechunk(chunks, 3000)]
            if len(rechunks) > 1:
                for chunk, start, end in rechunks:
                    wavIO=BytesIO()
                    chunk.export(wavIO, format="wav")
                    await self.channel_layer.send(
                        'audio',
                        {
                            'type': 'speechtotext',
                            'response_channel': self.channel_name,
                            'bytes': wavIO.getvalue(),
                        }
                    )

    async def ws_data(self, event):
        await self.send(text_data=event['text'])
