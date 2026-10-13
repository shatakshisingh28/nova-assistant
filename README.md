# Nova Desktop Starter

A purple Tkinter desktop assistant with streaming AI generation, optional Groq-first/Gemini-second fallback, SQLite chat/task/note/memory storage, push-to-talk voice, speech output, and a small allowlist of safe local commands.

## Install (Windows / PowerShell)

Use Python 3.10+ (Python 3.11 recommended). In this folder run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Add a key to `.env`. Get a Groq key from https://console.groq.com/. To enable fallback, also configure a Gemini API key from https://aistudio.google.com/. API free tiers, model availability and quotas change; check the provider console if a model fails. Keep `.env` private and never commit it.

## Run

```powershell
python app.py
```

If PyAudio installation fails, remove `PyAudio` from `requirements.txt`, reinstall, and use text input until voice is configured. Tkinter normally ships with standard Windows Python installers.

## Commands

- `help`, `time`, `date`
- `open YouTube`, `open GitHub`, `open Gmail`
- `search Python decorators`
- `calculate 45 * 12`
- `add task finish SQL practice`, `my tasks`, `done 1`
- `note project idea`, `show notes`
- `remember that I prefer Python`, `what do you remember`, `forget memories`

Anything else goes to the configured AI providers. SQLite data is stored in `~/.nova/nova.sqlite3` by default.

## Roadmap

1. Install and test desktop UI and local commands before configuring AI.
2. Add Groq key and verify streaming API access; add Gemini only as a second configured provider.
3. Add incremental token display in the UI (current version receives streamed chunks but shows the finished answer at once).
4. Improve voice with a visible listening state, cancel button and offline speech recognition if needed.
5. Add due dates and scheduled reminders to the SQLite task table.
6. Add more automation only through an explicit allowlist and confirmation dialog.
7. Add settings panel for model selection, voice rate, and data controls.
8. Package with PyInstaller only after the app is stable.

## Safety

Nova opens only allowlisted websites and does not execute arbitrary shell commands. Keep this boundary. Never let model output directly run terminal commands, delete files, or send messages without explicit user confirmation.
