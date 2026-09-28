@'
import os
import json
import re
from groq import Groq

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    return Groq(api_key=api_key)

def generate_script(video_subject: str, language: str = "en", model: str = "llama-3.3-70b-versatile") -> str:
    prompt = (
        f"You are a professional YouTube Shorts and TikTok creator.\n"
        f"Write a compelling, engaging, and fast-paced video script about: '{video_subject}'.\n"
        f"Keep the script concise (around 120-150 words) suitable for a 45-60 second video.\n"
        f"Return ONLY the narration text. Do not include speaker tags, timestamps, scene directions, or quotes."
    )
    
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def get_search_terms(video_subject: str, amount: int = 5, model: str = "llama-3.3-70b-versatile") -> list[str]:
    prompt = (
        f"Generate {amount} relevant, visually descriptive search terms for stock video clips on Pexels "
        f"matching the topic: '{video_subject}'.\n"
        f"Return ONLY a valid JSON array of strings, for example: [\"car restoration\", \"mechanic garage\", \"classic sports car\"]."
    )
    
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    raw_content = response.choices[0].message.content.strip()
    match = re.search(r'\[.*\]', raw_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return [video_subject]
'@ | Set-Content -Path "Backend\gpt.py" -Encoding UTF8