import os
import sys
import inspect
import argparse
from dotenv import load_dotenv

load_dotenv()

from Backend.pipeline import generate_video

def main():
    parser = argparse.ArgumentParser(description="Headless MoneyPrinter Video Generator")
    parser.add_argument("--subject", type=str, required=True, help="Topic for the video")
    parser.add_argument("--voice", type=str, default="en_us_001", help="Edge TTS voice code")
    args = parser.parse_args()

    print(f"[*] Starting video generation for subject: {args.subject}")

    # Inspect generate_video parameters to support both 'topic' and 'video_subject'
    sig = inspect.signature(generate_video)
    params = sig.parameters

    kwargs = {}
    if "topic" in params:
        kwargs["topic"] = args.subject
    elif "video_subject" in params:
        kwargs["video_subject"] = args.subject
    else:
        # Fallback to first positional argument
        kwargs[list(params.keys())[0]] = args.subject

    if "voice" in params:
        kwargs["voice"] = args.voice
    if "ai_model" in params:
        kwargs["ai_model"] = "llama-3.3-70b-versatile"

    output_path = generate_video(**kwargs)
    print(f"[+] Generation complete: {output_path}")

if __name__ == "__main__":
    main()
