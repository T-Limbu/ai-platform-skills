"""Dynamic UI/UX Knowledge Distiller powered by YouTube Transcripts, yt-dlp, and Gemini Files API.

Extracts YouTube transcripts or falls back to yt-dlp subtitles/audio with Gemini Files API,
and dynamically slots knowledge into modular, self-organizing topic playbooks
(references/<topic>.md) as the knowledge base grows.

Usage:
  python distill_ui_ux.py --url https://www.youtube.com/watch?v=VIDEO_ID
  python distill_ui_ux.py --id VIDEO_ID
  python distill_ui_ux.py --batch videos.txt
"""

import os
import sys
import json
import re
import time
import tempfile
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

SKILL_ROOT = Path(__file__).parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"
INDEX_MD = REFERENCES_DIR / "INDEX.md"

FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]


def extract_video_id(url_or_id: str) -> str:
    """Extracts raw 11-character video ID from YouTube URL or ID string."""
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and not ("/" in url_or_id or "?" in url_or_id or "&" in url_or_id):
        return url_or_id
    match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", url_or_id)
    if match:
        return match.group(1)
    return url_or_id


def fetch_transcript(video_id: str) -> str:
    """Pulls full timestamped text from YouTube via youtube-transcript-api."""
    if not YouTubeTranscriptApi:
        raise ImportError("youtube-transcript-api is not installed.")
    api = YouTubeTranscriptApi()
    snippets = api.fetch(video_id)
    lines = []
    for s in snippets:
        mins = int(s.start // 60)
        secs = int(s.start % 60)
        lines.append(f"[{mins:02d}:{secs:02d}] {s.text}")
    return "\n".join(lines)


def parse_subtitle_file(file_path: Path) -> str:
    """Parses .vtt, .srt, or .json3 subtitle file into plain timestamped lines."""
    if file_path.suffix == ".json3":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            lines = []
            for event in data.get("events", []):
                t_start = event.get("tStartMs", 0) // 1000
                mins, secs = divmod(t_start, 60)
                segs = event.get("segs", [])
                text = "".join(s.get("utf8", "") for s in segs).strip()
                if text and text != "\n":
                    lines.append(f"[{mins:02d}:{secs:02d}] {text}")
            return "\n".join(lines)
        except Exception as e:
            print(f"    [!] Error parsing json3 subtitles: {e}")
            return ""

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()

        lines = []
        last_text = ""
        current_time = ""
        timestamp_re = re.compile(r"(?:(\d{1,2}):)?(\d{2}):(\d{2})[.,]\d{3}\s*-->")

        for raw_line in raw.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if any(line.startswith(prefix) for prefix in ("WEBVTT", "NOTE", "Kind:", "Language:", "Style:", "Region:")):
                continue
            if line.isdigit():
                continue

            ts_match = timestamp_re.search(line)
            if ts_match:
                hours = int(ts_match.group(1) or 0)
                mins = int(ts_match.group(2)) + hours * 60
                secs = int(ts_match.group(3))
                current_time = f"[{mins:02d}:{secs:02d}]"
                continue

            clean_text = re.sub(r"<[^>]+>", "", line).strip()
            if clean_text and clean_text != last_text:
                if current_time:
                    lines.append(f"{current_time} {clean_text}")
                    current_time = ""
                else:
                    lines.append(clean_text)
                last_text = clean_text

        return "\n".join(lines)
    except Exception as e:
        print(f"    [!] Error parsing subtitle file {file_path.name}: {e}")
        return ""


def fetch_transcript_ytdlp(video_url: str) -> str:
    """Attempts to extract captions/subtitles via yt_dlp if available."""
    if not yt_dlp:
        print("    [!] yt-dlp is not installed.")
        return ""

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en.*", "en"],
                "subtitlesformat": "vtt/srt/best",
                "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            sub_files = [f for f in Path(temp_dir).glob("*") if f.suffix in (".vtt", ".srt", ".json3")]
            if sub_files:
                text = parse_subtitle_file(sub_files[0])
                if text.strip():
                    return text.strip()
    except Exception as e:
        print(f"    [!] yt-dlp subtitle extraction failed: {e}")

    return ""


def download_audio_ytdlp(video_url: str, target_dir: Path) -> Path:
    """Uses yt_dlp to download the audio stream to a temporary audio file."""
    if not yt_dlp:
        raise ImportError("yt-dlp is not installed.")

    outtmpl = str(target_dir / "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    audio_files = [
        f for f in target_dir.glob("*")
        if f.is_file() and not f.name.endswith(".part") and f.suffix.lower() in (".m4a", ".mp3", ".webm", ".opus", ".aac", ".wav", ".mp4", ".ogg")
    ]
    if not audio_files:
        all_files = [f for f in target_dir.glob("*") if f.is_file() and not f.name.endswith(".part")]
        if not all_files:
            raise RuntimeError("No audio file found after yt-dlp download.")
        return max(all_files, key=lambda f: f.stat().st_size)

    return audio_files[0]


def parse_gemini_json(raw_text: str) -> dict:
    """Safely extracts and parses JSON dictionary from LLM response text."""
    if not raw_text:
        return {}
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return {}


def distill_and_route_with_gemini(transcript: str, video_title: str = "YouTube Video") -> dict:
    """Distills raw transcript text into categorized topic blocks via Gemini models."""
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
        models_to_try = FALLBACK_MODELS
        response = None
        for model_name in models_to_try:
            try:
                print(f"    [*] Attempting transcript analysis with {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    break
            except Exception as model_err:
                print(f"        [-] Model {model_name} failed: {model_err}")

        if not response or not response.text:
            return {}

        return parse_gemini_json(response.text)
    except Exception as e:
        print(f"Gemini API call / parsing note: {e}")
        return {}


def distill_with_gemini_audio(video_url: str, video_title: str = "YouTube Video") -> dict:
    """Downloads audio via yt-dlp, uploads to Gemini Files API, and analyzes multimodal audio."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY not found in environment.")
        return {}

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[-] Failed to initialize Gemini Client: {e}")
        return {}

    file_ref = None
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        try:
            print("    [*] Downloading audio stream via yt-dlp...")
            audio_path = download_audio_ytdlp(video_url, temp_dir_path)
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            print(f"    [+] Audio stream downloaded: {audio_path.name} ({file_size_mb:.2f} MB)")

            print("    [*] Uploading audio stream to Gemini Files API...")
            file_ref = client.files.upload(file=str(audio_path))
            file_name = file_ref.name
            print(f"    [+] Uploaded to Gemini Files API: {file_name}")

            # Poll until file is ACTIVE
            state_name = getattr(file_ref.state, "name", str(file_ref.state))
            poll_count = 0
            while state_name == "PROCESSING":
                poll_count += 1
                if poll_count > 60:
                    raise TimeoutError(f"Gemini file {file_name} stuck in PROCESSING state.")
                print(f"    [*] Waiting for audio file processing (poll {poll_count})...")
                time.sleep(3)
                file_ref = client.files.get(name=file_name)
                state_name = getattr(file_ref.state, "name", str(file_ref.state))

            if state_name != "ACTIVE":
                raise RuntimeError(f"Audio file failed processing, state: {state_name}")

            prompt = f"""
You are the Principal Design Systems Architect at Apple and Linear.
Analyze the audio from this YouTube design masterclass:

Title: {video_title}

Task:
Break down the masterclass into concrete, hardened, mathematical UI/UX design laws and actionable techniques.
Do not force content into pre-set categories. Group findings dynamically by topic (e.g., 'typography', 'layout-and-grids', 'color-and-darkmode', 'components-and-buttons', 'touch-and-mobile', 'forms-and-inputs', 'interaction-states', 'depth-and-overlays', 'data-visualization', 'paywalls', 'onboarding', etc.).

Return ONLY a strictly valid JSON object where keys are clean kebab-case topic slugs and values are detailed markdown strings for that topic:
{{
  "topic-slug": "# Topic Title\\n\\n### Source: {video_title}\\n\\n### Concrete Rules...\\n\\n### Code Presets...\\n\\n### Anti-Patterns..."
}}
"""
            models_to_try = FALLBACK_MODELS
            response = None
            for model_name in models_to_try:
                try:
                    print(f"    [*] Attempting audio distillation with {model_name}...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[file_ref, prompt],
                    )
                    if response and response.text:
                        break
                except Exception as model_err:
                    print(f"        [-] Model {model_name} failed: {model_err}")

            if not response or not response.text:
                print("    [-] All Gemini models failed to generate distillation from audio.")
                return {}

            return parse_gemini_json(response.text)

        except Exception as e:
            print(f"    [-] Gemini audio distillation failed: {e}")
            return {}
        finally:
            if file_ref and hasattr(file_ref, "name") and file_ref.name:
                try:
                    print(f"    [*] Deleting temporary Gemini file {file_ref.name}...")
                    client.files.delete(name=file_ref.name)
                    print(f"    [+] Successfully deleted Gemini file {file_ref.name}")
                except Exception as del_err:
                    print(f"    [!] Warning: Failed to delete Gemini file {file_ref.name}: {del_err}")


def distill_with_gemini_native_url(video_url: str, video_title: str = "YouTube Video") -> dict:
    """Fallback handler using Gemini native YouTube multimodal comprehension (Google servers inspect YouTube directly)."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("    [-] GEMINI_API_KEY not found in environment.")
        return {}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = f"""
You are the Principal Design Systems Architect at Apple and Linear.
Analyze this YouTube design masterclass video: {video_url}

Task:
Break down the masterclass into concrete, hardened, mathematical UI/UX design laws and actionable techniques.
Do not force content into pre-set categories. Group findings dynamically by topic (e.g., 'typography', 'layout-and-grids', 'color-and-darkmode', 'components-and-buttons', 'touch-and-mobile', 'forms-and-inputs', 'interaction-states', 'depth-and-overlays', 'data-visualization', 'paywalls', 'onboarding', etc.).

Return ONLY a strictly valid JSON object where keys are clean kebab-case topic slugs and values are detailed markdown strings for that topic:
{{
  "topic-slug": "# Topic Title\\n\\n### Source: {video_title}\\n\\n### Concrete Rules...\\n\\n### Code Presets...\\n\\n### Anti-Patterns..."
}}
"""
        print("    [*] Calling Gemini native YouTube video understanding (Google server direct ingestion)...")
        models_to_try = FALLBACK_MODELS
        response = None
        for model_name in models_to_try:
            try:
                print(f"    [*] Attempting native YouTube video analysis with {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_uri(file_uri=video_url, mime_type="video/mp4"),
                        types.Part.from_text(text=prompt),
                    ],
                )
                if response and response.text:
                    break
            except Exception as model_err:
                print(f"        [-] Model {model_name} failed: {model_err}")

        if not response or not response.text:
            return {}

        return parse_gemini_json(response.text)
    except Exception as e:
        print(f"    [-] Gemini native YouTube video analysis failed: {e}")
        return {}


def distill_with_gemini_multimodal(video_url: str, video_title: str = "YouTube Video") -> dict:
    """Fallback handler using audio stream download & Gemini Files API, with native URL fallback."""
    res = distill_with_gemini_audio(video_url, video_title)
    if not res:
        res = distill_with_gemini_native_url(video_url, video_title)
    return res


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
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    display_title = title or f"YouTube Video ({video_id})"
    print(f"[*] Processing: {display_title} [{video_id}]")

    topic_blocks = {}
    transcript = None
    is_ci = bool(os.environ.get("GITHUB_ACTIONS"))

    # In CI environments, avoid YouTube datacenter IP blocking by using Gemini native multimodal directly
    if is_ci:
        # Check if transcript is already cached in repository
        cached_file = REFERENCES_DIR / "raw-transcripts" / f"{video_id}.txt"
        if cached_file.exists():
            print(f"    [+] Found local cached transcript at {cached_file.name}")
            try:
                with open(cached_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "Title:" in content and "ID:" in content:
                        parts = content.split("\n\n", 1)
                        if len(parts) > 1:
                            content = parts[1]
                    transcript = content.strip()
                    print(f"    [+] Loaded cached transcript ({len(transcript.splitlines())} lines)")
                    topic_blocks = distill_and_route_with_gemini(transcript, display_title)
            except Exception as read_err:
                print(f"    [!] Failed to read cached transcript: {read_err}")

        # If un-cached, immediately use Google-to-Google Gemini native multimodal comprehension
        if not topic_blocks:
            print("    [*] CI environment detected: Bypassing runner scraping & calling Gemini native YouTube comprehension directly...")
            topic_blocks = distill_with_gemini_native_url(canonical_url, display_title)

    else:
        # Local execution: Tier 1 youtube-transcript-api -> Tier 2 yt-dlp -> Tier 3 cache -> Tier 4 audio -> Tier 5 native
        try:
            transcript = fetch_transcript(video_id)
            print(f"    [+] Transcript retrieved via youtube-transcript-api ({len(transcript.splitlines())} lines)")
        except Exception as e:
            print(f"    [!] youtube-transcript-api blocked or unavailable: {e}")

        if not transcript:
            print("    [*] Attempting subtitle extraction via yt-dlp...")
            try:
                transcript = fetch_transcript_ytdlp(canonical_url)
                if transcript:
                    print(f"    [+] Subtitles retrieved via yt-dlp ({len(transcript.splitlines())} lines)")
            except Exception as yt_err:
                print(f"    [!] yt-dlp subtitle extraction failed: {yt_err}")

        if not transcript:
            cached_file = REFERENCES_DIR / "raw-transcripts" / f"{video_id}.txt"
            if cached_file.exists():
                print(f"    [+] Found local cached transcript at {cached_file.name}")
                try:
                    with open(cached_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "Title:" in content and "ID:" in content:
                            parts = content.split("\n\n", 1)
                            if len(parts) > 1:
                                content = parts[1]
                        transcript = content.strip()
                        print(f"    [+] Loaded cached transcript ({len(transcript.splitlines())} lines)")
                except Exception as read_err:
                    print(f"    [!] Failed to read cached transcript: {read_err}")

        if transcript:
            raw_dir = REFERENCES_DIR / "raw-transcripts"
            raw_dir.mkdir(parents=True, exist_ok=True)
            with open(raw_dir / f"{video_id}.txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {display_title}\nID: {video_id}\n\n" + transcript)

            topic_blocks = distill_and_route_with_gemini(transcript, display_title)
        else:
            print("    [!] No subtitles available. Switching to yt-dlp audio download & Gemini Files API...")
            topic_blocks = distill_with_gemini_audio(canonical_url, display_title)

            if not topic_blocks:
                print("    [!] Audio download blocked or unavailable. Falling back to Gemini native YouTube multimodal analysis...")
                topic_blocks = distill_with_gemini_native_url(canonical_url, display_title)

    # Route and persist topic playbooks
    if topic_blocks:
        for slug, md_content in topic_blocks.items():
            append_or_create_playbook(slug, md_content, video_id, display_title)
        update_references_index()
        print(f"[+] Successfully distilled insights for {display_title}")
    else:
        print("    [-] Failed to distill video into topic blocks.")
        sys.exit(1)


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
