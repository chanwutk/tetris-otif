import json
import os
import sys
import typing

import numpy as np
import torch
from torch.nn.functional import interpolate

if typing.TYPE_CHECKING:
    from detectron2.modeling.meta_arch.retinanet import RetinaNet

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor

# TODO: hardcode config for now
CONFIG = os.path.join('/path/to/otif-dataset/retinanet/b3d/config_refined.json')
DETECTRON_CONFIG_DIR = '/otif/python/detectron2/configs'

# FROM: from b3d.external import nms
def nms(bounding_boxes, confidence_scores, threshold):
    # https://github.com/amusi/Non-Maximum-Suppression/blob/master/nms.py
    # If no bounding boxes, return empty list
    if len(bounding_boxes) == 0:
        return [], []

    # Bounding boxes
    boxes = np.array(bounding_boxes)

    # coordinates of bounding boxes
    start_x = boxes[:, 0]
    start_y = boxes[:, 1]
    end_x = boxes[:, 2]
    end_y = boxes[:, 3]

    # Confidence scores of bounding boxes
    score = np.array(confidence_scores)

    # Picked bounding boxes
    picked_boxes = []
    picked_scores = []

    # Compute areas of bounding boxes
    areas = (end_x - start_x + 1) * (end_y - start_y + 1)

    # Sort by confidence score of bounding boxes
    order = np.argsort(score)

    # Iterate bounding boxes
    while order.size > 0:
        # The index of largest confidence score
        index = order[-1]

        # Pick the bounding box with largest confidence score
        picked_boxes.append(bounding_boxes[index])
        picked_scores.append(confidence_scores[index])

        # Compute ordinates of intersection-over-union(IOU)
        x1 = np.maximum(start_x[index], start_x[order[:-1]])
        x2 = np.minimum(end_x[index], end_x[order[:-1]])
        y1 = np.maximum(start_y[index], start_y[order[:-1]])
        y2 = np.minimum(end_y[index], end_y[order[:-1]])

        # Compute areas of intersection-over-union
        w = np.maximum(0.0, x2 - x1 + 1)
        h = np.maximum(0.0, y2 - y1 + 1)
        intersection = w * h

        # Compute the ratio between intersection and union
        ratio = intersection / (areas[index] + areas[order[:-1]] - intersection)

        left = np.where(ratio < threshold)
        order = order[left]

    return picked_boxes, picked_scores

# FROM: from b3d.utils import parse_outputs
def parse_outputs(outputs, offset):
    instances = outputs['instances'].to('cpu')
    bboxes = []
    scores = []
    classes = []
    for bbox, score, pred_class in zip(
            instances.pred_boxes, instances.scores, instances.pred_classes):
        bbox[0] += offset[0]
        bbox[1] += offset[1]
        bbox[2] += offset[0]
        bbox[3] += offset[1]
        bboxes.append(bbox.numpy())
        scores.append(score.numpy())
        classes.append(pred_class.numpy())
    return bboxes, scores, classes


def get_detector(device: str, configfile: typing.Optional[str] = None) -> "DefaultPredictor":
    with open(configfile or CONFIG) as fp:
        config = json.load(fp)

    cfg = get_cfg()
    cfg.merge_from_file(os.path.join(DETECTRON_CONFIG_DIR, config['config']))
    cfg.MODEL.WEIGHTS = config['weights']
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = config['num_classes']
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config['score_threshold']
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = config['score_threshold']
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = config['nms_threshold']
    cfg.MODEL.RETINANET.NMS_THRESH_TEST = config['nms_threshold']
    cfg.TEST.DETECTIONS_PER_IMAGE = config['detections_per_image']
    cfg.MODEL.ANCHOR_GENERATOR.SIZES = config['anchor_generator_sizes']
    cfg.MODEL.DEVICE = device

    return DefaultPredictor(cfg)


# def detect(
#     image: np.ndarray,
#     detector: "DefaultPredictor",
#     nms_threshold: float = 0.5
# ) -> polyis.dtypes.DetArray:
#     """
#     Detect vehicles in an image using RetinaNet.
    
#     Args:
#         image: Input image as numpy array (H, W, C)
#         detector: RetinaNet detector instance
#         nms_threshold: NMS threshold
        
#     Returns:
#         np.ndarray: Detection results as array of shape (N, 5)
#                     where each row is [x1, y1, x2, y2, confidence]
#     """
#     detections = detect_batch([image], detector, nms_threshold)[0]
#     return detections

