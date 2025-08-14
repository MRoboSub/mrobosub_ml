import json
import os
import requests
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from tqdm import tqdm

LABELBOX_JSON = "labelbox_export.json"
OUTPUT_DIR = "yolov5_seg_dataset"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images/train")
LABEL_DIR = os.path.join(OUTPUT_DIR, "labels/train")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

def download_or_decode_mask(data):
    if "mask" in data:
        if data["mask"].get("url"):
            response = requests.get(data["mask"]["url"])
            return Image.open(BytesIO(response.content)).convert("L")
        elif data["mask"].get("data"):
            mask_data = base64.b64decode(data["mask"]["data"])
            return Image.open(BytesIO(mask_data)).convert("L")
    return None

def mask_to_polygons(mask_np):
    # Threshold mask
    _, thresh = cv2.threshold(mask_np, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = [cnt.squeeze() for cnt in contours if len(cnt) >= 3]
    return polygons

def normalize_polygon(polygon, width, height):
    return [(x / width, y / height) for x, y in polygon]

def polygon_to_yolo_line(class_id, polygon, width, height):
    xs = [x for x, y in polygon]
    ys = [y for x, y in polygon]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    x_center = (x_min + x_max) / 2 / width
    y_center = (y_min + y_max) / 2 / height
    w = (x_max - x_min) / width
    h = (y_max - y_min) / height

    flat_poly = " ".join(f"{x:.6f} {y:.6f}" for x, y in normalize_polygon(polygon, width, height))
    return f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f} {flat_poly}"

def process_labelbox_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    class_map = {}  # Maps class name to index
    next_class_id = 0

    for item in tqdm(data, desc="Processing images"):
        image_url = item["Labeled Data"]
        file_name = os.path.basename(image_url).split("?")[0]
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content)).convert("RGB")
        width, height = img.size

        # Save the image locally
        img_out_path = os.path.join(IMAGE_DIR, file_name)
        img.save(img_out_path)

        # Start writing the label file
        label_lines = []

        for annotation in item["Label"]["objects"]:
            class_name = annotation["title"]
            if class_name not in class_map:
                class_map[class_name] = next_class_id
                next_class_id += 1
            class_id = class_map[class_name]

            mask_img = download_or_decode_mask(annotation)
            if mask_img is None:
                continue
            mask_np = np.array(mask_img.resize((width, height)))

            polygons = mask_to_polygons(mask_np)
            for poly in polygons:
                line = polygon_to_yolo_line(class_id, poly, width, height)
                label_lines.append(line)

        # Save label file
        if label_lines:
            label_path = os.path.join(LABEL_DIR, file_name.replace(".jpg", ".txt").replace(".png", ".txt"))
            with open(label_path, "w") as f:
                f.write("\n".join(label_lines))

    print("Class map:", class_map)

process_labelbox_json(LABELBOX_JSON)

