package main

import (
	"pipeline2/lib"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
)

type Configs struct {
	Detector lib.DetectorConfig
	Segmentation lib.SegmentationConfig
	Tracker lib.TrackerConfig
}

func main() {
	dataRoot := os.Args[1]
	label := os.Args[2]
	mode := os.Args[3]
	validfile := os.Args[4]
	logfile := os.Args[5]
	videoPath := ""
	outRoot := ""
    if len(os.Args) > 7 {
        videoPath = os.Args[6]
		outRoot = os.Args[7]
    }

	// fmt.Println("videoPath:", videoPath) // TODO: delete after testing

	cfg := lib.GetConfig(dataRoot, label)
	opts := lib.GetExecOptions(mode, true)

	bytes, err := ioutil.ReadFile(validfile)
	if err != nil {
		panic(err)
	}
	for i, line := range strings.Split(string(bytes), "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		parts := strings.Split(line, "\t")
		detectCfg := lib.ParseDetectorConfig(cfg, parts[0])
		segmentCfg := lib.ParseSegmentationConfig(parts[1])
		trackerCfg := lib.ParseTrackerConfig(parts[2])
		validAcc, _ := strconv.ParseFloat(parts[5], 64)

		// create directory where output tracks will be stored
		if outRoot == "" {
			outRoot = fmt.Sprintf("./outputs/%s/%s", label, mode)
		}
		outDir := fmt.Sprintf("%s/%d", outRoot, i)
		os.MkdirAll(outDir, 0755)

		t, acc, stderr, segTime, detectTime, trackTime, decodeTime := lib.Exec2(dataRoot, cfg, "test", outDir, detectCfg, segmentCfg, trackerCfg, opts, videoPath)

		logStr := fmt.Sprintf("%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v", detectCfg, segmentCfg, trackerCfg, t, segTime, detectTime, trackTime, decodeTime, validAcc, acc, stderr)
		fmt.Println(logStr)
		file, err := os.OpenFile(logfile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			panic(err)
		}
		if _, err := file.Write([]byte(logStr+"\n")); err != nil {
			panic(err)
		}
		file.Close()
	}
}
