# -*- coding:utf-8 -*-
# @author: syh


import shutil
import xml.etree.ElementTree as ET
import os
from tqdm import tqdm


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return [x, y, w, h]


def convert_annotation(xml_path, image_set):
    in_file = open(xml_path, encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    for size in root.iter("size"):
        w = int(size.find("width").text)
        h = int(size.find("height").text)

    all_boxs = []
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        b1, b2, b3, b4 = b
        b = (b1, b2, b3, b4)
        bb = convert((w, h), b)
        bb.insert(0, cls_id)
        all_boxs.append(bb)

    out_file = open(f'./labels/{os.path.split(xml_path)[-1].replace(".xml", ".txt")}', 'w', encoding="utf-8")
    for box in all_boxs:
        out_file.write(" ".join([str(i) for i in box]) + '\n')
    out_file.close()

    list_file = open('ImageSets/%s.txt' % image_set, 'a', encoding="utf-8")
    list_file.write(abs_path.replace("\\", "/") + '/images/%s.jpg\n' % image_id)
    list_file.close()


if __name__ == "__main__":
    sets = ['train', 'val', 'test']
    # 改成自己的类别
    classes = ['黑葡萄', '绿葡萄', '樱桃', '西瓜', '龙眼', '香蕉', '芒果', '菠萝', '柚子', '草莓', '苹果', '柑橘', '火龙果', '梨子', '花生', '黄瓜', '土豆', '大蒜', '茄子', '白萝卜', '辣椒', '胡萝卜', '花菜', '白菜', '番茄', '西蓝花', '橙子']
    abs_path = os.getcwd()
    print(abs_path)

    if not os.path.exists('./labels/'):
        os.makedirs('./labels/')
    else:
        shutil.rmtree('./labels/')
        os.makedirs('./labels/')

    for image_set in sets:
        if os.path.exists('./ImageSets/%s.txt' % image_set):
            os.remove('./ImageSets/%s.txt' % image_set)
        image_ids = open('./ImageSets/Main/%s.txt' % image_set).read().strip().split()
        for image_id in tqdm(image_ids, desc=f'{image_set}'):
            convert_annotation(f"./Annotations/{image_id}.xml", image_set)
