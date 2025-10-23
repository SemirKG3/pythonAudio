Developer setup

1. Create virtualenv and activate (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run tests:

```powershell
pytest -q
```

3. Run example:

```powershell
python examples\trim_audio.py
```
