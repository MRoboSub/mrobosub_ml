"""
LabelAndPartitionSeg.py

Same as LabelAndPartition.py (Labelbox ndjson -> train/test split), but writes
YOLOv8 SEGMENTATION labels (normalized polygons) instead of YOLOv5 detection
labels (bbox). Mask shape is preserved instead of being collapsed to a box.

Label format (one line per instance):
    class_id x1 y1 x2 y2 x3 y3 ... xn yn
where all coordinates are normalized to [0, 1] relative to image width/height.
"""

import asyncio
import os
import sys
import json
import random
from httpx import AsyncClient
from PIL import Image
import io
from typing import Literal, Union
from enum import Enum

import aiofiles
import numpy as np
import cv2
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

API_KEY = os.getenv("LABELBOX_API_KEY")
if API_KEY is not None:
    print("API Key successfully loaded")
else:
    print("API Key not found. Make sure the environment variable is set.")
    exit(1)

PROJECT_ID = "cmeaykrdk0lvm07y1eriofb1o" # 2025 project ID on labelbox

# TODO: change this to pathmarker and maybe also bin, once we have 2026 training data
class Classes(Enum):
    SHARK = 0
    SAWFISH = 1
    BIN_SHARK = 2
    BIN_SAWFISH = 3
    GATE_BACK = 4
    RED_POLE = 5
    OCTAGON = 6
    BIN_FAR = 7

# Fraction of the dataset to actually pull/process, in (0.0, 1.0].
# Set to e.g. 0.05 to sanity-check the whole pipeline on 5% of the data before
# committing to a full pull. Set to 1.0 for the real run.
SAMPLE_FRACTION = 0.05

# Minimum number of polygon points to keep (need >=3 for a valid polygon)
MIN_POLY_POINTS = 3
# approxPolyDP epsilon as a fraction of contour perimeter (higher = fewer points)
APPROX_EPSILON_FRAC = 0.002


def mask_to_polygon(mask: Image.Image) -> list[tuple[float, float]]:
    """
    Takes a 2D mask image (white inside object, black outside) and returns
    the largest contour as a simplified list of (x, y) pixel coordinates.
    """
    assert mask.mode == "L"
    mask_array = np.array(mask)
    binary = (mask_array > 0).astype(np.uint8) * 255

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []

    # keep only the largest contour (assumes one instance per mask, matching
    # how Labelbox exports one mask per annotated object)
    largest = max(contours, key=cv2.contourArea)

    perimeter = cv2.arcLength(largest, True)
    epsilon = APPROX_EPSILON_FRAC * perimeter
    simplified = cv2.approxPolyDP(largest, epsilon, True)

    points = [(float(p[0][0]), float(p[0][1])) for p in simplified]
    if len(points) < MIN_POLY_POINTS:
        return []
    return points


async def image_task(
    mask_client: AsyncClient, image: AsyncClient, image_json, batch: Union[Literal["train"], Literal["test"]]
):
    assert image_json["media_attributes"]["mime_type"] == "image/png"

    image_name = image_json["data_row"]["external_id"]
    image_data_url = image_json["data_row"]["row_data"]
    image_data_res = await image.get(image_data_url, timeout=None)
    image_data = image_data_res.content

    project = image_json["projects"][PROJECT_ID]

    labels: dict[str, list[tuple[Classes, list[tuple[float, float]]]]] = {}

    for labeler in project["labels"]:
        name = labeler["label_details"]["created_by"]
        labels[name] = []
        for label in labeler["annotations"]["objects"]:
            mask_data_url = label["mask"]["url"]
            mask_data_res = await mask_client.get(mask_data_url, timeout=None)
            if mask_data_res.status_code != 200:
                continue
            mask = Image.open(io.BytesIO(mask_data_res.content))

            polygon = mask_to_polygon(mask)
            if not polygon:
                continue  # skip degenerate/empty masks

            class_name = label["value"].upper()
            classification: Classes = getattr(Classes, class_name)
            labels[name].append((classification, polygon))

        if len(labels[name]) == 0:
            labels.pop(name, "")

    image_base = image_name.rstrip(".jpg").rstrip(".png")
    w = image_json["media_attributes"]["width"]
    h = image_json["media_attributes"]["height"]

    lines: list[str] = []
    if len(labels) != 0:
        async with aiofiles.open(f"{batch}/images/{image_name}", mode="wb") as f:
            await f.write(image_data)

        for classification, polygon in next(iter(labels.values())):
            coords = " ".join(f"{x / w:.6f} {y / h:.6f}" for x, y in polygon)
            lines.append(f"{classification.value} {coords}")

        async with aiofiles.open(f"{batch}/labels/{image_base}.txt", mode="w") as f:
            await f.write("\n".join(lines))


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def generateFiles(json_file_name):
    try:
        os.mkdir("train")
        os.mkdir("train/images")
        os.mkdir("train/labels")
        os.mkdir("test")
        os.mkdir("test/images")
        os.mkdir("test/labels")
    except FileExistsError:
        print("Error generating the train/test directories - did they already exist?")
        exit()

    jsons = []
    with open(json_file_name) as f1:
        for line in f1:
            jsons.append(json.loads(line))

    random.shuffle(jsons)

    if not (0.0 < SAMPLE_FRACTION <= 1.0):
        raise ValueError(f"SAMPLE_FRACTION must be in (0.0, 1.0], got {SAMPLE_FRACTION}")
    num_sample = max(1, int(len(jsons) * SAMPLE_FRACTION))
    jsons = jsons[:num_sample]
    print(f"SAMPLE_FRACTION={SAMPLE_FRACTION} -> using {len(jsons)} of the available rows")

    num_test = len(jsons) // 10
    test = jsons[:num_test]
    train = jsons[num_test:]

    headers = {"Authorization": f"Bearer {API_KEY}"}

    async def gather():
        async with AsyncClient(headers=headers) as header_client, AsyncClient() as default_client:
            flist = []
            for test_json in test:
                flist.append(image_task(header_client, default_client, test_json, "test"))
            for train_json in train:
                flist.append(image_task(header_client, default_client, train_json, "train"))

            for batch in tqdm(chunks(flist, 20), total=(len(flist) + 1) // 20):
                await atqdm.gather(*batch)

    asyncio.run(gather())

    # write a ready-to-use data.yaml for ultralytics
    class_names = {c.value: c.name.lower() for c in Classes}
    yaml_lines = [
        f"train: {os.path.abspath('train/images')}",
        f"val: {os.path.abspath('test/images')}",
        f"nc: {len(class_names)}",
        f"names: {list(class_names.values())}",
    ]
    with open("data.yaml", "w") as f:
        f.write("\n".join(yaml_lines))
    print("Wrote data.yaml")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] usage: python3 LabelAndPartitionSeg.py [JSONFILE].ndjson")
        exit()
    generateFiles(str(sys.argv[1]))