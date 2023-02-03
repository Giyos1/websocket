import json
import numpy
import torch
from collections import deque
from pydub import AudioSegment
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from models import get_audio
from .utils import split_on_silence, rechunk
from pydub.silence import split_on_silence as split_on_silences
from stt import speechtotext
from .utils import get_time,replace_numbers_with_words_uzbek,get_weather_json_to_word

yahshi = get_audio("yahshi raxmat")
voyeeeey = get_audio("voyeeeey, uyaltirmaaaang")
tushunmadim = get_audio("sizni yahshi tushunmadim")


def hasTalked(dq, audio_segment):
    sortedDQ = sorted(list(dq))
    bottom40Middle = sum(sortedDQ[0:40]) / 40
    parts = split_on_silences(audio_segment, min_silence_len=200, silence_thresh=bottom40Middle + 32)
    if len(parts) == 0:
        return False
    print(sum(parts))
    return sum(parts)

class TestConsumer(AsyncWebsocketConsumer):
    # ws://
    async def connect(self):
        await self.accept()

    async def disconnect(self, *args, **kwargs):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        await self.channel_layer.send('audio', {
            'type': 'process',
            'text': text_data,
            'response_channel': self.channel_name,
            'response_type': 'ws.data',
        })

    async def ws_data(self, event):
        # Send data to WebSocket
        await self.send(bytes_data=event['audio'])


class AudioConsumer(AsyncConsumer):

    async def process(self, message):
        response_channel = message.get('response_channel')
        response_type = message.get('response_type')
        text = message.get('text')
        text = replace_numbers_with_words_uzbek(text)
        text_list = text.split()

        while len(text_list) > 5:
            audio = get_audio(" ".join(text_list[0:3]))
            text_list = text_list[3:]
            await self.channel_layer.send(
                response_channel,
                {
                    'type': response_type,
                    'audio': audio,
                }
            )
        if len(text_list) > 0:
            audio = get_audio(" ".join(text_list))
            await self.channel_layer.send(
                response_channel,
                {
                    'type': response_type,
                    'audio': audio,
                }
            )

    async def speechtotext(self, message):
        sound = AudioSegment(data=message.get('bytes'), sample_width=2, frame_rate=16000, channels=1)
        text = speechtotext(sound)

        if text:
            await self.channel_layer.send(
                message.get('response_channel'),
                {
                    'type': message.get('response_type'),
                    'text': text,
                    'is_final': message.get('is_final'),
                }
            )


class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.audio_segment = None
        self.count = 0
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

        self.count += 1
        if self.count % 8 == 0:
            chunks = split_on_silence(self.audio_segment)
            rechunks = [v for v in rechunk(chunks, 3000)]
            cutoff = 0

            for index, (chunk, start, end) in enumerate(rechunks):
                await self.channel_layer.send(
                    'audio',
                    {
                        'type': 'speechtotext',
                        'response_type': 'ws.data',
                        'response_channel': self.channel_name,
                        'bytes': chunk.raw_data,
                        'is_final': index != len(rechunks) - 1,
                    }
                )
                if index != len(rechunks) - 1:
                    cutoff = end

            if cutoff > 0:
                self.audio_segment = self.audio_segment[cutoff:]

    async def ws_data(self, message):
        await self.send(text_data=json.dumps({
            'text': message.get('text'),
            'is_final': message.get('is_final'),
        }))


class OyqizConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.audio_segment = None
        self.count = 0
        self.dBFS = None
        self.listening = False
        await self.accept()

    async def disconnect(self, *args, **kwargs):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not bytes_data:
            return
        audio_segment = AudioSegment(bytes_data, sample_width=2, frame_rate=16000, channels=1)
        if audio_segment.dBFS != float("-inf") and audio_segment.dBFS > -80.0:
            dBFS = audio_segment.dBFS
        else:
            dBFS = -80.0
        if self.dBFS is None:
            self.dBFS = deque(80*[dBFS], 80)
        elif audio_segment.dBFS != float("-inf"):
            self.dBFS.appendleft(dBFS)

        if self.audio_segment is None:
            self.audio_segment = audio_segment
        else:
            self.audio_segment += audio_segment

        self.count += 1

        if self.count % 4 == 0:
            if self.listening:
                if len(self.audio_segment) > 2000 and hasTalked(self.dBFS, self.audio_segment):
                    text = speechtotext(self.audio_segment)
                    if len(text) < 4:
                        return
                    print(text)
                    if text in ['qalaysiz', 'yaxshimisiz']:
                        await self.send(bytes_data=yahshi)
                    elif text in ['soat', 'soat nechi bo‘ldi']:
                        await self.send(bytes_data=get_audio(get_time()))
                    elif text in ['yonim', 'jonim', 'asalim']:
                        await self.send(bytes_data=voyeeeey)
                    elif text in ['ob havo','havo','ob ha','obi havo']:
                        await self.send(bytes_data=get_audio(get_weather_json_to_word()))
                    else:
                        await self.send(bytes_data=tushunmadim)
                    await self.send(text_data=json.dumps({
                        'is_listening': False,
                    }))
                    self.listening = False
            else:
                if len(self.audio_segment) > 1000:
                    self.audio_segment = self.audio_segment[-1000:]
                if hasTalked(self.dBFS, self.audio_segment):
                    text = speechtotext(self.audio_segment)
                    print(text)
                    if text in ['oyqiz', 'oy qiz', 'voy qiz', 'oyiqiz', 'oyi qiz', 'o‘yqiz', 'boyqiz', 'boy qiz']:
                        # audio = get_audio("labbay eshitaman")
                        # await self.send(bytes_data=audio)
                        self.audio_segment = None
                        await self.send(text_data=json.dumps({
                            'is_listening': True,
                        }))
                        self.listening = True

    async def ws_data(self, message):
        await self.send(bytes_data=message['audio'])
