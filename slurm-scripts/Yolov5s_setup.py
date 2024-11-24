import torch # Since yolov3, yolo has been redeveloped to use pytorch
import os
from IPython.display import Image, clear_output  # to display images


if(torch.cuda.is_available()):
    print("Setup complete. Using torch " + torch.cuda.get_device_properties(0).name)
else:
    print("CPU")
