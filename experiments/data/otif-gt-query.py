"""
given gt tracks for otif b3d, get counts of motion patterns as would be compared to in eval
"""
import json
import numpy as np
import cv2
from pathlib import Path

JNC0_CONFIG = {
    "left": np.array([
        [300, 406],
        [300, 100],
        [0, 94],
        [0, 350],
    ], dtype=np.int32),
    "rightTop": np.array([
        [1080, 0],
        [780, 0],
        [800, 230],
        [1080, 155],
    ], dtype=np.int32),
    "rightBottom": np.array([
        [1080, 500],
        [815, 380],
        [740, 590],
        [1080, 720],
    ], dtype=np.int32)
}

JNC2_CONFIG = {
    "left": np.array([
        [250, 490],
        [250, 300],
        [0, 300],
        [0, 475],
    ], dtype=np.int32),
    "top": np.array([
        [680, 0],
        [380, 0],
        [370, 230],
        [680, 155],
    ], dtype=np.int32),
    "right": np.array([
        [1080, 275],
        [815, 260],
        [815, 540],
        [1080, 525],
    ], dtype=np.int32),
    "bottom": np.array([
        [750, 600],
        [300, 600],
        [370, 720],
        [680, 720],
    ], dtype=np.int32)
}

JNC6_CONFIG = {
    "left": np.array([
        [250, 490],
        [250, 100],
        [0, 100],
        [0, 475],
    ], dtype=np.int32),
    "top": np.array([
        [750, 0],
        [420, 0],
        [420, 75],
        [750, 75],
    ], dtype=np.int32),
    "right": np.array([
        [1080, 100],
        [815, 100],
        [815, 540],
        [1080, 545],
    ], dtype=np.int32),
    "bottom": np.array([
        [750, 600],
        [300, 600],
        [340, 720],
        [680, 720],
    ], dtype=np.int32)
}

JNC7_CONFIG = {
    "left": np.array([
        [320, 430],
        [320, 230],
        [0, 260],
        [0, 400],
    ], dtype=np.int32),
    "top": np.array([
        [810, 0],
        [360, 0],
        [360, 150],
        [810, 150],
    ], dtype=np.int32),
    "right": np.array([
        [1080, 230],
        [815, 230],
        [815, 520],
        [1080, 515],
    ], dtype=np.int32),
    "bottom": np.array([
        [800, 600],
        [300, 600],
        [340, 720],
        [800, 720],
    ], dtype=np.int32)
}

AMS_CONFIG = {
    "right": np.array([
        [1600, 300],
        [1000, 300],
        [1000, 720],
        [1600, 720],
    ], dtype=np.int32),
    "bottom": np.array([
        [800, 500],
        [300, 500],
        [300, 900],
        [800, 900],
    ], dtype=np.int32),
}



def point_in_poly(point, poly):
    """Check if (x, y) is inside polygon (NumPy array)."""
    return cv2.pointPolygonTest(poly, (float(point[0]), float(point[1])), False) >= 0


def get_region(point, regions):
    """Return the region name containing this point, or None."""
    for name, poly in regions.items():
        if point_in_poly(point, poly):
            return name
    return None


def process_tracks(json_path, regions):
    """Given a JSON of tracks and region config, count all region-to-region transitions."""
    with open(json_path, "r") as f:
        tracks = json.load(f)

    region_names = list(regions.keys())
    # dynamically construct all possible pairs
    counts = {f"{a}_{b}": 0 for a in region_names for b in region_names if a != b}

    for track in tracks:
        if not track:
            continue

        start_det = track[0]
        end_det = track[-1]

        x0 = (start_det["left"] + start_det["right"]) / 2
        y0 = (start_det["top"] + start_det["bottom"]) / 2
        x1 = (end_det["left"] + end_det["right"]) / 2
        y1 = (end_det["top"] + end_det["bottom"]) / 2

        start_region = get_region((x0, y0), regions)
        end_region = get_region((x1, y1), regions)

        if start_region and end_region and start_region != end_region:
            key = f"{start_region}_{end_region}"
            if key in counts:
                counts[key] += 1

    return counts



def main(tracks_dir, output_txt, regions):
    """Iterate over all JSONs in a directory and write counts.txt"""
    json_files = sorted(Path(tracks_dir).glob("*.json"))
    region_names = list(regions.keys())
    pair_names = [f"{a}_{b}" for a in region_names for b in region_names if a != b]

    with open(output_txt, "w") as f:
        f.write("#\t" + "\t".join(pair_names) + "\n")
        for jf in json_files:
            counts = process_tracks(jf, regions)
            file_id = jf.stem  # filename without extension
            f.write(f"{file_id}\t" + "\t".join(str(counts[p]) for p in pair_names) + "\n")

    print(f"Wrote results to {output_txt}")

tracks_dir = "/data/alenachao/data/otif-dataset/dataset/amsterdam-y5/validation/tracks"
output_path = "/data/alenachao/data/otif-dataset/dataset/amsterdam/test/gt.txt"
main(tracks_dir, output_path, AMS_CONFIG)
