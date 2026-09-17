import sys
import argparse
from auth import get_credentials
from googleapiclient.discovery import build
from lib import load_ids, read_remote, read_local, diff


def add_video(youtube, playlist_id, video_id):
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            }
        },
    ).execute()


def delete_video(youtube, playlist_item_id):
    youtube.playlistItems().delete(id=playlist_item_id).execute()


def get_playlist_item_ids(youtube, playlist_id, video_ids):
    """Returns {video_id: playlist_item_id} for the given video_ids."""
    result = {}
    page_token = None

    while len(result) < len(video_ids):
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token,
        ).execute()

        for item in response["items"]:
            vid = item["snippet"]["resourceId"]["videoId"]
            if vid in video_ids:
                result[vid] = item["id"]

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return result


def main():
    parser = argparse.ArgumentParser(description="Push local playlist state to YouTube")
    parser.add_argument("name", help="Playlist name as defined in ids.tsv")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without applying it")
    args = parser.parse_args()

    ids = load_ids()
    if args.name not in ids:
        print(f"Error: '{args.name}' not found in ids.tsv", file=sys.stderr)
        sys.exit(1)

    playlist_id = ids[args.name]
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    remote = read_remote(youtube, playlist_id)
    local = read_local(args.name)

    if not local:
        print("Error: local playlist is empty. Aborting to avoid wiping upstream.", file=sys.stderr)
        sys.exit(1)

    added, deleted = diff(remote, local)

    if not added and not deleted:
        print("Already in sync.", file=sys.stderr)
        return

    print(f"{len(added)} to add, {len(deleted)} to delete", file=sys.stderr)

    if args.dry_run:
        for vid in added:
            print(f"  add    {vid}\t{local[vid]['title']}")
        for vid in deleted:
            print(f"  delete {vid}\t{remote[vid]['title']}")
        return

    for video_id in added:
        add_video(youtube, playlist_id, video_id)
        print(f"  added {video_id}\t{local[video_id]['title']}", file=sys.stderr)

    if deleted:
        item_ids = get_playlist_item_ids(youtube, playlist_id, deleted)
        for video_id in deleted:
            if video_id in item_ids:
                delete_video(youtube, item_ids[video_id])
                print(f"  deleted {video_id}\t{remote[video_id]['title']}", file=sys.stderr)


if __name__ == "__main__":
    main()
