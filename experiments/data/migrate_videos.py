#!/usr/bin/env python3
"""
Migrate videos from /data/alenachao/data/videos into
/data/alenachao/data/otif-dataset/dataset.

For each source folder (e.g. ams/test/*.mp4), copies the videos into the
corresponding dataset folder (e.g. amsterdam/test/video/*.mp4), renaming
from the te00.mp4 / tr00.mp4 / va00.mp4 scheme to 0.mp4, 1.mp4, etc.

The existing video/ folder at the destination is deleted and recreated.
"""

import os
import re
import shutil
from pathlib import Path

SRC_ROOT = Path("/data/alenachao/data/videos")
DST_ROOT = Path("/data/alenachao/data/otif-dataset/dataset")

# Mapping from source folder name -> destination folder name.
# Folders not listed here map to themselves (e.g. caldot1 -> caldot1).
NAME_MAP = {
    "ams": "amsterdam",
    "ams-y05": "amsterdam-y5",
    "ams-y11": "amsterdam-y11",
    "caldot1-y05": "caldot1-y5",
    "caldot1-y11": "caldot1-y11",
    "caldot2-y05": "caldot2-y5",
    "caldot2-y11": "caldot2-y11",
}

# Splits present in the source directories
SPLITS = ["test", "train", "valid"]

# Regex to strip the 2-letter prefix (te, tr, va) and extract the number
VIDEO_RE = re.compile(r"^(?:te|tr|va)(\d+)\.mp4$")


def rename_video(filename: str) -> str | None:
    """Convert e.g. 'te00.mp4' -> '0.mp4', 'tr12.mp4' -> '12.mp4'."""
    m = VIDEO_RE.match(filename)
    if m is None:
        return None
    num = int(m.group(1))  # strips leading zeros
    return f"{num}.mp4"


def process_source(src_name: str) -> None:
    """Process one source folder (e.g. 'ams' or 'caldot1')."""
    src_dir = SRC_ROOT / src_name
    dst_name = NAME_MAP.get(src_name, src_name)
    dst_dir = DST_ROOT / dst_name

    if not dst_dir.exists():
        print(f"  WARNING: destination {dst_dir} does not exist, skipping")
        return

    for split in SPLITS:
        split_src = src_dir / split
        if not split_src.exists():
            continue

        video_dst = dst_dir / split / "video"

        # Delete existing video folder and recreate it
        if video_dst.exists():
            print(f"  Removing existing {video_dst}")
            shutil.rmtree(video_dst)
        video_dst.mkdir(parents=True, exist_ok=True)

        # Copy and rename each video
        count = 0
        for f in sorted(split_src.iterdir()):
            if not f.is_file() or f.suffix != ".mp4":
                continue
            new_name = rename_video(f.name)
            if new_name is None:
                print(f"  WARNING: unexpected filename {f.name}, skipping")
                continue
            dst_path = video_dst / new_name
            shutil.copy2(f, dst_path)
            count += 1

        print(f"  {src_name}/{split} -> {dst_name}/{split}/video : {count} videos copied")


def main():
    # Iterate over every directory/symlink in the source root
    entries = sorted(
        e.name for e in SRC_ROOT.iterdir() if e.is_dir() or e.is_symlink()
    )

    for src_name in entries:
        src_dir = SRC_ROOT / src_name
        # Resolve symlinks – if it points to a directory, process it
        if src_dir.is_symlink():
            target = src_dir.resolve()
            if not target.is_dir():
                continue
        elif not src_dir.is_dir():
            continue

        print(f"Processing: {src_name}")
        process_source(src_name)

    print("\nDone!")


if __name__ == "__main__":
    main()
