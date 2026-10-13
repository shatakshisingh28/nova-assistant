"""Speech input (microphone -> text) and output (text -> voice)."""
import threading

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class Speaker:
    """Speaks replies aloud (offline) and always prints them too."""

    def __init__(self, name="Nova", enabled=True, rate=175):
        self.name = name
        self.rate = rate
        self.enabled = enabled and pyttsx3 is not None
        self._lock = threading.Lock()
        if enabled and pyttsx3 is None:
            print("[pyttsx3 not installed - replies will be text only]")

    def say(self, text):
        print(f"{self.name}: {text}")
        if not self.enabled:
            return
        with self._lock:
            try:
                # A fresh engine per call avoids a known runAndWait() hang on some systems.
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as exc:  # noqa: BLE001
                print(f"[voice output failed: {exc}] - switching to text only")
                self.enabled = False


class Listener:
    """Listens on the microphone and returns recognised text."""

    def __init__(self, language="en-IN"):
        if sr is None:
            raise RuntimeError("SpeechRecognition is not installed")
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        with sr.Microphone() as source:  # raises if no mic / PyAudio missing
            print("[calibrating for background noise...]")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self, timeout=8, phrase_limit=15):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            except sr.WaitTimeoutError:
                return ""
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("[speech service unreachable - check your internet]")
            return ""
