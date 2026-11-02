# Running OTIF as in Tetris

This branch is the OTIF code Tetris compares against (Bastani and Madden, SIGMOD 2022),
with the YOLOv5 and B3D RetinaNet detectors and the changes Tetris's runs used.
`README.md` is OTIF's own documentation; this file lists what Tetris ran and how.

## What is here

- OTIF's code as run: see the commit "add the code as run for the Tetris experiments".
- `env/`: the exact conda and pip environments, OS, CUDA, and Go versions (`env/README.md`).
- `experiments/setup_gopath.sh`: the GOPATH `pipeline/iou-tracker.go` needs.
- `experiments/data/`, `experiments/eval/`: dataset conversion and result export scripts (paths inside are hard-coded to
  the machine they ran on; edit them before use).

Not here: videos, labels, and detector weights.
The data root (`OTIF_DATA`) follows OTIF's layout, `dataset/<label>/{train,valid,test}/video/N.mp4`, with Tetris's
clips renamed from `teNN/trNN/vaNN.mp4` to `N.mp4` (`experiments/data/migrate_videos.py`).
YOLOv5 weights are Tetris's fine-tuned detectors at `$OTIF_DATA/yolov5/<label>/best.pt`.
The B3D RetinaNet model is described by `$OTIF_DATA/retinanet/b3d/config_refined.json` (config name, weights path,
classes, score threshold), and `pipeline2/retinanet.py` reads detectron2's model configs from `python/detectron2`.

## Setup

```sh
git clone https://github.com/facebookresearch/detectron2.git python/detectron2
git -C python/detectron2 checkout fd27788985af0f4ca800bca563acdb700bb890e2
git submodule update --init python/darknet
export OTIF_DATA=/path/to/otif-dataset
docker compose up -d --build        # or the image in env/README.md
docker exec -it otif bash
cd /otif && eval "$(experiments/setup_gopath.sh /tmp/gopath | tail -1)"   # for step 3 only
```

## Datasets and parameters

| Tetris dataset | OTIF label | Detector | Tracker thresholds |
| --- | --- | --- | --- |
| CalDoT1 | `caldot1-y5` | `yolov5-704x480` | `{"Thresholds":[0,1,1,1,1,1,1]}` |
| CalDoT2 | `caldot2-y5` | `yolov5-704x480` | same |
| Amsterdam | `amsterdam-y5` | `yolov5-704x480` | same (OTIF's README has `[0,0,1,...]`) |
| B3D1-4 | `jnc0`, `jnc2`, `jnc6`, `jnc7` | `retinanet-1080x720` | same |

Validation tuning starts from the segmentation proxy `640_352_-1` (OTIF's README starts from `416_256_-1`)
and runs 10 iterations.
These come from the shell history of the container the scored runs used.

## Preparation (per dataset; `L` = label, `D` = detector, `T` = thresholds)

```sh
D_DIMS=${D##*-}; DATA=/path/to/otif-dataset/dataset/$L
# 1. Reference detection of the training split
cd /otif/pipeline2 && go run 10_detect.go /path/to/otif-dataset/ $L $DATA/train/video/ $DATA/train/$D/ $D_DIMS
# 2. IoU tracks of the training detections
mkdir -p $DATA/train/tracks && go run iou-tracker2.go /path/to/otif-dataset/ $L $DATA/train/video/ $DATA/train/$D/ $DATA/train/tracks/ iou '' "$T"
# 3. Frames for the segmentation proxy (needs the GOPATH from Setup)
cd /otif/pipeline && python 16_extract_frames.py /path/to/otif-dataset/ $L $D
# 4. Segmentation proxy
python 20_train_segmentation.py /path/to/otif-dataset/ $L car
# 5. RNN tracker (this fork's rnn/train.py reads train/tracks)
cd /otif/rnn && python train.py /path/to/otif-dataset/ $L
# 6. Reference detection of the validation split
cd /otif/pipeline2 && go run 10_detect.go /path/to/otif-dataset/ $L $DATA/valid/video/ $DATA/valid/$D/ $D_DIMS
# 7. Validation tuning: the speed-accuracy curve of configurations
go run 30_speed_accuracy.go /path/to/otif-dataset/ $L ours-simple $D 640_352_-1 "$T" 10 outputs/$L-valid-ours-simple.txt
```

Without step 3's GOPATH, `16_extract_frames.py`'s tracking call fails silently and keeps no training frames;
the scored runs then fell back to tracks left over from OTIF's own dataset copy.
Tetris's preparation-cost measurement reran steps 1-7 with the GOPATH in place.

## Extraction on the test split

```sh
cd /otif/pipeline2
go build -o eval 40_evaltest.go
./eval /path/to/otif-dataset/ $L ours-simple outputs/$L-valid-ours-simple.txt outputs/$L-test-ours-simple.txt
```

`outputs/$L-test-ours-simple.txt` lists each tuned configuration's runtime and accuracy on the test split.
`experiments/eval/export-hota-outputs.ipynb` turns it into the per-configuration CSV Tetris reports,
and `experiments/eval/otif-to-trackeval2.py` converts the tracks for TrackEval.
Tetris's harness (`measurements-gpu/r1o2_leap_otif_rerun.py` in the tetris repo) runs these steps under GNU time
in a pinned container per step.
