#!/usr/bin/env python3
"""
Instagram Business API handler for Hive.
Publish posts, get insights, manage comments, view profile.
Uses Graph API v22.0 directly via HTTP requests.

Env vars:
  INSTAGRAM_TOKEN      - Meta access token with instagram_basic, instagram_content_publish
  INSTAGRAM_ACCOUNT_ID - Instagram Business/Creator account ID (from Graph API, NOT @username)
"""

import os
import sys
import json
import time
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_config() -> tuple[str, str]:
    token = os.environ.get("INSTAGRAM_TOKEN")
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")

    if not token:
        raise ValueError("INSTAGRAM_TOKEN not set in environment")
    if not account_id:
        raise ValueError("INSTAGRAM_ACCOUNT_ID not set in environment")

    return token, account_id


def api_call(
    endpoint: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
    method: str = "GET",
) -> dict:
    """Make a Graph API call."""
    token, _ = get_config()

    url = f"{GRAPH_API_BASE}/{endpoint}"

    if params is None:
        params = {}
    params["access_token"] = token

    if method == "GET":
        url = f"{url}?{urlencode(params)}"
        body = None
        headers = {}
    else:
        url = f"{url}?{urlencode(params)}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data).encode("utf-8") if data else None

    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "data": result}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Profile ---


def profile_info() -> dict:
    """Get Instagram business profile info."""
    _, account_id = get_config()
    return api_call(
        account_id,
        params={
            "fields": "id,name,username,biography,followers_count,follows_count,media_count,profile_picture_url,website"
        },
    )


# --- Media / Posts ---


def media_list(limit: int = 25) -> dict:
    """List recent media posts."""
    _, account_id = get_config()
    return api_call(
        f"{account_id}/media",
        params={
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
            "limit": str(limit),
        },
    )


def media_get(media_id: str) -> dict:
    """Get details of a specific media post."""
    return api_call(
        media_id,
        params={
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count,children{id,media_type,media_url}"
        },
    )


def publish_photo(image_url: str, caption: Optional[str] = None) -> dict:
    """Publish a photo post (2-step: create container → publish)."""
    _, account_id = get_config()

    # Step 1: Create media container
    params = {"image_url": image_url}
    if caption:
        params["caption"] = caption

    container = api_call(f"{account_id}/media", params=params, method="POST")
    if not container.get("success"):
        return container

    container_id = container["data"]["id"]

    # Step 2: Publish
    time.sleep(2)  # allow processing
    return api_call(
        f"{account_id}/media_publish",
        params={"creation_id": container_id},
        method="POST",
    )


def publish_video(video_url: str, caption: Optional[str] = None, media_type: str = "REELS") -> dict:
    """Publish a video/Reel (2-step with polling for processing)."""
    _, account_id = get_config()

    # Step 1: Create media container
    params = {"video_url": video_url, "media_type": media_type}
    if caption:
        params["caption"] = caption

    container = api_call(f"{account_id}/media", params=params, method="POST")
    if not container.get("success"):
        return container

    container_id = container["data"]["id"]

    # Step 2: Poll for processing completion (up to 60s)
    for _ in range(12):
        time.sleep(5)
        status = api_call(container_id, params={"fields": "status_code"})
        if status.get("success") and status["data"].get("status_code") == "FINISHED":
            break
    else:
        return {"success": False, "error": "Video processing timeout (60s). Try publishing manually."}

    # Step 3: Publish
    return api_call(
        f"{account_id}/media_publish",
        params={"creation_id": container_id},
        method="POST",
    )


