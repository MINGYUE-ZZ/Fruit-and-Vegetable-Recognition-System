# -*- coding:utf-8 -*-
# @author: syh


import os
import random
from tqdm import tqdm

train_val_percent = 1  # 训练集和验证集的总比例
train_percent = 0.8  # 训练集占总比例的比例
Annotations_file_path = 'images'
txt_save_path = 'ImageSets/Main'
total_xml = os.listdir(Annotations_file_path)

if not os.path.exists(txt_save_path):
    os.makedirs(txt_save_path, exist_ok=True)

random.shuffle(total_xml)
num = len(total_xml)
list = range(num)
tv = int(num * train_val_percent)
tr = int(tv * train_percent)
train_val = random.sample(list, tv)
train = random.sample(train_val, tr)

f_train_val = open('ImageSets/Main/trainval.txt', 'w')
f_test = open('ImageSets/Main/test.txt', 'w')
f_train = open('ImageSets/Main/train.txt', 'w')
f_val = open('ImageSets/Main/val.txt', 'w')

for i in tqdm(list, unit="image", ncols=80, desc='划分数据'):
    name = total_xml[i].split(".")[0] + '\n'
    if i in train_val:
        f_train_val.write(name)
        if i in train:
            f_train.write(name)
        else:
            f_val.write(name)
    else:
        f_test.write(name)

f_train_val.close()
f_train.close()
f_val.close()
f_test.close()
