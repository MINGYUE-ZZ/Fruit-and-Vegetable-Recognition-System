# -*- coding:utf-8 -*-
# @author: syh


from ultralytics import YOLO

# Load a model
model = YOLO('./runs/detect/train/weights/best.pt')
# Run batched inference on a list of images
model("./img", imgsz=640, save=True, device=0)
