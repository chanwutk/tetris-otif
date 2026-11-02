# Environments of the Tetris runs

These files are exported from the image the Tetris baseline runs used,
`bombe-revision-otif:scored-env` (`sha256:350221799df1`).
That image is a snapshot of the exited container the scored OTIF runs ran in,
whose base image was built from `Dockerfile` on 2026-03-12 (`sha256:2a8ab48a34fe`).

- OS: Ubuntu 22.04.5, CUDA 12.8, Go 1.18.1.
- `base` (`/usr/local`): Python 3.7.10, TensorFlow 1.15.5, numpy 1.18.5; OTIF's segmentation proxy and RNN tracker.
- `retinanet`: Python 3.13.12, torch 2.6.0+cu124,
  detectron2 at `fd27788985af0f4ca800bca563acdb700bb890e2`; the YOLOv5 and RetinaNet detectors.

Files per env:

- `<env>.explicit.txt`: `conda list --explicit`, the exact conda packages.
- `<env>.conda.yml`: `conda env export`, conda and pip packages with versions.
- `<env>.pip.txt`: `pip freeze`.
  Lines with `@ file:///...` point at conda build artifacts and are installed by the conda lists instead.

Go: `pipeline2/` builds with its `go.mod`.
`pipeline/iou-tracker.go`, which `pipeline/16_extract_frames.py` runs, has no `go.mod`
and imports `github.com/cpmech/gosl`, which the image does not have.
`experiments/setup_gopath.sh` builds the GOPATH the Tetris runs used.
