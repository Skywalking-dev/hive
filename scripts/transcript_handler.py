#!/usr/bin/env python3
"""YouTube transcript extraction handler for Hive."""

import os
import sys
import json
import random
import time
import argparse
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# --- Config ---

def get_youtube_api_key() -> str:
    """Get YouTube Data API key from environment."""
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise ValueError("YOUTUBE_API_KEY not set in environment")
    return key


# --- Core API ---

def extract_transcript(video_id: str, languages: tuple = ("es", "en"), max_retries: int = 3) -> dict:
    """Fetch transcript for a YouTube video with exponential backoff."""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        CouldNotRetrieveTranscript,
        NoTranscriptFound,
        TranscriptsDisabled,
    )

    api = YouTubeTranscriptApi()

    for attempt in range(max_retries):
        try:
            fetched = api.fetch(video_id, languages=list(languages))

            transcript_list = [
                {"text": s.text, "start": s.start, "duration": s.duration}
                for s in fetched
            ]

            total_text = " ".join(s.text for s in fetched)

            return {
                "video_id": video_id,
                "title": "",
                "language": fetched.language,
                "language_code": fetched.language_code,
                "total_text": total_text,
                "char_count": len(total_text),
                "segment_count": len(transcript_list),
                "segments": transcript_list,
            }

        except (TranscriptsDisabled, NoTranscriptFound) as exc:
            return None

        except CouldNotRetrieveTranscript as exc:
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            return None

        except Exception:
            return None

    return None


def get_video_metadata(video_id: str) -> dict:
    """Fetch metadata for a single YouTube video via Data API."""
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", developerKey=get_youtube_api_key())
    response = youtube.videos().list(part="snippet", id=video_id).execute()

    items = response.get("items")
    if not items:
        raise ValueError(f"Video {video_id} not found")

    snippet = items[0]["snippet"]
    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "published_at": snippet.get("publishedAt"),
        "channel_title": snippet.get("channelTitle", ""),
    }


def get_channel_videos(channel_id: str, max_results: int = 50) -> list:
    """List videos from a YouTube channel's uploads playlist."""
    from googleapiclient.discovery import build

    if max_results <= 0:
        return []

    youtube = build("youtube", "v3", developerKey=get_youtube_api_key())

    channel_response = youtube.channels().list(
        part="contentDetails", id=channel_id
    ).execute()

    items = channel_response.get("items")
    if not items:
        raise ValueError(f"Channel {channel_id} not found")

    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page = None

    while len(videos) < max_results:
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page,
        ).execute()

        for item in playlist_response.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "video_id": snippet["resourceId"]["videoId"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt"),
            })

        next_page = playlist_response.get("nextPageToken")
        if not next_page:
            break

    return videos[:max_results]


# --- Output ---

def output(success: bool, data=None, error=None):
    """Print JSON result in Hive standard format."""
    result = {"success": success}
    if data is not None:
        result["data"] = data
    if error is not None:
        result["error"] = error
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if success else 1)


# --- Commands ---

def cmd_extract(args):
    """Extract transcript, optionally enriched with metadata."""
    languages = tuple(args.languages.split(",")) if args.languages else ("es", "en")

    transcript = extract_transcript(args.video_id, languages=languages)
    if not transcript:
        output(False, error=f"No transcript available for {args.video_id}")

    # Enrich with metadata if API key available
    try:
        meta = get_video_metadata(args.video_id)
        transcript["title"] = meta.get("title", "")
        transcript["channel_title"] = meta.get("channel_title", "")
        transcript["published_at"] = meta.get("published_at")
    except Exception:
        pass  # metadata is optional

    output(True, data=transcript)


def cmd_metadata(args):
    """Get video metadata only."""
    try:
        meta = get_video_metadata(args.video_id)
        output(True, data=meta)
    except Exception as e:
        output(False, error=str(e))


def cmd_channel(args):
    """List videos from a channel."""
    try:
        videos = get_channel_videos(args.channel_id, max_results=args.max)
        output(True, data={"channel_id": args.channel_id, "count": len(videos), "videos": videos})
    except Exception as e:
        output(False, error=str(e))


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="YouTube transcript handler for Hive")
    sub = parser.add_subparsers(dest="command", required=True)

    # extract
    p_extract = sub.add_parser("extract", help="Extract transcript from video")
    p_extract.add_argument("video_id", help="YouTube video ID")
    p_extract.add_argument("--languages", default="es,en", help="Comma-separated language priority (default: es,en)")
    p_extract.set_defaults(func=cmd_extract)

    # metadata
    p_meta = sub.add_parser("metadata", help="Get video metadata")
    p_meta.add_argument("video_id", help="YouTube video ID")
    p_meta.set_defaults(func=cmd_metadata)

    # channel
    p_chan = sub.add_parser("channel", help="List videos from channel")
    p_chan.add_argument("channel_id", help="YouTube channel ID")
    p_chan.add_argument("--max", type=int, default=50, help="Max results (default: 50)")
    p_chan.set_defaults(func=cmd_channel)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
