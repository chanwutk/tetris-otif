import os
import numpy as np
import ultralytics
import sys
import json

# Set environment variable to suppress verbose output
os.environ['YOLO_VERBOSE'] = 'False'


# COCO class indices: car=2, bus=5, truck=7
# Note: Vans are typically classified as cars (2) in COCO dataset
VEHICLE_CLASSES = [2, 5, 7]  # car (includes vans), bus, truck

def get_detector(device: str, model_path: str):
    """
    Get YOLOv5 detector model configured to detect only vehicles.

    Args:
        device: Device to run the model on ('cpu' or 'cuda')
        model_path: Path to the YOLOv5 model file

    Returns:
        torch.nn.Module: Configured YOLOv5 model for vehicle detection
    """
    # print(f"Loading YOLOv5 detector for dataset on {device}")
    model = ultralytics.YOLO(model_path, verbose=False)  # type: ignore
    # print(f"Loaded YOLOv5 detector for dataset on {device}")
    model.fuse()
    # print(f"Fused YOLOv5 detector for dataset on {device}")
    model.to(device)
    # print(f"Moved YOLOv5 detector for dataset to {device}")
    model.eval()
    # print(f"Evaluated YOLOv5 detector for dataset on {device}")
    return model


# def detect(image, model):
#     """
#     Detect vehicles in an image using YOLOv5.

#     Args:
#         image: Input image as numpy array (H, W, C)
#         model: YOLOv5 model instance

#     Returns:
#         np.ndarray: Detection results as array of shape (N, 5)
#                     where each row is [x1, y1, x2, y2, confidence]
#     """

#     # Filter classes during prediction for better performance
#     results = model(image, verbose=False)[0]

#     if results.boxes is None or len(results.boxes) == 0:
#         res = np.empty((0, 5))
#         return res

#     # Get bounding boxes and confidence scores
#     bboxes = results.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
#     confidences = results.boxes.conf.cpu().numpy()  # confidence scores

#     # Create output array with shape (N, 5): [x1, y1, x2, y2, confidence]
#     detections = np.zeros((len(bboxes), 5))
#     detections[:, :4] = bboxes
#     detections[:, 4] = confidences

#     return detections


def detect_batch(images, model):
    """
    Detect vehicles in a batch of images using YOLOv5.

    Args:
        images: Input images as numpy array (H, W, C)
        model: YOLOv5 model instance

    Returns:
        list[np.ndarray]: Detection results as array of shape (N, 5)
                    where each row is [x1, y1, x2, y2, confidence]
    """
    # print('detect_batch')
    # Pass images as a list instead of stacking them
    # Ultralytics handles batching internally and expects a list of images
    # print("DEBUG: ", images, flush=True)
    all_results = model(images, verbose=False)
    all_detections = []

    for results in all_results:
        if results.boxes is None or len(results.boxes) == 0:
            all_detections.append([])
            continue

        bboxes = results.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        scores = results.boxes.conf.cpu().numpy()
        classes = results.boxes.cls.cpu().numpy() if results.boxes.cls is not None else [-1]*len(bboxes)

        dlist = []
        for i in range(len(bboxes)):
            x1, y1, x2, y2 = bboxes[i]
            score = scores[i]
            cls = int(classes[i]) if len(classes) > i else -1

            w = x2 - x1
            h = y2 - y1
            cx = x1 + w / 2
            cy = y1 + h / 2

            dlist.append({
                "class": "car",  # TODO: you can map cls → class name if needed
                "score": float(score),
                "left": int(cx - w / 2),
                "right": int(cx + w / 2),
                "top": int(cy - h / 2),
                "bottom": int(cy + h / 2),
            })

        all_detections.append(dlist)

    return all_detections


data_root = sys.argv[1]
batch_size = int(sys.argv[2])
width = int(sys.argv[3])
height = int(sys.argv[4])
param_width = int(sys.argv[5])
param_height = int(sys.argv[6])
nms_threshold = float(sys.argv[7])
classes = sys.argv[8]
label = sys.argv[9]
model_path = sys.argv[10]
# label = ""

detector = get_detector("cuda:0" , model_path)
# detector = get_detector("cpu" , CONFIG)

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
    # print("DEBUG: ", images.shape)

    # RGB -> BGR
    images = images[:, :, :, ::-1]

    images_list = [np.ascontiguousarray(img) for img in images]

    detections = detect_batch(
        images_list,
        detector,
    )

    print('json'+json.dumps(detections), flush=True)