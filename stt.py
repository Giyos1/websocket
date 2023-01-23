import numpy
import torch
from transformers import Wav2Vec2Processor, AutoModelForCTC

processor = Wav2Vec2Processor.from_pretrained("language")
model = AutoModelForCTC.from_pretrained("language")

def speechtotext(audio_segment):
    fp_arr = numpy.array(audio_segment.get_array_of_samples()).T.astype(numpy.float32)
    model_input = processor(fp_arr, sampling_rate=16000, return_tensors="pt").input_values
    logits = model(model_input).logits
    bashorat = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(bashorat)
    text = transcription[0] if len(transcription) > 0 else None
    return text