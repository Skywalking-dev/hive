---
name: instagram
description: Manage Instagram Business account - publish posts/reels/stories/carousels, view insights, manage comments, search hashtags. Use when user needs to post content, check performance, or moderate comments on Instagram.
allowed-tools: Bash, Read
---

# Instagram Business API (Graph API v22)

Manage Instagram Business account via Python CLI.

## Prerequisites
- `INSTAGRAM_TOKEN` in `.env` (Meta access token with `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights`)
- `INSTAGRAM_ACCOUNT_ID` in `.env` (Instagram Business account ID from Graph API)

## Quick Commands

```bash
# Profile info
python scripts/instagram_handler.py profile

# List recent posts
python scripts/instagram_handler.py media
python scripts/instagram_handler.py media --limit 10

# Get post details
python scripts/instagram_handler.py media-get 17895695123456789

# Publish photo
python scripts/instagram_handler.py publish-photo "https://example.com/image.jpg" --caption "New post!"

# Publish Reel
python scripts/instagram_handler.py publish-video "https://example.com/video.mp4" --caption "Check this out"

# Publish carousel
python scripts/instagram_handler.py publish-carousel '[{"type":"IMAGE","url":"https://..."},{"type":"IMAGE","url":"https://..."}]' --caption "Swipe!"

# Stories
python scripts/instagram_handler.py stories
python scripts/instagram_handler.py publish-story --image-url "https://example.com/story.jpg"

# Comments
python scripts/instagram_handler.py comments 17895695123456789
python scripts/instagram_handler.py comment-reply 17895695123456789 "Thanks!"
python scripts/instagram_handler.py comment-hide 17895695123456789

# Insights
python scripts/instagram_handler.py insights
python scripts/instagram_handler.py insights --period week
python scripts/instagram_handler.py media-insights 17895695123456789

# Hashtags
python scripts/instagram_handler.py hashtag-search "marketing"
python scripts/instagram_handler.py hashtag-top 17843853986123456

# Mentions
python scripts/instagram_handler.py mentions
```

## Publishing Flow

All publishing is **2-step** (container → publish):
1. Create media container with URL + metadata
2. Meta processes the media (instant for images, seconds for video)
3. Publish the container

Videos poll for processing up to 60s. If timeout, publish manually from Meta Business Suite.

## Media Requirements

| Type | Format | Max Size | Aspect Ratio |
|------|--------|----------|--------------|
| Photo | JPEG, PNG | 8MB | 1:1, 4:5, 1.91:1 |
| Reel | MP4, MOV | 1GB | 9:16 (vertical) |
| Story | JPEG/MP4 | 8MB/100MB | 9:16 |
| Carousel | Mix | Per item | Per item |

- Image/video URLs must be **publicly accessible**
- Carousel: 2-10 items, mix of images and videos

## Insight Periods
`day`, `week`, `days_28`, `month`, `lifetime`

## Account Metrics
`impressions`, `reach`, `follower_count`, `profile_views`, `website_clicks`, `email_contacts`

## Media Metrics
`impressions`, `reach`, `engagement`, `saved`, `shares`, `video_views` (for Reels)

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `190` | Invalid/expired token | Refresh INSTAGRAM_TOKEN |
| `9004` | Image URL not accessible | Ensure public URL, no auth required |
| `36003` | Video processing failed | Check format/size, retry |
| `10` | Permission denied | Check token scopes |
| `4` | Rate limit | Wait and retry (200 calls/user/hour) |
