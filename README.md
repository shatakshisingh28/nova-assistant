# Nova: Virtual AI Assistant

A voice assistant and chatbot in one. Say (or type) a quick command like
"set a timer for 10 minutes" and it runs locally; ask anything else and it
answers through an LLM (the Claude API).

## Setup

```bash
pip install -r requirements.txt
```

**PyAudio** (microphone access) is the usual sticking point:

- Windows: `pip install PyAudio`. If that fails: `pip install pipwin` then `pipwin install pyaudio`
- macOS: `brew install portaudio` then `pip install PyAudio`
- Linux: `sudo apt install portaudio19-dev python3-pyaudio espeak` then `pip install PyAudio`

If the microphone can't be opened, Nova automatically falls back to typing.

**Chatbot brain (optional but recommended):** create an API key at
https://console.anthropic.com, then set it:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="your-key"
# Windows (PowerShell, then reopen the terminal)
setx ANTHROPIC_API_KEY "your-key"
```

Without a key, all quick commands still work; open-ended questions just
get a "brain offline" reply.

## Run

```bash
python main.py              # voice mode
python main.py --text       # type instead of speaking
python main.py --mute       # no spoken replies
python main.py --wake nova  # only react when you say "nova ..."
```

Optional environment variables: `NOVA_CITY` (default weather city),
`NOVA_MODEL` (Claude model name), `NOVA_DATA_DIR` (where notes/tasks are saved).

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
| anything else | Answered by the chatbot, with conversation memory |
| "bye" | Exit |

## Files

- `main.py`: the loop (listen, try quick commands, otherwise ask the chatbot, speak)
- `skills.py`: local commands; add your own function and list it in `handle()`
- `brain.py`: the LLM chatbot and its personality (`SYSTEM_PROMPT`)
- `speech.py`: microphone input and text-to-speech

## Ideas to extend it

- Answer questions about a CSV file (fits a data analyst portfolio nicely)
- Read and send email, or check your calendar
- A web or Tkinter front end
- Offline speech recognition with Vosk or Whisper
