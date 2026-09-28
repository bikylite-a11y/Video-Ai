import json
import os
import re
from groq import Groq

def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    return Groq(api_key=api_key)

def _model_name(ai_model: str | None) -> str:
    if not ai_model or "70b" in ai_model or "llama3.2" in ai_model:
        return "llama-3.1-8b-instant"
    return ai_model

def generate_script(
    video_subject: str,
    paragraph_number: int = 1,
    ai_model: str | None = None,
    voice: str | None = None,
    custom_prompt: str = "",
) -> str:
    prompt = f"""
Write a compelling, fast-paced narration script about:
"{video_subject}"

Requirements:
- Use approximately {paragraph_number} paragraph(s).
- Return only narration text.
- Do not include speaker labels, timestamps, scene directions, or quotation marks.
{f"Additional instructions: {custom_prompt}" if custom_prompt else ""}
""".strip()

    response = get_client().chat.completions.create(
        model=_model_name(ai_model),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return (response.choices[0].message.content or "").strip()

def get_search_terms(
    video_subject: str,
    amount: int = 5,
    script: str = "",
    ai_model: str | None = None,
) -> list[str]:
    prompt = f"""
Generate exactly {amount} relevant, visually descriptive Pexels stock-video
search terms for this topic:

{video_subject}

Script context:
{script}

Return only a valid JSON array of strings.
""".strip()

    response = get_client().chat.completions.create(
        model=_model_name(ai_model),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    raw_content = (response.choices[0].message.content or "").strip()
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
Create YouTube metadata for this short video.

Topic: {video_subject}
Script: {script}

Return only valid JSON in this format:
{{
  "title": "title",
  "description": "description",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}
""".strip()

    response = get_client().chat.completions.create(
        model=_model_name(ai_model),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    raw_content = (response.choices[0].message.content or "").strip()
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
