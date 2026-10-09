"""Dynamic UI/UX Knowledge Distiller powered by YouTube Transcripts and Gemini.

Extracts YouTube transcripts and dynamically slots knowledge into modular,
self-organizing topic playbooks (references/<topic>.md) as the knowledge base grows.

Usage:
  python distill_ui_ux.py --url https://www.youtube.com/watch?v=VIDEO_ID
  python distill_ui_ux.py --id VIDEO_ID
  python distill_ui_ux.py --batch videos.txt
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

SKILL_ROOT = Path(__file__).parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"
INDEX_MD = REFERENCES_DIR / "INDEX.md"


def extract_video_id(url_or_id: str) -> str:
    """Extracts raw 11-character video ID from YouTube URL or ID string."""
    if len(url_or_id) == 11 and not ("/" in url_or_id or "?" in url_or_id):
        return url_or_id
    match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()


def fetch_transcript(video_id: str) -> str:
    """Pulls full timestamped text from YouTube."""
    api = YouTubeTranscriptApi()
    snippets = api.fetch(video_id)
    lines = []
    for s in snippets:
        mins = int(s.start // 60)
        secs = int(s.start % 60)
        lines.append(f"[{mins:02d}:{secs:02d}] {s.text}")
    return "\n".join(lines)


def distill_and_route_with_gemini(transcript: str, video_title: str = "YouTube Video") -> dict:
    """Distills raw transcript text into categorized topic blocks via Gemini 2.0 Flash."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[INFO] GEMINI_API_KEY not found in environment.")
        print("Raw transcript saved for offline/in-chat distillation.\n")
        return {}

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are the Principal Design Systems Architect at Apple and Linear.
Analyze the following YouTube design masterclass transcript:

Title: {video_title}

TRANSCRIPT:
{transcript}

Task:
Break down the video into concrete, hardened, mathematical UI/UX design laws and actionable techniques.
Do not force content into pre-set categories. Group findings dynamically by topic (e.g., 'typography', 'layout-and-grids', 'color-and-darkmode', 'components-and-buttons', 'touch-and-mobile', 'forms-and-inputs', 'interaction-states', 'depth-and-overlays', 'data-visualization', 'paywalls', 'onboarding', etc.).

Return a strictly valid JSON object where keys are clean kebab-case topic slugs and values are detailed markdown strings for that topic:
{{
  "topic-slug": "# Topic Title\\n\\n### Source: {video_title}\\n\\n### Concrete Rules...\\n\\n### Code Presets...\\n\\n### Anti-Patterns..."
}}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        # Parse JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"Gemini API call / parsing note: {e}")
        return {}


def update_references_index():
    """Generates a clean Table of Contents of all active topic playbooks."""
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([f for f in REFERENCES_DIR.glob("*.md") if f.name not in ("INDEX.md", "README.md")])
    
    lines = [
        "# 📚 UI/UX Master Knowledge Base Index",
        "",
        "> Dynamically evolved from top-tier UI/UX engineering masterclasses.",
        "",
        f"**Active Playbooks:** `{len(files)}`",
        "",
        "| Playbook | Topic Focus | File Path |",
        "| :--- | :--- | :--- |",
    ]
    for f in files:
        title = f.stem.replace("-", " ").title()
        lines.append(f"| **{title}** | Specialized Playbook | [`references/{f.name}`]({f.name}) |")
    
    with open(INDEX_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"-> Updated dynamic index at {INDEX_MD} ({len(files)} playbooks)")


def append_or_create_playbook(topic_slug: str, content: str, video_id: str, title: str):
    """Appends insights to an existing playbook or dynamically creates a new one."""
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    playbook_file = REFERENCES_DIR / f"{topic_slug}.md"

    is_new = not playbook_file.exists()
    mode = "w" if is_new else "a"

    with open(playbook_file, mode, encoding="utf-8") as f:
        if is_new:
            f.write(f"# 📘 {topic_slug.replace('-', ' ').title()} Playbook\n\n")
        f.write(f"\n\n---\n\n## 🎥 Reference: {title} (`{video_id}`)\n\n" + content.strip() + "\n")

    action = "Created new playbook" if is_new else "Appended to"
    print(f"    [+] {action} {playbook_file.name}")


def process_video(url_or_id: str, title: str = ""):
    video_id = extract_video_id(url_or_id)
    display_title = title or f"YouTube Video ({video_id})"
    print(f"[*] Processing: {display_title} [{video_id}]")

    try:
        transcript = fetch_transcript(video_id)
        print(f"    [+] Transcript retrieved ({len(transcript.splitlines())} lines)")
    except Exception as e:
        print(f"    [-] Failed to fetch transcript for {video_id}: {e}")
        return

    # Save raw transcript copy
    raw_dir = REFERENCES_DIR / "raw-transcripts"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with open(raw_dir / f"{video_id}.txt", "w", encoding="utf-8") as f:
        f.write(f"Title: {display_title}\nID: {video_id}\n\n" + transcript)

    # Distill and dynamically route into topic playbooks
    topic_blocks = distill_and_route_with_gemini(transcript, display_title)
    if topic_blocks:
        for slug, md_content in topic_blocks.items():
            append_or_create_playbook(slug, md_content, video_id, display_title)
        update_references_index()
    else:
        print("    [+] Raw transcript saved for in-chat distillation.")


def main():
    parser = argparse.ArgumentParser(description="Dynamically distill YouTube UI/UX videos into modular topic playbooks.")
    parser.add_argument("--url", help="YouTube video URL")
    parser.add_argument("--id", help="YouTube video ID")
    parser.add_argument("--batch", help="Path to text file containing video URLs or IDs (one per line)")

    args = parser.parse_args()

    if args.url:
        process_video(args.url)
    elif args.id:
        process_video(args.id)
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"Batch file not found: {batch_path}")
            sys.exit(1)
        with open(batch_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    process_video(line)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
