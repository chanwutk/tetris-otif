package lib

import (
	"github.com/mitroadmaps/gomapinfer/common"
	"fmt"
	"io/ioutil"
	_"math"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func GetGoodTracks(label string, detections [][]Detection) [][][]TrackDetection {
	tracks := GetTracks(detections)
	numSegments := 1
	if label == "shibuya" {
		numSegments = 10
	} else if strings.HasPrefix(label, "caldot") || label == "warsaw" {
		numSegments = 2
	} else if label == "uav" {
		numSegments = 8
	} else if label == "jnc0" {
		numSegments = 6
	} else if label == "jnc2" || label == "jnc6" || label == "jnc7" {
		numSegments = 12
	}
	goodTracks := make([][][]TrackDetection, numSegments)
	for _, track := range tracks {
		duration := track[len(track)-1].FrameIdx - track[0].FrameIdx
		distance := track[0].Center().Distance(track[len(track)-1].Center())
		if label == "shibuya" {
			rightPoly := common.Polygon{
				common.Point{820, 275},
				common.Point{1085, 380},
				common.Point{1280, 230},
				common.Point{1280, 0},
				common.Point{820, 0},
			}
			leftPoly := common.Polygon{
				common.Point{334, 363},
				common.Point{0, 434},
				common.Point{0, 720},
				common.Point{660, 710},
			}
			topPoly := common.Polygon{
				common.Point{787, 274},
				common.Point{455, 140},
				common.Point{255, 165},
				common.Point{365, 365},
			}
			bottomPoly := common.Polygon{
				common.Point{1095, 430},
				common.Point{700, 630},
				common.Point{700, 720},
				common.Point{1280, 720},
				common.Point{1280, 430},
			}
			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1
			if leftPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			} else if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 2
			} else if rightPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 3
			} else if rightPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 4
			} else if rightPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 5
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 6
			} else if bottomPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 7
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 8
			} else if topPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 9
			}
			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "warsaw" {
			leftPoly := common.Polygon{
				common.Point{634, 363},
				common.Point{0, 434},
				common.Point{0, 720},
				common.Point{660, 710},
			}
			topPoly := common.Polygon{
				common.Point{562, 401},
				common.Point{505, 138},
				common.Point{983, 296},
				common.Point{1043, 384},
			}
			bottomPoly := common.Polygon{
				common.Point{1280, 420},
				common.Point{867, 471},
				common.Point{1127, 720},
				common.Point{1280, 720},
			}
			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1
			if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 0
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 1
			}
			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "uav" {
			rightPoly := common.Polygon{
				common.Point{488, 117},
				common.Point{480, 287},
				common.Point{1280, 445},
				common.Point{1280, 280},
			}
			leftPoly := common.Polygon{
				common.Point{295, 66},
				common.Point{0, 0},
				common.Point{0, 171},
				common.Point{298, 231},
			}
			topPoly := common.Polygon{
				common.Point{296, 65},
				common.Point{478, 102},
				common.Point{478, 0},
				common.Point{283, 0},
			}
			bottomPoly := common.Polygon{
				common.Point{314, 252},
				common.Point{475, 299},
				common.Point{395, 720},
				common.Point{242, 720},
			}
			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1
			if leftPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 1
			} else if rightPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 2
			} else if rightPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 3
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 4
			} else if bottomPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 5
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 6
			} else if topPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 7
			}
			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "caldot1" || label == "caldot1-mota" || label == "caldot1-y5" || label == "caldot1-y11" {
			topPoly := common.Polygon{
				common.Point{458, 344},
				common.Point{598, 138},
				common.Point{289, 136},
				common.Point{391, 298},
			}
			bottomPoly := common.Polygon{
				common.Point{448, 369},
				common.Point{392, 480},
				common.Point{0, 480},
				common.Point{0, 37},
			}
			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1
			if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 0
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			}
			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "caldot2" || label == "caldot2-y5" || label == "caldot2-y11"{
			topPoly := common.Polygon{
				common.Point{334, 344},
				common.Point{588, 167},
				common.Point{100, 167},
				common.Point{104, 297},
			}
			bottomPoly := common.Polygon{
				common.Point{322, 363},
				common.Point{0, 288},
				common.Point{0, 480},
				common.Point{322, 480},
			}
			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}

			segment := -1
			if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 0
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			}
			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "jnc0" {
			leftPoly := common.Polygon{
				common.Point{300, 406},
				common.Point{300, 100},
				common.Point{0, 94},
				common.Point{0, 350},
			}

			rightTopPoly := common.Polygon{
				common.Point{1080, 0},
				common.Point{780, 0},
				common.Point{800, 230},
				common.Point{1080, 155},
			}

			rightBotPoly := common.Polygon{
				common.Point{1080, 500},
				common.Point{815, 380},
				common.Point{740, 590},
				common.Point{1080, 720},
			}

			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}

			segment := -1
			if leftPoly.Contains(p0) && rightTopPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && rightBotPoly.Contains(p1) {
				segment = 1
			} else if rightTopPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 2
			} else if rightBotPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 3
			} else if rightTopPoly.Contains(p0) && rightBotPoly.Contains(p1) {
				segment = 4
			} else if rightBotPoly.Contains(p0) && rightTopPoly.Contains(p1) {
				segment = 5
			}

			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}
		} else if label == "jnc2" {
			leftPoly := common.Polygon{
				common.Point{250, 490},
				common.Point{250, 300},
				common.Point{0, 300},
				common.Point{0, 475},
			}
			topPoly := common.Polygon{
				common.Point{680, 0},
				common.Point{380, 0},
				common.Point{370, 230},
				common.Point{680, 155},
			}
			rightPoly := common.Polygon{
				common.Point{1080, 275},
				common.Point{815, 260},
				common.Point{815, 540},
				common.Point{1080, 525},
			}
			bottomPoly := common.Polygon{
				common.Point{750, 600},
				common.Point{300, 600},
				common.Point{370, 720},
				common.Point{680, 720},
			}

			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1

			if leftPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			} else if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 2
			} else if rightPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 3
			} else if rightPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 4
			} else if rightPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 5
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 6
			} else if topPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 7
			} else if topPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 8
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 9
			} else if bottomPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 10
			} else if bottomPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 11
			}

			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}

		} else if label == "jnc6" {
			leftPoly := common.Polygon{
				common.Point{250, 490},
				common.Point{250, 100},
				common.Point{0, 100},
				common.Point{0, 475},
			}
			topPoly := common.Polygon{
				common.Point{750, 0},
				common.Point{420, 0},
				common.Point{420, 75},
				common.Point{750, 75},
			}
			rightPoly := common.Polygon{
				common.Point{1080, 100},
				common.Point{815, 100},
				common.Point{815, 540},
				common.Point{1080, 545},
			}
			bottomPoly := common.Polygon{
				common.Point{750, 600},
				common.Point{300, 600},
				common.Point{340, 720},
				common.Point{680, 720},
			}

			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1

			if leftPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			} else if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 2
			} else if rightPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 3
			} else if rightPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 4
			} else if rightPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 5
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 6
			} else if topPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 7
			} else if topPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 8
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 9
			} else if bottomPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 10
			} else if bottomPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 11
			}

			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}

		} else if label == "jnc7" {
			leftPoly := common.Polygon{
				common.Point{320, 430},
				common.Point{320, 230},
				common.Point{0, 260},
				common.Point{0, 400},
			}
			topPoly := common.Polygon{
				common.Point{810, 0},
				common.Point{360, 0},
				common.Point{360, 150},
				common.Point{810, 150},
			}
			rightPoly := common.Polygon{
				common.Point{1080, 230},
				common.Point{815, 230},
				common.Point{815, 520},
				common.Point{1080, 515},
			}
			bottomPoly := common.Polygon{
				common.Point{800, 600},
				common.Point{300, 600},
				common.Point{340, 720},
				common.Point{800, 720},
			}

			p0_ := track[0].Center()
			p1_ := track[len(track)-1].Center()
			p0 := common.Point{float64(p0_.X), float64(p0_.Y)}
			p1 := common.Point{float64(p1_.X), float64(p1_.Y)}
			segment := -1

			if leftPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 0
			} else if leftPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 1
			} else if leftPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 2
			} else if rightPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 3
			} else if rightPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 4
			} else if rightPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 5
			} else if topPoly.Contains(p0) && bottomPoly.Contains(p1) {
				segment = 6
			} else if topPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 7
			} else if topPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 8
			} else if bottomPoly.Contains(p0) && topPoly.Contains(p1) {
				segment = 9
			} else if bottomPoly.Contains(p0) && leftPoly.Contains(p1) {
				segment = 10
			} else if bottomPoly.Contains(p0) && rightPoly.Contains(p1) {
				segment = 11
			}

			if segment >= 0 {
				goodTracks[segment] = append(goodTracks[segment], track)
			}

		} else {
			if (label == "amsterdam" || label == "amsterdam-y5" || label == "amsterdam-y11" || label == "jackson") && (duration < 10 || distance < 50) {
				continue
			}
			if label == "taipei" && duration < 30 {
				continue
			}
			goodTracks[0] = append(goodTracks[0], track)
		}
	}
	return goodTracks
}

