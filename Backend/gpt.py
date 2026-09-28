import json
import os
import re
import time
from groq import Groq, RateLimitError

def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    return Groq(api_key=api_key)

def _get_active_model() -> str:
    client = get_client()
    try:
        models = client.models.list()
        available_ids = [m.id for m in models.data]
        print(f"[*] Available Groq models: {available_ids}")

        preferred = [
            "openai/gpt-oss-20b",
            "allam-2-7b",
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
        ]
        for candidate in preferred:
            if candidate in available_ids:
                return candidate

        text_models = [m for m in available_ids if "whisper" not in m and "guard" not in m]
        if text_models:
            return text_models[0]
    except Exception as e:
        print(f"[!] Warning checking models: {e}")

    return "openai/gpt-oss-20b"

def _call_groq(model: str, messages: list[dict], max_tokens: int = 700) -> str:
    client = get_client()
    for attempt in range(3):
        try:
            extra_params = {}
            if "gpt-oss" in model:
                extra_params["reasoning_effort"] = "low"

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=max_tokens,
                **extra_params
            )
            msg = response.choices[0].message
            content = msg.content or ""
            # If reasoning model placed text in reasoning attribute, use it as fallback
            if not content.strip():
                content = getattr(msg, "reasoning", "") or getattr(msg, "reasoning_content", "") or ""
            return content.strip()
        except RateLimitError as e:
            time.sleep(3 * (attempt + 1))
            if attempt == 2:
                print(f"[!] Rate limit exceeded: {e}")
                return ""
        except Exception as e:
            print(f"[!] Groq API error: {e}")
            return ""
    return ""

def generate_script(
    video_subject: str,
    paragraph_number: int = 1,
    ai_model: str | None = None,
    voice: str | None = None,
    custom_prompt: str = "",
) -> str:
    prompt = f"Write a fast-paced, punchy, 100-word educational video script about '{video_subject}'. Do not include quotes, timestamps, or speaker headers. Narration only."

    model = _get_active_model()
    print(f"[*] Calling Groq with model: {model}")
    text = _call_groq(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=700)

    # Clean and strip any internal reasoning tags if present
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Guaranteed fallback to prevent pipeline failure
    if not text:
        print("[!] Using fallback script generation.")
        text = (
            f"Did you know this fascinating detail about {video_subject}? "
            f"Throughout history, {video_subject} has transformed our understanding of the world. "
            f"From incredible discoveries to unexpected facts, researchers continue to find mind-bending elements that challenge everything we thought we knew. "
            f"Next time you explore {video_subject}, remember just how much remains uncovered. Follow for more amazing facts!"
        )
    return text

def get_search_terms(
    video_subject: str,
    amount: int = 5,
    script: str = "",
    ai_model: str | None = None,
) -> list[str]:
    prompt = f"List {amount} concise Pexels stock video search keywords for the topic: '{video_subject}'. Return JSON array of strings only, like [\"keyword1\", \"keyword2\"]."
    model = _get_active_model()
    time.sleep(1)
    raw = _call_groq(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=250)

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            terms = json.loads(match.group(0))
            if isinstance(terms, list) and len(terms) > 0:
                return [str(t) for t in terms[:amount]]
        except Exception:
            pass

    # Clean keyword fallback based on subject
    words = [w for w in re.sub(r"[^\w\s]", "", video_subject).split() if len(w) > 2]
    return words[:amount] if words else [video_subject, "cinematic", "technology", "nature", "exploration"]

def generate_metadata(
    video_subject: str,
    script: str,
    ai_model: str | None = None,
) -> tuple[str, str, list[str]]:
    title = f"{video_subject.title()} #Shorts"
    description = f"{script}\n\n#shorts #facts #{video_subject.replace(' ', '')}"
    keywords = [video_subject, "shorts", "viral", "facts"]
    return (title, description, keywords)
