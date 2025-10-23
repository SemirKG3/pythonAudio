from py_audio_tools.processor import AudioProcessor


def demo():
    ap = AudioProcessor()
    audio = ap.load('tests/fixtures/beep.wav')
    trimmed = ap.trim(audio, 0, 500)
    ap.export(trimmed, 'out/beep_trimmed.wav')


if __name__ == '__main__':
    demo()