def publish_carousel(media_urls: list[dict], caption: Optional[str] = None) -> dict:
    """
    Publish a carousel post.
    media_urls: [{"type": "IMAGE", "url": "..."}, {"type": "VIDEO", "url": "..."}]
    """
    _, account_id = get_config()

    # Step 1: Create child containers
    children_ids = []
    for item in media_urls:
        params = {"is_carousel_item": "true"}
        if item["type"].upper() == "IMAGE":
            params["image_url"] = item["url"]
        else:
            params["video_url"] = item["url"]
            params["media_type"] = "VIDEO"

        child = api_call(f"{account_id}/media", params=params, method="POST")
        if not child.get("success"):
            return child
        children_ids.append(child["data"]["id"])

    # Wait for video processing if any
    time.sleep(3)

    # Step 2: Create carousel container
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
    }
    if caption:
        params["caption"] = caption

    container = api_call(f"{account_id}/media", params=params, method="POST")
    if not container.get("success"):
        return container

    container_id = container["data"]["id"]

    # Step 3: Publish
    time.sleep(2)
    return api_call(
        f"{account_id}/media_publish",
        params={"creation_id": container_id},
        method="POST",
    )


# --- Stories ---


def stories_list() -> dict:
    """List current stories (last 24h)."""
    _, account_id = get_config()
    return api_call(
        f"{account_id}/stories",
        params={
            "fields": "id,media_type,media_url,timestamp,permalink"
        },
    )


def publish_story(image_url: Optional[str] = None, video_url: Optional[str] = None) -> dict:
    """Publish a story (image or video)."""
    _, account_id = get_config()

    params = {"media_type": "STORIES"}
    if image_url:
        params["image_url"] = image_url
    elif video_url:
        params["video_url"] = video_url
    else:
        return {"success": False, "error": "Provide image_url or video_url"}

    container = api_call(f"{account_id}/media", params=params, method="POST")
    if not container.get("success"):
        return container

    container_id = container["data"]["id"]
    time.sleep(3)

    return api_call(
        f"{account_id}/media_publish",
        params={"creation_id": container_id},
        method="POST",
    )


# --- Comments ---


def comments_list(media_id: str, limit: int = 25) -> dict:
    """List comments on a media post."""
    return api_call(
        f"{media_id}/comments",
        params={
            "fields": "id,text,username,timestamp,like_count,replies{id,text,username,timestamp}",
            "limit": str(limit),
        },
    )


def comment_reply(comment_id: str, message: str) -> dict:
    """Reply to a comment."""
    return api_call(
        f"{comment_id}/replies",
        params={"message": message},
        method="POST",
    )


def comment_delete(comment_id: str) -> dict:
    """Delete/hide a comment."""
    return api_call(comment_id, params={"hide": "true"}, method="POST")


# --- Insights ---


def account_insights(period: str = "day", metric: Optional[str] = None, metric_type: Optional[str] = None) -> dict:
    """Get account-level insights."""
    _, account_id = get_config()
    default_metrics = "reach,accounts_engaged,total_interactions"
    params = {
        "metric": metric or default_metrics,
        "period": period,
        "metric_type": metric_type or "total_value",
    }
    return api_call(f"{account_id}/insights", params=params)


def media_insights(media_id: str) -> dict:
    """Get insights for a specific media post."""
    return api_call(
        f"{media_id}/insights",
        params={
            "metric": "reach,likes,comments,shares,saves"
        },
    )


# --- Hashtag Search ---


def hashtag_search(query: str) -> dict:
    """Search for a hashtag ID (needed for hashtag feed)."""
    _, account_id = get_config()
    return api_call(
        "ig_hashtag_search",
        params={"q": query, "user_id": account_id},
    )


def hashtag_top_media(hashtag_id: str, limit: int = 25) -> dict:
    """Get top media for a hashtag."""
    _, account_id = get_config()
    return api_call(
        f"{hashtag_id}/top_media",
        params={
            "user_id": account_id,
            "fields": "id,caption,media_type,permalink,like_count,comments_count,timestamp",
            "limit": str(limit),
        },
    )


# --- Mentions & Tags ---


