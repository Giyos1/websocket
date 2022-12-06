import torch
import struct

model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language='uz',
                                     speaker='v3_uz')

model.to(torch.device('cpu'))  # gpu or cpu


def get_audio(text):
    audio = model.apply_tts(text=text,
                           speaker='dilnavoz',
                           sample_rate=24000,
                           put_accent=True,
                           put_yo=True)

    floatlist = audio.tolist()

    return struct.pack('%sf' % len(floatlist), *floatlist)
