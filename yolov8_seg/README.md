Authored July 2026 by Muskaan Mittal

### STEP 1: Prepare Training Data

Set up python environment, get images labelled on labelbox via README.md in outer folder. Export labelbox API key per those instructions.
Once you have the .ndjson for this year's data in mrobosub_ml directory,

```cd yolov8_seg```
```python3 LabelAndPartitionSeg.py [JSONFILE].ndjson```

### STEP 2: Train Model

```pip install ultralytics```

Now, if on cluster: (unvalidated)
```bash
yolo segment train \
  data=data.yaml \
  model=yolov8n-seg.pt \
  epochs=100 \
  imgsz=640 \
  device=0
```

If running locally on computer, can train fewer epochs. Use: (tested on macbook m3)

```export PYTORCH_ENABLE_MPS_FALLBACK=1```

```bash
yolo segment train \
  data=data.yaml \
  model=yolov8n-seg.pt \
  epochs=25 \
  imgsz=640 \
  device=0
```

### STEP 3: Use Model for Inference
Once model is trained, copy over best.pt (the weights) into main mrobosub repo (mrobosub_perception/models/[20xx]_seg_best.pt). Update the filename in seg_executor.py to this path and you are now ready to run ML inference!