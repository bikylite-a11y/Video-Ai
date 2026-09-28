import os
import sys
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
    
    # Generate video
    output_path = generate_video(
        video_subject=args.subject,
        voice=args.voice,
        ai_model="llama-3.3-70b-versatile"
    )
    
    print(f"[+] Generation complete: {output_path}")

if __name__ == "__main__":
    main()