import os
import re

try:
    import ollama
except ImportError:
    ollama = None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None


load_dotenv()

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = """
You are a fantasy dungeon master.
Keep responses under 200 words.
Always give exactly 3 choices.
Label choices only as A, B, and C.
Never ask open-ended questions.
Continue only from the chosen option.
Do not add choices labeled D or anything beyond A, B, and C.
""".strip()


def generate_story(prompt: str) -> str:
    if ollama is None:
        return fallback_story(
            RuntimeError("The ollama Python package is not installed. Run python -m pip install -r requirements.txt.")
        )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return normalize_choice_labels(response["message"]["content"].strip())
    except Exception as error:
        return fallback_story(error)


def normalize_choice_labels(story: str) -> str:
    story = re.sub(r"(?m)^(\s*)A[\):\-]\s*", r"\1A. ", story)
    story = re.sub(r"(?m)^(\s*)B[\):\-]\s*", r"\1B. ", story)
    story = re.sub(r"(?m)^(\s*)C[\):\-]\s*", r"\1C. ", story)
    return story


def fallback_story(error: Exception) -> str:
    return (
        "The lantern light flickers as the dungeon waits in uneasy silence. "
        "The local AI model could not answer, so the quest pauses at the edge "
        "of the next chamber.\n\n"
        "A. Check that Ollama is running and try again.\n"
        "B. Start a new path through the torchlit hall.\n"
        "C. Save your progress before continuing.\n\n"
        f"AI service note: {error}"
    )
