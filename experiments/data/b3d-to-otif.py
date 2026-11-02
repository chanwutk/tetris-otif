import json
import argparse

def b3d_to_otif(input_file, output_file):
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            frame_data = json.loads(line)
            tracks = frame_data["tracks"]

            if not tracks:  # no detections
                outfile.write("null\n")
            else:
                detections = []
                for track in tracks:
                    track_id, x1, y1, x2, y2, conf = track
                    det = {
                        "left": x1,
                        "top": y1,
                        "right": x2,
                        "bottom": y2,
                        "class": "car", # TODO: might need to change
                        "score": conf,
                        "track_id": track_id
                    }
                    detections.append(det)
                outfile.write(json.dumps(detections) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert b3d JSONL outputs to OTIF JSONL format")
    parser.add_argument("input_file", help="Input OTIF JSONL file")
    parser.add_argument("output_file", help="Output JSONL file")
    args = parser.parse_args()

    b3d_to_otif(args.input_file, args.output_file)

