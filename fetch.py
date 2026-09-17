import sys
import argparse
from auth import get_credentials
from googleapiclient.discovery import build
from lib import load_ids, read_remote, read_local, diff, PLAYLISTS_DIR


def write_local(name, videos):
    path = f"{PLAYLISTS_DIR}/{name}.tsv"
    with open(path, "w") as f:
        for v in videos.values():
            f.write(f"{v['url']}\t{v['availability']}\t{v['title']}\n")
    return path


def main():
    parser = argparse.ArgumentParser(description="Fetch a YouTube playlist")
    parser.add_argument("name", help="Playlist name as defined in ids.tsv")
    parser.add_argument("--preview", action="store_true", help="Print to stdout instead of writing to file")
    args = parser.parse_args()

    ids = load_ids()
    if args.name not in ids:
        print(f"Error: '{args.name}' not found in ids.tsv", file=sys.stderr)
        sys.exit(1)

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    remote = read_remote(youtube, ids[args.name])
    local = read_local(args.name)
    added, deleted = diff(local, remote)

    if added or deleted:
        print(f"{len(added)} added, {len(deleted)} deleted", file=sys.stderr)

    if args.preview:
        for v in remote.values():
            sys.stdout.write(f"{v['url']}\t{v['availability']}\t{v['title']}\n")
    else:
        path = write_local(args.name, remote)
        print(f"Saved {len(remote)} videos to {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
