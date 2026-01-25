import asyncio
import os
import sys
import json
import random
from httpx import AsyncClient
from PIL import Image
import io
from typing import Literal
from enum import Enum
from dataclasses import dataclass
import aiofiles
import numpy as np
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

# Create and get API_KEY from https://app.labelbox.com/workspace-settings/api-keys (and don't commit to git)
API_KEY = ""
PROJECT_ID = "cmeaykrdk0lvm07y1eriofb1o" # 2025 project ID on labelbox

class Classes(Enum):
    SHARK = 0
    SAWFISH = 1
    BIN_SHARK = 2
    BIN_SAWFISH = 3
    GATE_BACK = 4
    RED_POLE = 5
    OCTAGON = 6
    BIN_FAR = 7


@dataclass
class Bbox:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def x_center(self) -> float:
        return self.left + self.width / 2

    @property
    def y_center(self) -> float:
        return self.top + self.height / 2

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

"""
    Takes in a 2D image that is a mask and returns the bounding box 
    defined by that mask
"""
def mask_to_bbox(mask: Image.Image) -> Bbox:
    assert mask.mode == "L"

    mask_array = np.array(mask)
    y_indices, x_indices = np.where(mask_array > 0)
    if len(x_indices) == 0 or len(y_indices) == 0:
        return Bbox(0, 0, 0, 0)

    left = float(np.min(x_indices))
    top = float(np.min(y_indices))
    right = float(np.max(x_indices))
    bottom = float(np.max(y_indices))

    return Bbox(left, top, right, bottom)

"""
Processes a single image (i.e., a single json data_row)
and writes processed classification to [train or test]/labels/[image_name].txt

Format of output entry: [class number] [bbox.x_center] [bbox.y_center] [bbox.width] [bbox.height]
where the last 4 entries have been scaled down into range [0, 1] relative to the image width/height
"""
async def image_task(
    client: AsyncClient, image_json, batch: Literal["train"] | Literal["test"]
):
    assert image_json["media_attributes"]["mime_type"] == "image/png"

    # pull the actual image from labelbox
    image_name = image_json["data_row"]["external_id"]
    image_data_url = image_json["data_row"]["row_data"]
    async with AsyncClient() as default_client:
        # have to use a client without headers as image_data_url is a signed link and including an auth header messes it up
        image_data_res = await default_client.get(image_data_url, timeout=None)
    image_data = image_data_res.content

    project = image_json["projects"][PROJECT_ID]
    labels: dict[str, list[tuple[Classes, Bbox]]] = {}
    for labeler in project["labels"]:
        name = labeler["label_details"]["created_by"]
        labels[name] = []
        for label in labeler["annotations"]["objects"]:
            mask_data_url = label["mask"]["url"]
            mask_data_res = await client.get(mask_data_url, timeout=None) # fetch mask from labelbox
            mask = Image.open(io.BytesIO(mask_data_res.content))
            # the mask is a 2D image: white inside bounding box and black everywhere else
            bbox: Bbox = mask_to_bbox(mask)
            class_name = label["value"].upper() # class_name, for instance, might be BIN_SAWFISH
            classification: Classes = getattr(Classes, class_name)
            labels[name].append((classification, bbox))
    # reconcile duplicates?
    image_base = image_name.rstrip(".jpg").rstrip(".png")
    w = image_json["media_attributes"]["width"]
    h = image_json["media_attributes"]["height"]

    async with aiofiles.open(f"{batch}/images/{image_name}", mode="wb") as f:
        await f.write(image_data)

    lines: list[str] = []
    if len(labels) != 0:
        for classification, bbox in next(
            iter(labels.values())  # same image might have been labeled by multiple people, only use the first labeler
        ):
            lines.append(
                f"{classification.value} {bbox.x_center / w} {bbox.y_center / h} {bbox.width / w} {bbox.height / h}"
            ) # class number and the values x_center, y_center, width, height scaled down by width and height of the image to be in range [0,1]

    async with aiofiles.open(f"{batch}/labels/{image_base}.txt", mode="w") as f:
        await f.write("\n".join(lines))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def generateFiles(json_file_name):
    # Create Data/images and Data/labels
    try:
        os.mkdir("train")
        os.mkdir("train/images")
        os.mkdir("train/labels")
        os.mkdir("test")
        os.mkdir("test/images")
        os.mkdir("test/labels")
    except:
        print("Error generating the train/test directories - did they already exist?")
        exit()

    jsons = []
    with open(json_file_name) as f1:
        for line in f1:
            jsons.append(json.loads(line))
    random.shuffle(jsons)
    num_test = len(jsons) // 10
    test = jsons[:num_test]
    train = jsons[num_test:]

    headers = {"Authorization": f"Bearer {API_KEY}"}

    async def gather():
        async with AsyncClient(headers=headers) as client:
            flist = []
            for test_json in test:
                f = image_task(client, test_json, "test")
                flist.append(f)
            for train_json in train:
                f = image_task(client, train_json, "train")
                flist.append(f)
            for batch in tqdm(chunks(flist, 20), total=(len(flist) + 1) // 20):
                await atqdm.gather(*batch)

    asyncio.run(gather())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] usage: python3 LabelAndPartition.py [JSONFILE].ndjson")
        exit()
    if API_KEY == "":
        print("[ERROR]: Must set API_KEY variable")
        exit()
    generateFiles(str(sys.argv[1]))

