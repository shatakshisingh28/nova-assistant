"""Quick local commands. Each returns a reply string, or None if it doesn't apply."""
import ast
import datetime as dt
import json
import operator
import os
import re
import threading
import urllib.parse
import webbrowser
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

DATA_DIR = Path(os.getenv("NOVA_DATA_DIR", Path.home() / ".nova"))
NOTES_FILE = DATA_DIR / "notes.txt"
TASKS_FILE = DATA_DIR / "tasks.json"
DEFAULT_CITY = os.getenv("NOVA_CITY", "New Delhi")

EXIT = "__EXIT__"

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "leetcode": "https://leetcode.com",
    "linkedin": "https://www.linkedin.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "kaggle": "https://www.kaggle.com",
    "maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "wikipedia": "https://www.wikipedia.org",
}


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _grp(m, i, raw, text):
    """Group i of a match made on lower-cased text, but in the user's original case."""
    if raw and len(raw) == len(text):
        return raw[m.start(i):m.end(i)].strip()
    return m.group(i).strip()


# ---------------------------------------------------------------- time & date
def tell_time(_text):
    return "It's " + dt.datetime.now().strftime("%I:%M %p").lstrip("0") + "."


def tell_date(_text):
    return "Today is " + dt.datetime.now().strftime("%A, %d %B %Y") + "."


# ---------------------------------------------------------------- web
def open_site(text):
    m = re.search(r"\bopen\s+(.+)", text)
    if not m:
        return None
    target = m.group(1).strip(" .").removeprefix("the ").strip()
    if target in SITES:
        webbrowser.open(SITES[target])
        return f"Opening {target}."
    if re.fullmatch(r"[a-z0-9-]+(\.[a-z]{2,})+", target):  # looks like a domain
        webbrowser.open("https://" + target)
        return f"Opening {target}."
    if re.fullmatch(r"[a-z0-9-]+", target):  # single word -> guess .com
        webbrowser.open(f"https://www.{target}.com")
        return f"Opening {target}.com."
    return None


def web_search(text):
    m = re.match(r"(?:google|search(?: for)?|search the web for)\s+(.+)", text)
    if not m:
        return None
    query = m.group(1).strip()
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
    return f"Searching Google for {query}."


