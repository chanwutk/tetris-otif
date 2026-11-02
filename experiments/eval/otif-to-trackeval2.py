"""
output OTIF HOTA dataset but output dir format
|-- input dir (ex: /data/alenachao/hota/TrackEval/scripts/pipeline-stages/track-results-otif-full-dataset)
    |-- 1 # video 1
        |-- 0.jsonl # param 0
        |-- 1.jsonl
        ...
        |-- tracks.jsonl # gt
    |-- 2
        |-- 0.jsonl
        |-- 1.jsonl
        ...
        |-- tracks.jsonl
"""


import os
import json
import argparse

def convert_json_to_jsonl_by_video(input_dir, output_dir, gt_dir):
    os.makedirs(output_dir, exist_ok=True)

    # List of parameter folders
    param_folders = sorted([f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))])
    if not param_folders:
        print("No parameter folders found in input directory.")
        return

    # Assume all parameter folders have the same number of videos
    video_names = [
        os.path.splitext(f)[0]
        for f in os.listdir(gt_dir)
    ]
    print(video_names)

    for video_name in video_names:
        video_folder = os.path.join(output_dir, f"{video_name}")
        os.makedirs(video_folder, exist_ok=True)

        # Convert parameter outputs
        for param_name in param_folders:
            param_folder_path = os.path.join(input_dir, param_name)
            json_filename = f"{video_name}.json"
            json_path = os.path.join(param_folder_path, json_filename)

            if not os.path.exists(json_path):
                print(f"Warning: {json_path} does not exist, skipping.")
                continue

            output_file = os.path.join(video_folder, f"{param_name}.jsonl")
            with open(json_path, "r") as infile, open(output_file, "w") as outfile:
                data = json.load(infile)
                if data is None:
                    data = [None]
                for elem in data:
                    outfile.write(json.dumps(elem) + "\n")

        # load gt
        gt_file_path = os.path.join(gt_dir, str(video_name) + ".json")
        gt_output_file = os.path.join(video_folder, "tracks.jsonl")
        with open(gt_file_path, "r") as infile, open(gt_output_file, "w") as outfile:
            data = json.load(infile)
            if data is None:
                data = [None]
            for elem in data:
                outfile.write(json.dumps(elem) + "\n")

        print(f"Video {video_name} JSONL files saved to {video_folder}")

    print("Conversion complete.")



input_dir = "/data/alenachao/otif/pipeline2/outputs/caldot2/ours-simple"
output_dir = "/data/alenachao/TrackEval/scripts/pipeline-stages/track-results-otif-caldot2"
gt_dir = "/data/alenachao/data/otif-dataset/dataset/caldot2/test/tracks"
convert_json_to_jsonl_by_video(input_dir, output_dir, gt_dir)