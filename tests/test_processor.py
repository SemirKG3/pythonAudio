import pytest
from py_audio_tools.processor import AudioProcessor
from pathlib import Path


def test_load_missing():
    ap = AudioProcessor()
    with pytest.raises(FileNotFoundError):
        ap.load('tests/fixtures/missing.wav')


def test_trim_wave(tmp_path):
    # This is a very small smoke test that will skip if no backend is installed
    ap = AudioProcessor()
    p = Path('tests/fixtures/beep.wav')
    if not p.exists():
        pytest.skip('fixture missing')
    audio = ap.load(str(p))
    trimmed = ap.trim(audio, 0, 100)
    out = tmp_path / 't.wav'
    ap.export(trimmed, str(out))
    assert out.exists()
