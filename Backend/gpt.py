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
        print(f"[*] Available Groq models on this account: {available_ids}")

        preferred = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ]
        for candidate in preferred:
            if candidate in available_ids:
                return candidate

        text_models = [mid for mid in available_ids if "whisper" not in mid and "guard" not in mid]
        if text_models:
            return text_models[0]
    except Exception as e:
        print(f"[!] Warning checking models: {e}")

    return "qwen/qwen3.8-27b"

def _call_groq_with_retry(model: str, messages: list[dict], temperature: float, max_tokens: int = 350) -> str:
    client = get_client()
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
            )
            return (response.choices[0].message.content or "").strip()
        except RateLimitError as e:
            wait_time = (attempt + 1) * 3
            print(f"[!] Rate limited on {model}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            if attempt == 3:
                raise e

def generate_script(
    video_subject: str,
    paragraph_number: int = 1,
    ai_model: str | None = None,
    voice: str | None = None,
    custom_prompt: str = "",
) -> str:
    prompt = f"""
Write a short, punchy narration script about:
"{video_subject}"

Requirements:
- Exactly 1 paragraph, about 90 to 120 words.
- Return ONLY narration text.
- Do not include speaker labels, timestamps, scene directions, or quotation marks.
{f"Additional instructions: {custom_prompt}" if custom_prompt else ""}
""".strip()

    model = _get_active_model()
    print(f"[*] Using Groq model: {model}")
    return _call_groq_with_retry(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )

def get_search_terms(
    video_subject: str,
    amount: int = 5,
    script: str = "",
    ai_model: str | None = None,
) -> list[str]:
    prompt = f"""
Generate {amount} concise Pexels stock video search terms for:
"{video_subject}"

Return ONLY a valid JSON array of short strings, e.g. ["space nebula", "telescope", "astronaut"].
""".strip()

    model = _get_active_model()
    time.sleep(1)
    raw_content = _call_groq_with_retry(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=150
    )

    match = re.search(r"\[.*\]", raw_content, re.DOTALL)
    if match:
        try:
            terms = json.loads(match.group(0))
            if isinstance(terms, list):
                return [str(term) for term in terms[:amount]]
        except json.JSONDecodeError:
            pass

    return [video_subject]

def generate_metadata(
    video_subject: str,
    script: str,
    ai_model: str | None = None,
) -> tuple[str, str, list[str]]:
    prompt = f"""
Create YouTube Shorts metadata for:
Topic: {video_subject}
Script: {script[:200]}

Return only valid JSON in this format:
{{
  "title": "title",
  "description": "description",
  "keywords": ["tag1", "tag2"]
}}
""".strip()

    model = _get_active_model()
    time.sleep(1)
    raw_content = _call_groq_with_retry(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=200
    )

    match = re.search(r"\{.*\}", raw_content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return (
                str(data.get("title", video_subject)),
                str(data.get("description", script)),
                [str(item) for item in data.get("keywords", [])],
            )
        except json.JSONDecodeError:
            pass

    return (
        video_subject,
        script,
        [video_subject, "shorts", "facts"],
    )
