"""Nova - a voice assistant + chatbot for everyday tasks.

Run:  python main.py            (voice mode)
      python main.py --text     (type instead of speak)
"""
import argparse

import skills
from brain import Brain
from speech import Listener, Speaker


def parse_args():
    p = argparse.ArgumentParser(description="Nova, your virtual AI assistant")
    p.add_argument("--text", action="store_true", help="type instead of using the microphone")
    p.add_argument("--mute", action="store_true", help="don't speak replies aloud")
    p.add_argument("--wake", default="", help="only react when this word is heard, e.g. --wake nova")
    p.add_argument("--lang", default="en-IN", help="speech recognition language (default en-IN)")
    p.add_argument("--name", default="Nova", help="assistant name")
    return p.parse_args()


def get_input(listener, wake):
    """Return the user's request as text ('' if nothing usable was heard)."""
    if listener is None:
        try:
            return input("You: ").strip()
        except EOFError:
            return "bye"
    heard = listener.listen()
    if not heard:
        return ""
    print(f"You: {heard}")
    if wake:
        if wake.lower() not in heard.lower():
            return ""
        heard = heard.lower().replace(wake.lower(), "", 1).strip(" ,.")
    return heard


def main():
    args = parse_args()
    speaker = Speaker(name=args.name, enabled=not args.mute)
    brain = Brain()

    listener = None
    if not args.text:
        try:
            listener = Listener(language=args.lang)
        except Exception as exc:  # noqa: BLE001
            print(f"[microphone unavailable: {exc}]")
            print("[falling back to typing - see README for PyAudio setup]")

    if not brain.available:
        print("[chat brain offline: set ANTHROPIC_API_KEY to enable open-ended answers]")

    speaker.say(f"Hi, I'm {args.name}. How can I help? Say help to hear what I can do.")

    while True:
        try:
            text = get_input(listener, args.wake)
            if not text:
                continue
            reply = skills.handle(text, speaker)
            if reply == skills.EXIT:
                speaker.say("Goodbye! Have a great day.")
                break
            if reply is None:
                reply = brain.ask(text)
            speaker.say(reply)
        except KeyboardInterrupt:
            print()
            speaker.say("Goodbye!")
            break


if __name__ == "__main__":
    main()