func Eval(dataRoot string, cfg Config, validtest string, path string) (float64, float64) {
	if cfg.Label == "caldot1-mota" && validtest == "test" {
		return EvalMOTA(dataRoot, cfg, validtest, path)
	}

	gtFname := filepath.Join(dataRoot, "dataset", cfg.Label, validtest, "gt.txt")
	gtCounts := make(map[int][]int)
	bytes, err := ioutil.ReadFile(gtFname)
	if err != nil {
		panic(err)
	}
	for _, line := range strings.Split(string(bytes), "\n") {
		parts := strings.Split(strings.TrimSpace(line), "\t")
		if len(parts) < 2 || parts[0] == "#" {
			continue
		}
		id := ParseInt(parts[0])
		var counts []int
		for _, part := range parts[1:] {
			counts = append(counts, ParseInt(part))
		}
		gtCounts[id] = counts
	}

	var accs []float64
	for id := range gtCounts {
		var detections [][]Detection

		// WE DONT CARE ABOUT OTIF ACC
		filePath := fmt.Sprintf("%s/%d.json", path, id)
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			fmt.Println("Warning: file not found, setting accuracy to 0:", filePath)
			accs = append(accs, 0)
			continue
		}

		ReadJsonFile(filePath, &detections)
		// fmt.Println(detections)
		goodTracks := GetGoodTracks(cfg.Label, detections)
		counts := make([]int, len(goodTracks))
		for segment := range goodTracks {
			counts[segment] = len(goodTracks[segment])
		}
		fmt.Println(id, "inferred", counts)
		fmt.Println(id, "gt", gtCounts[id])

		var curAccs []float64

		allZero := true
		for _, c := range counts {
			if c != 0 {
				allZero = false
				break
			}
		}

		if allZero {
			curAccs = append(curAccs, 0.0)
		} else {
			for segment := range gtCounts[id] {
				count1 := counts[segment]
				count2 := gtCounts[id][segment]
				var acc float64
				//acc = 100-math.Abs(float64(count1-count2))
				if count1 == count2 {
					acc = 1
				} else if count1 == 0 || count2 == 0 {
					acc = 0
				} else {
					// acc = 1 - math.Abs(float64(count1) - float64(count2)) / float64(count2)
					acc = float64(min(count1, count2)) / float64(max(count1, count2))
					// acc = 2 * float64(min(count1, count2)) / float64(count1 + count2)
				}
				curAccs = append(curAccs, acc)
			}
		}
		accs = append(accs, FloatsMean(curAccs))
	}

	// return mean and stderr accuracy
	return FloatsMean(accs), FloatsStderr(accs)
}

