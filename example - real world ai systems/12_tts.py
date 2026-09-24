"""12 - Text to speech, locally, on a CPU.

A 60 MB voice model is enough to read text aloud. No GPU, no cloud, no per-word cost.

Setup (downloads the voice, about 60 MB):
    pip install piper-tts
    python -m piper.download_voices en_US-lessac-medium

Run:  python 12_tts.py     -> writes sample.wav
"""

import wave

from piper import PiperVoice

# "Meltdown" is the GPU server (an NVIDIA H100) used as the running example in
# these demos - and a good test, because speech models stumble over names.
TEXT = (
    "Speech is just another model. The H100 server called Meltdown has eighty "
    "gigabytes of memory, and it can be split into slices."
)

voice = PiperVoice.load("en_US-lessac-medium.onnx")

with wave.open("sample.wav", "wb") as output:
    voice.synthesize_wav(TEXT, output)

print("wrote sample.wav - play it, then run 13_stt.py to turn it back into text")
