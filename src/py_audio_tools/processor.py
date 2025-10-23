"""Simple audio processing helpers."""
from pathlib import Path
from typing import Optional


def _try_import_pydub():
    try:
        from pydub import AudioSegment

        return AudioSegment
    except Exception:
        return None


def _try_import_soundfile():
    try:
        import soundfile as sf

        return sf
    except Exception:
        return None


class AudioProcessor:
    """A small helper to load, trim and export audio.

    Contract:
    - Inputs: path to audio file (wav/mp3/...), start_ms, end_ms
    - Outputs: exported file path
    - Error modes: FileNotFoundError, RuntimeError on unsupported formats
    """

    def __init__(self):
        self.AudioSegment = _try_import_pydub()
        self.soundfile = _try_import_soundfile()

    def load(self, path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        if self.AudioSegment:
            return self.AudioSegment.from_file(str(p))
        if self.soundfile:
            data, sr = self.soundfile.read(str(p))
            return (data, sr)
        raise RuntimeError("No audio backend available. Install pydub or soundfile.")

    def trim(self, audio, start_ms: Optional[int], end_ms: Optional[int]):
        """Trim audio. If using pydub, audio is AudioSegment; if soundfile, it's (data, sr)."""
        if self.AudioSegment and isinstance(audio, self.AudioSegment):
            s = start_ms or 0
            e = end_ms or len(audio)
            return audio[s:e]
        if self.soundfile and isinstance(audio, tuple):
            data, sr = audio
            s = int((start_ms or 0) / 1000.0 * sr)
            e = int((end_ms or (len(data) / sr * 1000.0)) / 1000.0 * sr)
            return (data[s:e], sr)
        raise RuntimeError("Unsupported audio object for trim")

    def export(self, audio, out_path: str, format: Optional[str] = None):
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if self.AudioSegment and isinstance(audio, self.AudioSegment):
            audio.export(str(p), format=format)
            return str(p)
        if self.soundfile and isinstance(audio, tuple):
            data, sr = audio
            fmt = format or p.suffix.lstrip('.')
            # soundfile uses subtype/dtype guesses; simple use-case write wav
            if fmt in ('wav', 'WAV'):
                self.soundfile.write(str(p), data, sr)
                return str(p)
            # fallback: try librosa + soundfile
            try:
                import soundfile as sf

                sf.write(str(p), data, sr)
                return str(p)
            except Exception as exc:
                raise RuntimeError(f"Failed to export using soundfile: {exc}")
        raise RuntimeError("No export backend available")