def detect_batch(
    images: list[np.ndarray],
    detector: "DefaultPredictor",
    nms_threshold: float = 0.5
):
    # print(f"[DEBUG] images.shape={images.shape}", file=sys.stderr, flush=True)
    # print(f"[DEBUG] mean pixel value={images.mean()}", file=sys.stderr, flush=True)

    # print("[DBG] cfg weights:", detector.cfg.MODEL.WEIGHTS, file=sys.stderr, flush=True)
    # print("[DBG] weights exist:", os.path.exists(detector.cfg.MODEL.WEIGHTS), file=sys.stderr, flush=True)

    """
    Detect vehicles in a batch of images using RetinaNet.
    """
    model: "RetinaNet" = detector.model
    image = images[0]
    height, width = image.shape[:2]
    transform = detector.aug.get_transform(image)
    new_h: int = transform.new_h  # type: ignore
    new_w: int = transform.new_w  # type: ignore
    images_stack = torch.from_numpy(np.stack(images)).to(device=detector.cfg.MODEL.DEVICE)

    assert str(model.pixel_mean.device) == str(detector.cfg.MODEL.DEVICE), \
        f"Model pixel mean device {model.pixel_mean.device} does " \
        f"not match detector device {detector.cfg.MODEL.DEVICE}"
    
    all_detections = []

    with torch.no_grad():
        # RGB -> BGR
        images_stack = torch.flip(images_stack, dims=[3])

        images_stack = images_stack.permute(0, 3, 1, 2)  # NHWC -> NCHW
        images_stack = images_stack.to(dtype=torch.float32)
        images_stack = interpolate(images_stack,
                                   size=(new_h, new_w),
                                   mode="bilinear",
                                   align_corners=False)

        inputs = [
            {"image": img, "height": height, "width": width}
            for img in images_stack
        ]
        predictions = model(inputs)

        for outputs in predictions:
            instances = outputs["instances"].to("cpu")
            bboxes = instances.pred_boxes.tensor.numpy()  # (N, 4)
            scores = instances.scores.numpy()
            classes = instances.pred_classes.numpy()

            nms_bboxes, nms_scores = nms(bboxes, scores, nms_threshold)

            dlist = []
            for i in range(len(nms_bboxes)):
                x1, y1, x2, y2 = nms_bboxes[i]
                score = nms_scores[i]
                cls = int(classes[i]) if len(classes) > i else -1

                w = x2 - x1
                h = y2 - y1
                cx = x1 + w / 2
                cy = y1 + h / 2

                dlist.append({
                    "class": "car", # TODO: hardcoded for now
                    "score": float(score),
                    "left": int(cx - w / 2),
                    "right": int(cx + w / 2),
                    "top": int(cy - h / 2),
                    "bottom": int(cy + h / 2),
                })

            all_detections.append(dlist)

    return all_detections

# print(">>> retinanet.py started")
# print(len(sys.argv), sys.argv)
# sys.stdout.flush()

data_root = sys.argv[1]
batch_size = int(sys.argv[2])
width = int(sys.argv[3])
height = int(sys.argv[4])
param_width = int(sys.argv[5])
param_height = int(sys.argv[6])
nms_threshold = float(sys.argv[7])
classes = sys.argv[8]
label = sys.argv[9]
# label = ""

detector = get_detector("cuda:0" , CONFIG)
# detector = get_detector("cpu" , CONFIG)

# TODO: update path
# param_file = os.path.join(data_root, 'dataset', label, 'resolution_counts.txt')

stdin = sys.stdin.detach()
while True:
    buf = stdin.read(batch_size*width*height*3)
    if not buf:
        break

    num_pixels = len(buf) // 3
    num_images = num_pixels // (width * height)
    if num_images == 0:
        break

    # record chosen resolution for batch
    images = np.frombuffer(buf, dtype='uint8')[:num_images*width*height*3].reshape((num_images, height, width, 3)) # NHWC
    # images = images.transpose((0, 3, 1, 2))
    # images = np.ascontiguousarray(images, dtype='float32')
    # with open(param_file, "a") as f:
    #     f.write(f"batch_size={batch_size}\tparam_width={param_width}\tparam_height={param_height}\n")
        # f.write(str(torch.version.cuda))

    # images = np.frombuffer(buf, dtype='uint8')[:num_images*width*height*3].reshape((num_images, height, width, 3))
    # images = images.transpose((0, 3, 1, 2))
    # images = np.ascontiguousarray(images, dtype='float32')/255.0
    if len(images) == 0:
        break

    detections = detect_batch(
        images,
        detector,
        nms_threshold
    )

    print('json'+json.dumps(detections), flush=True)

