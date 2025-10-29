from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import defaultdict
from dotenv import load_dotenv

import os
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Iterable

from googleapiclient.discovery import build

load_dotenv()

@dataclass(frozen=True)
class Comment:
    """
    Minimal comment object containing only the fields required for the logic layer.

    Fields:
        id:        The comment's ID.
        author_id: Canonical key for the author (channel ID if available, otherwise a name-based key).
        author_name: Display name for the author (for reporting / debugging).
        like_count: Number of likes on this comment.
        parent_id: If None -> top-level comment; otherwise the ID of its parent top-level comment.
    """
    id: str
    author_id: str
    author_name: str
    like_count: int
    parent_id: Optional[str] = None


def _author_key_from_snippet(snippet: dict) -> str:
    """
    Prefer stable channel ID; if missing, fall back to a name-based key.
    """
    ch = snippet.get("authorChannelId", {})
    cid = ch.get("value")
    if cid:  # canonical
        return cid
    # Fallback to a name-based pseudo-ID. This isn't perfectly unique,
    # but covers rare cases where channel ID isn't exposed.
    name = snippet.get("authorDisplayName") or "UNKNOWN"
    return f"name:{name}"


def _to_comment_from_top_level_item(item: dict) -> Comment:
    top = item["snippet"]["topLevelComment"]
    sn = top["snippet"]
    return Comment(
        id=top["id"],
        author_id=_author_key_from_snippet(sn),
        author_name=sn.get("authorDisplayName", "UNKNOWN"),
        like_count=int(sn.get("likeCount", 0)),
        parent_id=None,
    )


def _to_comment_from_reply_item(item: dict) -> Comment:
    sn = item["snippet"]
    return Comment(
        id=item["id"],
        author_id=_author_key_from_snippet(sn),
        author_name=sn.get("authorDisplayName", "UNKNOWN"),
        like_count=int(sn.get("likeCount", 0)),
        parent_id=sn.get("parentId"),
    )


def build_youtube_client(api_key: Optional[str] = None):
    """
    Build a YouTube Data API client using an API key (no OAuth needed for public comments).
    """
    api_key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key. Set YOUTUBE_API_KEY env var or pass api_key.")
    return build("youtube", "v3", developerKey=api_key)


def fetch_top_level_comments(
    youtube,
    *,
    video_id: str,
    max_comments: Optional[int] = 500,
    order: str = "time",
    sleep: float = 0.0,
) -> List[Comment]:
    """
    Fetch top-level comments for a single video.

    Args:
        youtube: YouTube API client from googleapiclient.discovery.build
        video_id: The 11-char YouTube video ID.
        max_comments: Soft cap on number of top-level comments to fetch (None = no cap).
        order: "time" or "relevance".
        sleep: Optional delay between paginated requests (seconds).

    Returns:
        List[Comment]: minimal Comment objects (top-level only).
    """
    results: List[Comment] = []
    page_token = None
    fetched = 0

    while True:
        req = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token,
            order=order,
            textFormat="plainText",
        )

        resp = req.execute()
        items = resp.get("items", [])

        for it in items:
            results.append(_to_comment_from_top_level_item(it))
            fetched += 1
            if max_comments is not None and fetched >= max_comments:
                break

        if max_comments is not None and fetched >= max_comments:
            break

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

        if sleep:
            time.sleep(sleep)

    return results


def fetch_replies_for_parent(
    youtube,
    *,
    parent_id: str,
    sleep: float = 0.0,
) -> List[Comment]:
    """
    Fetch ALL replies to a single top-level comment.
    """
    replies: List[Comment] = []
    page_token = None

    while True:
        req = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            maxResults=100,
            pageToken=page_token,
            textFormat="plainText",
        )
        resp = req.execute()
        items = resp.get("items", [])

        for item in items:
            replies.append(_to_comment_from_reply_item(item))

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

        if sleep:
            time.sleep(sleep)

    return replies