// for chameleon-orig, compute accuracy of inferred detections with 50% IOU threshold
func EvalDetection(dataRoot string, cfg Config, validtest string, path string) (float64, float64) {
	isMatch := func(d1 Detection, d2 Detection) bool {
		return d1.Rectangle().IOU(d2.Rectangle()) > 0.5
	}
	getF1 := func(inferred []Detection, gt []Detection) float64 {
		if len(inferred) == 0 && len(gt) == 0 {
			return 1
		} else if len(inferred) == 0 || len(gt) == 0 {
			return 0
		}

		var matches int
		gtSeen := make(map[int]bool)
		for _, d1 := range inferred {
			for j, d2 := range gt {
				if gtSeen[j] {
					continue
				}
				if !isMatch(d1, d2) {
					continue
				}
				gtSeen[j] = true
				matches++
				break
			}
		}

		if matches == 0 {
			return 0
		}
		precision := float64(matches)/float64(len(inferred))
		recall := float64(matches)/float64(len(gt))
		return 2*precision*recall/(precision+recall)
	}

	// find best detector to use as ground truth
	var bestDetectorCfg DetectorConfig
	parentDir := filepath.Join(dataRoot, "dataset", cfg.Label, validtest)
	files, err := ioutil.ReadDir(parentDir)
	if err != nil {
		panic(err)
	}
	for _, fi := range files {
		dir := fi.Name()
		if _, err := os.Stat(parentDir+dir+"/speed.txt"); err != nil {
			continue
		}
		detectorCfg := ParseDetectorConfig(cfg, dir)
		if detectorCfg.Dims[0] > bestDetectorCfg.Dims[0] {
			bestDetectorCfg = detectorCfg
		}
	}

	gtPath := parentDir + bestDetectorCfg.Dir() + "/"
	files, err = ioutil.ReadDir(gtPath)
	if err != nil {
		panic(err)
	}
	var accs []float64
	for _, fi := range files {
		if !strings.HasSuffix(fi.Name(), ".json") {
			continue
		}
		var inferred [][]Detection
		var gt [][]Detection
		ReadJsonFile(path+fi.Name(), &inferred)
		ReadJsonFile(gtPath+fi.Name(), &gt)
		gt = FilterDetectionsByClass(gt, cfg.Classes)

		// - ideally we would just be able to average F1 score on each frame.
		// - but we might have detected objects at a lower framerate, in which
		//   case we would be missing detections on intermediate frames.
		// - and we don't have a good way to distinguish missing detections from
		//   not detecting anything.
		// - so we try both the last non-empty inferred dlist and the current
		//   dlist and use whichever yields highest score
		var lastInferred []Detection
		for i := 0; i < len(gt); i++ {
			if len(inferred[i]) > 0 {
				lastInferred = inferred[i]
			}
			acc1 := getF1(inferred[i], gt[i])
			acc2 := getF1(lastInferred, gt[i])
			if acc1 > acc2 {
				accs = append(accs, acc1)
			} else {
				accs = append(accs, acc2)
			}
		}
	}

	var sum float64
	for _, acc := range accs {
		sum += acc
	}
	return sum/float64(len(accs)), 0
}

func EvalMOTA(dataRoot string, cfg Config, validtest string, path string) (float64, float64) {
	getMOTA := func(fname1 string, fname2 string) float64 {
		cmd := exec.Command("python", "../data-scripts/compute-mota.py", fname1, fname2, "16")
		bytes, err := cmd.CombinedOutput()
		fmt.Println(string(bytes))
		if err != nil {
			panic(err)
		}
		var acc float64
		for _, line := range strings.Split(string(bytes), "\n") {
			parts := strings.Fields(line)
			if parts[0] == "acc" {
				acc, _ = strconv.ParseFloat(parts[1], 64)
				break
			}
		}
		return acc
	}

	var accs []float64
	for _, idx := range []int{3, 7, 8} {
		fname1 := path+fmt.Sprintf("%d.json", idx)
		fname2 := filepath.Join(dataRoot, "dataset", cfg.Label, validtest+"-mota", fmt.Sprintf("%d.json", idx))
		acc := getMOTA(fname1, fname2)
		accs = append(accs, acc)
	}
	return FloatsMean(accs), FloatsStderr(accs)
}
