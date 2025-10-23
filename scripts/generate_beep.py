"""Generate a short beep WAV file at 440Hz for tests."""
import math
import wave
import struct

def generate_beep(path='tests/fixtures/beep.wav', duration_s=0.5, freq=440.0, sr=44100, amp=0.5):
    n_samples = int(sr * duration_s)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sr)
        for i in range(n_samples):
            t = i / sr
            val = int(amp * 32767.0 * math.sin(2.0 * math.pi * freq * t))
            data = struct.pack('<h', val)
            wf.writeframesraw(data)
    # finalize
    with wave.open(path, 'rb') as src:
        params = src.getparams()
    # rewrite to ensure correct headers (wave module handles this automatically above)

if __name__ == '__main__':
    generate_beep()
    print('Generated tests/fixtures/beep.wav')
