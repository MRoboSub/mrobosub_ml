from ultralytics import YOLO
import torch # Since yolov3, yolo has been redeveloped to use pytorch
import os
from IPython.display import Image, clear_output  # to display images

DEVICE = ""
if(torch.cuda.is_available()):
    print("Setup complete. Using torch " + torch.cuda.get_device_properties(0).name)
    DEVICE = torch.cuda.get_device_properties(0).name
else:
    print("cpu")
    DEVICE = "cpu"

# Load a model
model = YOLO("yolo11n.pt")

IMAGE=640
BATCH=64
EPOCHS=256
DATA="../model.yaml"  # TODO: check this is correct

# Train the model
train_results = model.train(
    data=DATA,  # path to dataset YAML
    epochs=EPOCHS,  # number of training epochs
    imgsz=IMAGE,  # training image size
    device=DEVICE,  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
)

# Evaluate model performance on the validation set
metrics = model.val(data="../mrobosub_dataset_2023/test/images/")

# Perform object detection on an image
# results = model("path/to/image.jpg")
# results[0].show()

# Export the model to ONNX format
path = model.export(format="onnx")  # return path to exported model