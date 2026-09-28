import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

from Backend.pipeline import run_generation_pipeline

def main():
    parser = argparse.ArgumentParser(description="Headless MoneyPrinter Video Generator")
    parser.add_argument("--subject", type=str, required=True, help="Topic for the video")
    parser.add_argument("--voice", type=str, default="en_us_001", help="Edge TTS voice code")
    args = parser.parse_args()

    print(f"[*] Starting video generation for subject: {args.subject}")

    data = {
        "videoSubject": args.subject,
        "voice": args.voice,
        "aiModel": "llama-3.1-8b-instant",
        "paragraphNumber": 1,
        "customPrompt": "",
        "threads": 2,
        "subtitlesPosition": "bottom",
        "textColor": "#FFFFFF",
    }

    def on_log(message: str, level: str = "info"):
        print(f"[{level.upper()}] {message}")

    output_path = run_generation_pipeline(
        data=data,
        is_cancelled=lambda: False,
        on_log=on_log,
        amount_of_stock_videos=5,
    )

    print(f"[+] Generation complete: {output_path}")

if __name__ == "__main__":
    main()
