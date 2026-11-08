
from pathlib import Path
import re


# Project directory: LLM OPS rag project/
PROJECT_DIR = Path(__file__).resolve().parent

INPUT_DIR = PROJECT_DIR / "transcripts"
OUTPUT_DIR = PROJECT_DIR / "cleaned_transcripts"


# Matches WebVTT timestamps, including optional cue settings.
# Examples:
# 00:01:47.400 --> 00:01:57.400
# 01:47.400 --> 01:57.400
TIMESTAMP_PATTERN = re.compile(
    r"^(?:\d{2}:)?\d{2}:\d{2}\.\d{3}\s+-->\s+"
    r"(?:\d{2}:)?\d{2}:\d{2}\.\d{3}(?:\s+.*)?$"
)


def clean_transcript(content: str) -> str:
    """Remove WebVTT formatting while preserving transcript text."""

    cleaned_lines = []
    skip_metadata_block = False

    for line in content.splitlines():
        line = line.strip()

        # Skip empty lines and end metadata blocks.
        if not line:
            skip_metadata_block = False
            continue

        # Skip the contents of WebVTT NOTE, STYLE and REGION blocks.
        if line.startswith(("NOTE", "STYLE", "REGION")):
            skip_metadata_block = True
            continue

        if skip_metadata_block:
            continue

        # Remove WebVTT header.
        if line == "WEBVTT":
            continue

        # Remove timestamps.
        if TIMESTAMP_PATTERN.match(line):
            continue

        # Remove numeric subtitle cue identifiers.
        if line.isdigit():
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def process_transcripts() -> None:
    """Clean all VTT and TXT files and save them to the output folder."""

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Transcript folder not found: {INPUT_DIR}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript_files = [
        file
        for file in INPUT_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in {".vtt", ".txt"}
    ]

    if not transcript_files:
        print(f"No transcript files found in: {INPUT_DIR}")
        return

    processed_count = 0

    for file in transcript_files:
        try:
            content = file.read_text(encoding="utf-8-sig")

            cleaned_content = clean_transcript(content)

            output_file = OUTPUT_DIR / file.name
            output_file.write_text(cleaned_content, encoding="utf-8")

            processed_count += 1
            print(f"Cleaned: {file.name}")

        except (OSError, UnicodeError) as error:
            print(f"Failed: {file.name} - {error}")

    print(f"\nProcessed {processed_count}/{len(transcript_files)} files.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    process_transcripts()
