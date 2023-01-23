import json
import numpy
import torch
from functools import reduce
from pydub import AudioSegment
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from models import get_audio
from transformers import Wav2Vec2Processor, AutoModelForCTC
from .utils import split_on_silence, rechunk

processor = Wav2Vec2Processor.from_pretrained("language")
model = AutoModelForCTC.from_pretrained("language")


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
        fp_arr = numpy.array(sound.get_array_of_samples()).T.astype(numpy.float32)
        model_input = processor(fp_arr, sampling_rate=16000, return_tensors="pt").input_values
        logits = model(model_input).logits
        bashorat = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(bashorat)
        text = transcription[0] if len(transcription) > 0 else None

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
