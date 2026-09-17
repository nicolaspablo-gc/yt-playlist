import os

PLAYLISTS_DIR = "playlists"
IDS_FILE = "ids.tsv"


def load_ids():
    mapping = {}
    with open(IDS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                playlist_id, name = parts
                mapping[name] = playlist_id
    return mapping


def read_remote(youtube, playlist_id):
    """Returns {video_id: {url, title, availability}} for all videos in the playlist."""
    videos = {}
    page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token,
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            title = snippet["title"]
            availability = "deleted" if title in ("[Deleted video]", "[Private video]") else "available"
            videos[video_id] = {
                "url": f"https://youtube.com/watch?v={video_id}",
                "title": title,
                "availability": availability,
            }

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return videos


def read_local(name):
    """Returns {video_id: {url, title, availability}} from playlists/<name>.tsv."""
    path = os.path.join(PLAYLISTS_DIR, f"{name}.tsv")
    if not os.path.exists(path):
        return {}

    videos = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t", 2)
            if len(parts) == 3:
                url, availability, title = parts
                video_id = url.split("v=")[-1]
                videos[video_id] = {"url": url, "title": title, "availability": availability}

    return videos


def diff(before, after):
    """Compare two {video_id: ...} dicts. Returns (added, deleted) sets of IDs."""
    before_ids = set(before.keys())
    after_ids = set(after.keys())
    return after_ids - before_ids, before_ids - after_ids
