"""13 - Speech to text, locally, on a CPU.

Setup:  pip install faster-whisper
        (the 'tiny' model is ~75 MB and downloads on first run)

Run:  python 13_stt.py       - transcribes the sample.wav made by 12_tts.py
"""

from faster_whisper import WhisperModel

# "tiny" runs on a laptop CPU. Swap for "small" or "large-v3" on a GPU server:
# same three lines, better accuracy, more hardware.
model = WhisperModel("tiny", device="cpu", compute_type="int8")

segments, info = model.transcribe("sample.wav")

print(f"detected language: {info.language}")
for segment in segments:
    print(f"[{segment.start:5.1f}s -> {segment.end:5.1f}s] {segment.text.strip()}")

# Note what you get back: text WITH timestamps. That is what lets a product
# jump to the right moment in a recording, not just show a transcript.
