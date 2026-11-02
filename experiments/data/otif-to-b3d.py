"""
converts otif-formatted jsonl tracks files in a directory to b3d format
"""

import os
import json


def otif_to_b3d_file(input_file, output_file, gt=False):
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for frame_idx, line in enumerate(infile):
            line = line.strip()
            if not line:
                continue
            detections = json.loads(line)
            tracks = []
            if detections:
                for det in detections:
                    track_id = det["track_id"]
                    x1 = det["left"]
                    y1 = det["top"]
                    x2 = det["right"]
                    y2 = det["bottom"]
                    conf = det["score"]
                    if gt:
                        tracks.append([track_id, x1, y1, x2, y2])
                    else:
                        tracks.append([track_id, x1, y1, x2, y2, 0, conf])

            frame_entry = {"frame_idx": frame_idx, "tracks": tracks}
            outfile.write(json.dumps(frame_entry) + "\n")


def otif_to_b3d_dir(input_dir, output_dir, gt=False):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".jsonl"):
            continue

        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)

        gt = filename == "tracks.jsonl"
        otif_to_b3d_file(input_file, output_file, gt)
        print(f"Converted {input_file} -> {output_file}")

parent_indir = "/data/alenachao/hota/TrackEval/scripts/pipeline-stages/track-results-otif-full-dataset"
parent_outdir = "/data/alenachao/hota/TrackEval/scripts/pipeline-stages/track-results-otif-full-dataset-b3d"

for dir in os.listdir(parent_indir):
    input_dir = os.path.join(parent_indir, dir)
    output_dir = os.path.join(parent_outdir, dir)
    # print(input_dir, output_dir)
    otif_to_b3d_dir(input_dir, output_dir)