def play_youtube(text):
    m = re.match(r"(?:play|youtube)\s+(.+?)(?:\s+on youtube)?$", text)
    if not m:
        return None
    query = m.group(1).strip()
    webbrowser.open(
        "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    )
    return f"Searching YouTube for {query}."


def wikipedia(text):
    m = re.match(r"(?:wikipedia|wiki)\s+(?:for\s+|about\s+)?(.+)", text)
    if not m:
        return None
    if requests is None:
        return "The requests package is needed for Wikipedia lookups."
    topic = m.group(1).strip()
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(
            topic.replace(" ", "_")
        )
        r = requests.get(url, timeout=8, headers={"User-Agent": "NovaAssistant/1.0"})
        if r.status_code == 404:
            return f"I couldn't find a Wikipedia page for {topic}."
        r.raise_for_status()
        extract = r.json().get("extract", "")
        sentences = re.split(r"(?<=[.!?])\s+", extract)
        return " ".join(sentences[:2]) or f"No summary available for {topic}."
    except Exception:  # noqa: BLE001
        return "I couldn't reach Wikipedia right now."


def weather(text):
    if "weather" not in text and "temperature" not in text:
        return None
    if requests is None:
        return "The requests package is needed for weather."
    m = re.search(r"\b(?:in|for|at)\s+([a-z .]+?)(?:\s+(?:today|now|tomorrow))?$", text)
    city = m.group(1).strip() if m else DEFAULT_CITY
    try:
        r = requests.get(
            "https://wttr.in/" + urllib.parse.quote(city),
            params={"format": "%C, %t, feels like %f, humidity %h"},
            timeout=8,
            headers={"User-Agent": "curl/8.0"},
        )
        r.raise_for_status()
        return f"Weather in {city.title()}: {r.text.strip()}."
    except Exception:  # noqa: BLE001
        return "I couldn't fetch the weather right now."


# ---------------------------------------------------------------- notes
def notes(text, raw=None):
    if re.search(r"\b(show|read|what are|list)\b.*\bnotes?\b", text) or text in (
        "my notes",
        "notes",
    ):
        if not NOTES_FILE.exists() or not NOTES_FILE.read_text().strip():
            return "You have no notes yet."
        lines = NOTES_FILE.read_text().strip().splitlines()[-5:]
        return "Your latest notes: " + " | ".join(lines)
    if re.search(r"\b(clear|delete)\b.*\bnotes?\b", text):
        if NOTES_FILE.exists():
            NOTES_FILE.unlink()
        return "All notes cleared."
    m = re.match(r"(?:take a note|make a note|note down|note|remember that)[:,]?\s+(.+)", text)
    if m:
        _ensure_dir()
        stamp = dt.datetime.now().strftime("%d %b %H:%M")
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {_grp(m, 1, raw, text)}\n")
        return "Noted."
    return None


# ---------------------------------------------------------------- to-do list
def _load_tasks():
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_tasks(tasks):
    _ensure_dir()
    TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def tasks(text, raw=None):
    m = re.match(r"(?:add task|add a task|add to my list|add to do|add todo)[:,]?\s+(.+)", text)
    if m:
        items = _load_tasks()
        task = _grp(m, 1, raw, text)
        items.append({"text": task, "done": False})
        _save_tasks(items)
        return f"Added task {len(items)}: {task}."

    if re.search(r"\b(my tasks|show tasks|list tasks|my to.?do|what.s on my list)\b", text):
        items = _load_tasks()
        pending = [(i, t) for i, t in enumerate(items, 1) if not t["done"]]
        if not pending:
            return "Your task list is empty."
        return "Your tasks: " + "; ".join(f"{i}. {t['text']}" for i, t in pending)

    m = re.match(r"(?:done|complete|finish(?:ed)?|mark)\s+(?:task\s+)?(?:number\s+)?(\d+)(?:\s+(?:as\s+)?done)?$", text)
    if m:
        items = _load_tasks()
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(items):
            items[idx]["done"] = True
            _save_tasks(items)
            return f"Marked task {idx + 1} as done."
        return "I couldn't find that task number."

    if re.search(r"\b(clear|delete)\b.*\btasks?\b", text):
        _save_tasks([])
        return "Task list cleared."
    return None


# ---------------------------------------------------------------- timers & reminders
_UNITS = {"second": 1, "sec": 1, "minute": 60, "min": 60, "hour": 3600, "hr": 3600}


def _parse_duration(text):
    m = re.search(r"(\d+)\s*(second|sec|minute|min|hour|hr)s?\b", text)
    if not m:
        return None, None
    return int(m.group(1)) * _UNITS[m.group(2)], m


def timers(text, speaker=None, raw=None):
    remind = re.match(r"remind me (?:in|after)\s+(.+?)\s+(?:to|about)\s+(.+)", text)
    if remind:
        seconds, _ = _parse_duration(remind.group(1))
        if seconds:
            what = _grp(remind, 2, raw, text)
            _start_timer(seconds, f"Reminder: {what}", speaker)
            return f"Okay, I'll remind you to {what} in {_human(seconds)}."

    if re.search(r"\b(set|start)\b.*\btimer\b", text) or text.startswith("timer"):
        seconds, _ = _parse_duration(text)
        if seconds:
            _start_timer(seconds, "Time's up! Your timer is done.", speaker)
            return f"Timer set for {_human(seconds)}."
        return "For how long? Try 'set a timer for 5 minutes'."
    return None


def _human(seconds):
    if seconds % 3600 == 0:
        n, unit = seconds // 3600, "hour"
    elif seconds % 60 == 0:
        n, unit = seconds // 60, "minute"
    else:
        n, unit = seconds, "second"
    return f"{n} {unit}{'' if n == 1 else 's'}"


def _start_timer(seconds, message, speaker):
    def fire():
        if speaker:
            speaker.say(message)
        else:
            print(message)

    t = threading.Timer(seconds, fire)
    t.daemon = True
    t.start()


# ---------------------------------------------------------------- calculator
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def calculate(text):
    m = re.match(r"(?:calculate|compute|what is|what's|whats|solve)\s+(.+)", text)
    if not m:
        return None
    expr = m.group(1).rstrip("?. ")
    for word, sym in [
        ("multiplied by", "*"), ("divided by", "/"), ("to the power of", "**"),
        ("plus", "+"), ("minus", "-"), ("times", "*"), ("into", "*"),
        ("over", "/"), ("mod", "%"), ("x", "*"), ("^", "**"),
    ]:
        expr = re.sub(rf"(?<=[\d\s)]){re.escape(word)}(?=[\d\s(])", f" {sym} ", expr) \
            if word.isalpha() else expr.replace(word, f" {sym} ")
    if not re.fullmatch(r"[\d\s+\-*/().%]+", expr) or not re.search(r"\d", expr):
        return None  # not arithmetic -> let the chatbot handle it
    try:
        value = _eval(ast.parse(expr.strip(), mode="eval"))
    except ZeroDivisionError:
        return "That's a division by zero."
    except Exception:  # noqa: BLE001
        return None
    if isinstance(value, float):
        value = round(value, 6)
        if value == int(value):
            value = int(value)
    return f"The answer is {value}."


# ---------------------------------------------------------------- help & exit
def help_text(text):
    if text in ("help", "what can you do", "commands", "what can you do?"):
        return (
            "I can tell the time and date, open websites, search Google or YouTube, "
            "look up Wikipedia, check the weather, take notes, manage a to-do list, "
            "set timers and reminders, and do maths. For anything else, just ask "
            "me and I'll answer like a chatbot."
        )
    return None


def is_exit(text):
    return text in {"exit", "quit", "bye", "goodbye", "stop", "good night", "see you"} or bool(
        re.match(r"(?:bye|goodbye|exit|quit)\b", text)
    )


# ---------------------------------------------------------------- dispatcher
def handle(text, speaker=None):
    """Return a reply for a local command, EXIT to quit, or None to use the chatbot."""
    raw = text.strip().rstrip("?!.")
    text = raw.lower()
    if not text:
        return None
    if is_exit(text):
        return EXIT

    for fn in (help_text, tell_date, tell_time):
        if fn is help_text and (r := fn(text)):
            return r
    if re.search(r"\bwhat(?:'s| is)? the time\b|^time$|\bcurrent time\b|\bwhat time is it\b", text):
        return tell_time(text)
    if re.search(r"\b(today's date|the date|what day is it|what is today|current date)\b|^date$", text):
        return tell_date(text)

    for fn in (timers, notes, tasks, weather, wikipedia, open_site, web_search, play_youtube, calculate):
        if fn is timers:
            reply = fn(text, speaker, raw)
        elif fn in (notes, tasks):
            reply = fn(text, raw)
        else:
            reply = fn(text)
        if reply:
            return reply
    return None
