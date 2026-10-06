import json
import importlib
import os
import re
import webbrowser
from pathlib import Path
from typing import Any, cast

try:
    pyaudio: Any = importlib.import_module("pyaudio")
except Exception:  # pragma: no cover - optional dependency for voice input
    pyaudio = None

try:
    pyttsx3: Any = importlib.import_module("pyttsx3")
except Exception:  # pragma: no cover - optional dependency for speech output
    pyttsx3 = None

try:
    requests: Any = importlib.import_module("requests")
except Exception:  # pragma: no cover - optional dependency for dictionary API
    requests = None

try:
    vosk_module: Any = importlib.import_module("vosk")
    KaldiRecognizer = vosk_module.KaldiRecognizer
    Model = vosk_module.Model
except Exception:  # pragma: no cover - optional dependency for voice input
    KaldiRecognizer = None
    Model = None


API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
DEFAULT_SAMPLE_RATE = 16000

SAVED_WORDS_FILE = Path(__file__).resolve().with_name("dictionary_words.json")
FILLER_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "could",
    "do",
    "for",
    "hey",
    "i",
    "in",
    "is",
    "it",
    "me",
    "please",
    "show",
    "say",
    "search",
    "the",
    "to",
    "uh",
    "um",
    "want",
    "would",
    "you",
}
COMMAND_WORDS = {
    "exit",
    "quit",
    "bye",
    "meaning",
    "definition",
    "definitions",
    "example",
    "examples",
    "link",
    "save",
    "help",
    "commands",
    "find",
}


def init_tts():
    if pyttsx3 is None:
        return None

    engine = pyttsx3.init()
    engine.setProperty("rate", 180)

    voices = engine.getProperty("voices") or []
    english_candidates = []
    for voice in voices:
        voice_text = " ".join(
            [
                str(getattr(voice, "name", "")),
                str(getattr(voice, "id", "")),
                " ".join(map(str, getattr(voice, "languages", []))),
            ]
        ).lower()
        if "ru" in voice_text or "russian" in voice_text:
            continue
        if "english" in voice_text or re.search(r"\ben[-_]", voice_text):
            english_candidates.append(voice)

    if english_candidates:
        engine.setProperty("voice", english_candidates[0].id)
    elif voices:
        engine.setProperty("voice", voices[0].id)

    return engine

def speak(text: str) -> None:
    print(f"Assistant: {text}")
    engine = init_tts()
    if engine is None:
        return

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS error: {e}")
    finally:
        try:
            engine.stop()
        except Exception:
            pass


