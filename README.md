# Nova: Virtual AI Assistant

A voice assistant and chatbot in one, built in Python. Say (or type) a quick
command like "set a timer for 10 minutes" and it runs locally. Ask anything
else and it answers through an LLM running on [Groq](https://groq.com).

## Features

- Voice input (microphone) and spoken replies, or plain typing with `--text`
- Quick local commands: time and date, weather, web search, YouTube, Wikipedia,
  notes, to-do list, timers, reminders, calculator
- Chatbot for everything else, with memory of the last few turns
- Falls back to typing automatically if the microphone can't be opened

## Requirements

- Python 3.9 or newer
- A microphone (only for voice mode)
- A free Groq API key (only for the chatbot; quick commands work without it)

## Setup

### 1. Get the files

Extract the zip, then open a terminal **inside** the extracted `nova-assistant`
folder. On Windows, open the folder in File Explorer, click the address bar,
type `cmd` and press Enter. Run `dir` to confirm you can see `main.py` and
`requirements.txt`.

### 2. Install the packages

```bash
python -m pip install -r requirements.txt
```

PyAudio (microphone access) is the usual sticking point:

| System | Fix |
|---|---|
| Windows | `python -m pip install pipwin`, then `python -m pipwin install pyaudio` |
| macOS | `brew install portaudio`, then `pip install PyAudio` |
| Linux | `sudo apt install portaudio19-dev python3-pyaudio espeak`, then `pip install PyAudio` |

If PyAudio won't install, install the rest with
`python -m pip install SpeechRecognition pyttsx3 groq requests` and run Nova
in `--text` mode.

### 3. Add your Groq API key

1. Create a key at https://console.groq.com/keys
2. Set it as an environment variable:

```bash
# Windows (Command Prompt). Close and reopen the terminal afterwards.
setx GROQ_API_KEY "your-key-here"

# macOS / Linux
export GROQ_API_KEY="your-key-here"
```

Keep the key private. Never paste it into the code or upload it to GitHub.

## Run

```bash
python main.py              # voice mode
python main.py --text       # type instead of speaking (good for a first test)
python main.py --mute       # no spoken replies
python main.py --wake nova  # only react when you say "nova ..."
python main.py --lang hi-IN # speech recognition language (default en-IN)
```

## What you can say

| Say | What happens |
|---|---|
| "what time is it" / "today's date" | Tells you |
| "open youtube" / "open github" | Opens the site |
| "search python decorators" | Google search |
| "play lo-fi music" | YouTube search |
| "wikipedia Alan Turing" | Two-sentence summary |
| "weather in Mumbai" | Current weather |
| "note buy a laptop stand" / "show my notes" | Saves / reads notes |
| "add task finish SQL practice" / "my tasks" / "done 1" | To-do list |
| "set a timer for 5 minutes" | Spoken alert when done |
| "remind me in 30 minutes to drink water" | Spoken reminder |
| "calculate 45 times 12" | Maths |
| "help" | Lists what Nova can do |
| anything else | Answered by the chatbot |
| "bye" | Exit |

## Settings (optional environment variables)

| Variable | Purpose | Default |
|---|---|---|
| `GROQ_API_KEY` | Enables the chatbot | none |
| `GROQ_MODEL` | Which Groq model to use | `llama-3.3-70b-versatile` |
| `NOVA_CITY` | Default city for weather | `New Delhi` |
| `NOVA_DATA_DIR` | Where notes and tasks are saved | `~/.nova` |

Groq retires and adds models over time. If the chatbot starts failing with a
"model not found" style error, pick a current model from
https://console.groq.com/docs/models and set `GROQ_MODEL` to its name.

## Project files

- `main.py`: the main loop (listen, try quick commands, otherwise ask the chatbot, speak)
- `skills.py`: local commands; add your own function and list it in `handle()`
- `brain.py`: the Groq chatbot and its personality (`SYSTEM_PROMPT`)
- `speech.py`: microphone input and text-to-speech
- `requirements.txt`: Python packages

## Troubleshooting

| Problem | Fix |
|---|---|
| `Could not open requirements file` | You're in the wrong folder. `cd` into the folder that contains `requirements.txt` |
| PyAudio fails to install | See the table in Setup, or use `--text` mode |
| "microphone unavailable" | Check the mic is plugged in and allowed in system privacy settings |
| "chat brain offline" | `GROQ_API_KEY` isn't set. Set it, then reopen the terminal |
| "couldn't reach the AI service" | Check internet, API key and the `GROQ_MODEL` name |
| Speech recognition never hears you | Speak after "calibrating" finishes; reduce background noise |

Voice recognition uses Google's free web speech service, so it needs an
internet connection.

## Ideas to extend it

- Answer questions about a CSV file (fits a data analyst portfolio nicely)
- Read and send email, or check your calendar
- A web or Tkinter front end
- Offline or Groq-hosted Whisper for speech recognition