def fetch_all_comments_for_video(
    youtube,
    *,
    video_id: str,
    max_comments: Optional[int] = 500,
    order: str = "time",
    sleep: float = 0.0,
) -> List[Comment]:
    """
    Fetch top-level comments and their replies for a video, returning a flat list of Comment objects.

    Notes:
        - Replies are fetched for each retrieved top-level comment.
        - This can consume quota for large videos; consider lowering `max_comments`.

    Returns:
        List[Comment]: both top-level comments (parent_id=None) and replies (parent_id=<top id>).
    """
    top_level = fetch_top_level_comments(
        youtube, video_id=video_id, max_comments=max_comments, order=order, sleep=sleep
    )

    print(f"Successfully retrieved comments. Found {len(top_level)} items")

    all_comments: List[Comment] = list(top_level)

    # Fetch replies for each top-level comment we actually pulled
    print("Retrieving comment replies...")
    for tl in top_level:
        all_comments.extend(fetch_replies_for_parent(youtube, parent_id=tl.id, sleep=sleep))

    return all_comments

@dataclass
class User:
    author_id: str
    author_name: str
    reply_count: int   # replies to their top-level comments by others
    like_count: int    # likes across all their comments (top-level + replies)
    score: int         # reply_count + like_count


def compute_top_users_by_popularity(
    comments: List[Comment],
    top_n: int = 10
) -> List[User]:
    """
    Compute the top-N users by "popularity".

    Popularity definition (per user):
    score = (# replies to their top-level comments, excluding their own replies)
            + (total likes on all their comments, including replies)

    Args:
        comments: Flat list of Comment objects (top-level have parent_id=None).
        top_n:    Number of top users to return.

    Returns:
        Sorted list (desc) of User of length <= top_n.
    """
    # Partition: top-level vs replies
    top_level = [c for c in comments if c.parent_id is None]
    replies   = [c for c in comments if c.parent_id is not None]

    # Index replies by their parent top-level comment ID
    replies_by_parent: Dict[str, List[Comment]] = defaultdict(list)
    for r in replies:
        if r.parent_id:  # safety
            replies_by_parent[r.parent_id].append(r)

    # 1) Likes per author across ALL comments (top-level + replies)
    likes_per_author: Dict[str, int] = defaultdict(int)
    author_name_latest: Dict[str, str] = {}
    for c in comments:
        likes_per_author[c.author_id] += int(c.like_count or 0)
        author_name_latest[c.author_id] = c.author_name  # keep the most recent seen

    # 2) Reply counts for authors' top-level comments (excluding their own replies)
    replies_to_their_comments: Dict[str, int] = defaultdict(int)
    for tl in top_level:
        others_replies = [
            r for r in replies_by_parent.get(tl.id, [])
            if r.author_id != tl.author_id
        ]
        replies_to_their_comments[tl.author_id] += len(others_replies)

    # 3) Build rows
    rows: List[User] = []
    author_keys = set(list(likes_per_author.keys()) + list(replies_to_their_comments.keys()))
    for author_id in author_keys:
        row = User(
            author_id=author_id,
            author_name=author_name_latest.get(author_id, author_id),
            reply_count=replies_to_their_comments.get(author_id, 0),
            like_count=likes_per_author.get(author_id, 0),
            score=replies_to_their_comments.get(author_id, 0) + likes_per_author.get(author_id, 0)
        )
        rows.append(row)

    # 4) Sort by score desc, then replies desc, then likes desc, then name asc
    rows.sort(key=lambda r: (-r.score, -r.reply_count, -r.like_count, r.author_name.lower()))

    return rows[:top_n]

if __name__ == "__main__":
    """
    Example run:
        export YOUTUBE_API_KEY="YOUR_KEY"
        python script.py
    """
    VIDEO_ID = "dQw4w9WgXcQ"  # <-- replace with the target video ID
    API_KEY = os.getenv("YOUTUBE_API_KEY")  # or set directly

    print("Building Client...")

    youtube = build_youtube_client(API_KEY)

    print("Fetching Comments and Replies...")

    # 1) Fetch data
    comments = fetch_all_comments_for_video(
        youtube,
        video_id=VIDEO_ID,
        max_comments=1000,  # tune for your quota/time
        order="time",
        sleep=0.0,
    )

    print("Computing Top Users...")
    # 2) Run logic
    top10 = compute_top_users_by_popularity(comments, top_n=10)

    # 3) Print results
    print(f"Top {len(top10)} users by popularity for video {VIDEO_ID}:")
    for i, row in enumerate(top10, start=1):
        print(
            f"{i:>2}. {row.author_name} "
            f"(id={row.author_id}) "
            f"— replies_to_their_comments={row.reply_count}, "
            f"likes_on_their_comments={row.like_count}, "
            f"score={row.score}"
        )
