#!/bin/bash
# Build the GOPATH that pipeline/iou-tracker.go needs, as in Tetris's runs.
# pipeline/ has no go.mod and imports github.com/cpmech/gosl, so it builds in GOPATH mode against
# the module versions pipeline2/go.mod pins plus gosl v1.1.0 (cgo off, which drops only gosl's METIS
# partitioning, unused by iou-tracker.go). Without it, pipeline/16_extract_frames.py's tracking call
# fails and that step keeps no training frames.
# Usage (inside the OTIF container, repo at /otif): experiments/setup_gopath.sh [GOPATH_DIR]
set -euo pipefail
OTIF=$(cd "$(dirname "$0")/.." && pwd)
GOPATH_DIR=${1:-$OTIF/.gopath}
MODULES=(
  github.com/mitroadmaps/gomapinfer@v0.0.0-20210917033103-4e3dcc98a112
  github.com/ajstarks/svgo@v0.0.0-20211024235047-1546f124cd8b
  github.com/dhconnelly/rtreego@v1.1.0
  github.com/qedus/osmpbf@v1.2.0
  google.golang.org/protobuf@v1.26.0
)
# Fetch pipeline2/go.mod's pinned modules into the module cache.
(cd "$OTIF/pipeline2" && go mod download)
CACHE=$(go env GOMODCACHE)
rm -rf "$GOPATH_DIR/src"
for module in "${MODULES[@]}"; do
  mkdir -p "$GOPATH_DIR/src/${module%@*}"
  cp -r "$CACHE/$module/." "$GOPATH_DIR/src/${module%@*}/"
done
git clone -q --depth 1 --branch v1.1.0 https://github.com/cpmech/gosl "$GOPATH_DIR/src/github.com/cpmech/gosl"
chmod -R u+w "$GOPATH_DIR"
cd "$OTIF/pipeline"
GO111MODULE=off GOFLAGS= CGO_ENABLED=0 GOPATH="$GOPATH_DIR" go build -o /dev/null iou-tracker.go
echo "export GO111MODULE=off GOFLAGS= CGO_ENABLED=0 GOPATH=$GOPATH_DIR"
