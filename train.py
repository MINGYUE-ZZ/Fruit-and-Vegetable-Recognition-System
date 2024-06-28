# -*- coding:utf-8 -*-
# @author: syh




from ultralytics import YOLO
import _locale



if __name__ == '__main__':
    # Initialize model from YAML
    model = YOLO('yolov8n.yaml')
    # Load weights
    model.load('./weights/yolov8n.pt')
    _locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])

    # Ensuring the file is read with correct encoding
    with open('./VOCData/ImageSets/train.txt', 'r', encoding='utf-8', errors='ignore') as file:
        train_paths = file.readlines()

    # Train the model
    model.train(data='./VOCData/mydata.yaml', epochs=100, imgsz=640)