def mentioned_media(limit: int = 25) -> dict:
    """Get media where the account is mentioned."""
    _, account_id = get_config()
    return api_call(
        f"{account_id}/tags",
        params={
            "fields": "id,caption,media_type,permalink,timestamp,username",
            "limit": str(limit),
        },
    )


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(description="Instagram Business API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Profile
    subparsers.add_parser("profile", help="Get profile info")

    # Media
    media_ls = subparsers.add_parser("media", help="List recent posts")
    media_ls.add_argument("--limit", type=int, default=25)

    media_get_p = subparsers.add_parser("media-get", help="Get post details")
    media_get_p.add_argument("id", help="Media ID")

    # Publish photo
    pub_photo = subparsers.add_parser("publish-photo", help="Publish photo")
    pub_photo.add_argument("image_url", help="Public image URL")
    pub_photo.add_argument("--caption", help="Post caption")

    # Publish video/reel
    pub_video = subparsers.add_parser("publish-video", help="Publish video/Reel")
    pub_video.add_argument("video_url", help="Public video URL")
    pub_video.add_argument("--caption")
    pub_video.add_argument("--type", default="REELS", choices=["REELS", "VIDEO"])

    # Publish carousel
    pub_car = subparsers.add_parser("publish-carousel", help="Publish carousel")
    pub_car.add_argument("items", help='JSON: [{"type":"IMAGE","url":"..."},...]')
    pub_car.add_argument("--caption")

    # Stories
    subparsers.add_parser("stories", help="List current stories")

    pub_story = subparsers.add_parser("publish-story", help="Publish story")
    pub_story.add_argument("--image-url")
    pub_story.add_argument("--video-url")

    # Comments
    comm_list = subparsers.add_parser("comments", help="List comments on a post")
    comm_list.add_argument("media_id", help="Media ID")
    comm_list.add_argument("--limit", type=int, default=25)

    comm_reply = subparsers.add_parser("comment-reply", help="Reply to a comment")
    comm_reply.add_argument("comment_id")
    comm_reply.add_argument("message")

    comm_del = subparsers.add_parser("comment-hide", help="Hide a comment")
    comm_del.add_argument("comment_id")

    # Insights
    acc_ins = subparsers.add_parser("insights", help="Account insights")
    acc_ins.add_argument("--period", default="day", choices=["day", "week", "days_28", "month", "lifetime"])
    acc_ins.add_argument("--metric", help="Comma-separated metrics")

    med_ins = subparsers.add_parser("media-insights", help="Post insights")
    med_ins.add_argument("media_id")

    # Hashtags
    ht_search = subparsers.add_parser("hashtag-search", help="Search hashtag")
    ht_search.add_argument("query")

    ht_top = subparsers.add_parser("hashtag-top", help="Top media for hashtag")
    ht_top.add_argument("hashtag_id")
    ht_top.add_argument("--limit", type=int, default=25)

    # Mentions
    mentions = subparsers.add_parser("mentions", help="Media where you are mentioned")
    mentions.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()

    try:
        if args.command == "profile":
            result = profile_info()
        elif args.command == "media":
            result = media_list(args.limit)
        elif args.command == "media-get":
            result = media_get(args.id)
        elif args.command == "publish-photo":
            result = publish_photo(args.image_url, args.caption)
        elif args.command == "publish-video":
            result = publish_video(args.video_url, args.caption, args.type)
        elif args.command == "publish-carousel":
            items = json.loads(args.items)
            result = publish_carousel(items, args.caption)
        elif args.command == "stories":
            result = stories_list()
        elif args.command == "publish-story":
            result = publish_story(args.image_url, args.video_url)
        elif args.command == "comments":
            result = comments_list(args.media_id, args.limit)
        elif args.command == "comment-reply":
            result = comment_reply(args.comment_id, args.message)
        elif args.command == "comment-hide":
            result = comment_delete(args.comment_id)
        elif args.command == "insights":
            result = account_insights(args.period, args.metric)
        elif args.command == "media-insights":
            result = media_insights(args.media_id)
        elif args.command == "hashtag-search":
            result = hashtag_search(args.query)
        elif args.command == "hashtag-top":
            result = hashtag_top_media(args.hashtag_id, args.limit)
        elif args.command == "mentions":
            result = mentioned_media(args.limit)
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
