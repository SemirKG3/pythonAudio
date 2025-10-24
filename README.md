# py-audio-tools

Small Python utilities for editing audio files (trim, convert) with a simple CLI.

Requirements
- Python 3.8+
- ffmpeg (required by pydub for many formats)

Quickstart

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Trim an audio file with the CLI (after installing the package or running `python -m src.py_audio_tools.cli`):

```powershell
python -m py_audio_tools.cli trim input.wav --start-ms 1000 --end-ms 5000 -o out.wav
```

Examples

See `examples/trim_audio.py` for a programmatic usage example.

GitHub

To push this project to GitHub:

1. Create a new repository on GitHub.
2. In this folder run:

```powershell
# Initialize repository and commit
git init
git add .
git commit -m "Initial scaffold"

# Add remote and push (using your repository)
git remote add origin https://github.com/SemirKG3/pythonAudio.git
git branch -M main
git push -u origin main
```

Notes

- pydub depends on ffmpeg for many file formats. Install ffmpeg on your system and ensure it's on PATH.
- If pydub is not available or can't handle a format, the code falls back to soundfile/librosa where possible.