def normalize_text(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    tokens = [token for token in cleaned.split() if token]
    return [token for token in tokens if token not in FILLER_WORDS]


def contains_word(tokens: list[str], word: str) -> bool:
    return word in tokens


def extract_find_target(command: str) -> str:
    tokens = normalize_text(command)
    if "find" not in tokens:
        return ""

    index = tokens.index("find") + 1
    while index < len(tokens) and tokens[index] in COMMAND_WORDS:
        index += 1

    if index >= len(tokens):
        return ""

    return tokens[index]


def init_vosk(model_path: str = MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model not found: '{model_path}'")
    model_cls = cast(Any, Model)
    rec_cls = cast(Any, KaldiRecognizer)
    if model_cls is None or rec_cls is None:
        raise RuntimeError("Vosk is not installed")
    model = model_cls(model_path)
    return rec_cls(model, DEFAULT_SAMPLE_RATE)


def listen(rec: KaldiRecognizer) -> str:
    recognizer = cast(Any, rec)
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=DEFAULT_SAMPLE_RATE,
        input=True,
        frames_per_buffer=8000,
    )
    print("Listening...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()
                if text:
                    print(f"You said: {text}")
                return text
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def fetch_word(word: str) -> dict | None:
    try:
        resp = requests.get(f"{API_URL}/{word}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
        raise ValueError("Unexpected dictionary response format")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            speak(f"The word '{word}' was not found in the dictionary.")
        else:
            speak(f"Dictionary request failed: {e}")
        return None
    except requests.RequestException as e:
        speak(f"Dictionary request failed: {e}")
        return None
    except ValueError as e:
        speak(f"Could not process the dictionary response: {e}")
        return None


def extract_definitions(entry: dict) -> list[dict[str, str]]:
    definitions: list[dict[str, str]] = []
    for meaning in entry.get("meanings", []):
        if not isinstance(meaning, dict):
            continue
        part_of_speech = str(meaning.get("partOfSpeech", "")).strip()
        for definition in meaning.get("definitions", []):
            if not isinstance(definition, dict):
                continue
            text = str(definition.get("definition", "")).strip()
            if text:
                definitions.append(
                    {
                        "part_of_speech": part_of_speech,
                        "definition": text,
                        "example": str(definition.get("example", "")).strip(),
                    }
                )
    return definitions


def save_word(word: str, entry: dict) -> None:
    try:
        items = []
        if SAVED_WORDS_FILE.exists():
            raw = json.loads(SAVED_WORDS_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                items = [item for item in raw if isinstance(item, dict)]
        items = [item for item in items if item.get("word") != word]
        items.append({"word": word, "entry": entry})
        SAVED_WORDS_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        speak(f"Saved '{word}' to {SAVED_WORDS_FILE.name}.")
    except Exception as e:
        speak(f"Could not save the word: {e}")


def cmd_find(command: str, state: dict) -> None:
    word = extract_find_target(command)
    if not word:
        speak("Please say 'find' followed by an English word.")
        return

    entry = fetch_word(word)
    if not entry:
        state["current_word"] = None
        state["current_entry"] = None
        state["current_definitions"] = []
        return

    state["current_word"] = word
    state["current_entry"] = entry
    state["current_definitions"] = extract_definitions(entry)

    if state["current_definitions"]:
        speak(f"Found '{word}'. You can ask for meaning, example, link, or save it.")
    else:
        speak(f"Found '{word}', but no definitions were available. You can still use link or save.")


def cmd_meaning(state: dict) -> None:
    if not state["current_word"] or not state["current_entry"]:
        speak("Please use 'find' first.")
        return
    if not state["current_definitions"]:
        speak("No definitions were found for this word.")
        return

    definition = state["current_definitions"][0]
    pos = definition.get("part_of_speech", "").strip()
    meaning = definition.get("definition", "").strip()
    speak(f"{state['current_word']}, {pos}: {meaning}" if pos else f"{state['current_word']}: {meaning}")


def cmd_example(state: dict) -> None:
    if not state["current_word"] or not state["current_entry"]:
        speak("Please use 'find' first.")
        return

    for definition in state["current_definitions"]:
        example = definition.get("example", "").strip()
        if example:
            speak(f"Example: {example}")
            return

    speak("No example was found for this word.")


def cmd_link(state: dict) -> None:
    if not state["current_word"] or not state["current_entry"]:
        speak("Please use 'find' first.")
        return

    urls = state["current_entry"].get("sourceUrls", [])
    if not isinstance(urls, list) or not urls:
        speak("No source link is available for this word.")
        return

    try:
        webbrowser.open(str(urls[0]))
        speak(f"Opening the source link for {state['current_word']}.")
    except Exception as e:
        speak(f"Could not open the link: {e}")


def cmd_save(state: dict) -> None:
    if not state["current_word"] or not state["current_entry"]:
        speak("Please use 'find' first.")
        return
    save_word(state["current_word"], state["current_entry"])


def cmd_help() -> None:
    speak(
        "Available commands are: find followed by a word, meaning, example, link, save, help, and exit."
    )


ROUTES = [
    (("meaning",), cmd_meaning),
    (("example",), cmd_example),
    (("link",), cmd_link),
    (("save",), cmd_save),
    (("help", "commands"), lambda state: cmd_help()),
]


def process(command: str, state: dict) -> bool:
    tokens = normalize_text(command)
    if not tokens:
        return True

    if any(contains_word(tokens, w) for w in ("exit", "quit", "bye")):
        speak("Goodbye!")
        return False

    if contains_word(tokens, "find"):
        cmd_find(command, state)
        return True

    for keywords, handler in ROUTES:
        if any(contains_word(tokens, k) for k in keywords):
            handler(state)
            return True

    speak("Command not recognized. Say 'help' for available commands.")
    return True


def main() -> None:
    rec = init_vosk()
    state = {"current_word": None, "current_entry": None, "current_definitions": []}
    speak("Hello! I am an English dictionary assistant. Say 'find' followed by a word to search it.")

    while True:
        command = listen(rec)
        if command and not process(command, state):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAssistant stopped by user.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Critical error: {e}")
