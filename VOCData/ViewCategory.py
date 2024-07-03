# -*- coding:utf-8 -*-
# @author: syh


import os
import xml.etree.ElementTree as ET
from tqdm import tqdm


def count_num(indir):
    label_list = []
    dict = {}  # 新建字典，用于存放各类标签名及其对应的数目
    for file in tqdm(os.listdir(indir)):
        file_path = os.path.join(indir, file)
        # actual parsing
        in_file = open(file_path, encoding='utf-8')
        tree = ET.parse(in_file)
        root = tree.getroot()

        # 遍历文件的所有标签
        for obj in root.iter('object'):
            name = obj.find('name').text
            if name in dict.keys():
                dict[name] += 1  # 如果标签不是第一次出现，则+1
            else:
                dict[name] = 1  # 如果标签是第一次出现，则将该标签名对应的value初始化为1

    # 打印结果
    print("各类标签的数量分别为：")
    for key in dict.keys():
        print(key + ': ' + str(dict[key]))
        label_list.append(key)
    print("标签类别如下：")
    print(label_list)


if __name__ == '__main__':
    count_num('Annotations')  # 调用函数统计各类标签数目
