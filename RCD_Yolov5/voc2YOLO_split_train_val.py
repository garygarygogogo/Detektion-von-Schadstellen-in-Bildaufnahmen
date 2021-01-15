import cv2
import os
import xml.etree.ElementTree as ET
import shutil
import numpy as np


def xml_txt(train_txt_path, train_image_path, val_txt_path, val_image_path, xml_dir_path, labels):
    train_cnt = 0
    val_cnt = 0
    if not os.path.exists(train_txt_path):
        os.makedirs(train_txt_path)
    if not os.path.exists(train_image_path):
        os.makedirs(train_image_path)
    if not os.path.exists(val_txt_path):
        os.makedirs(val_txt_path)
    if not os.path.exists(val_image_path):
        os.makedirs(val_image_path)
    # 遍历图片文件夹
    for (root, dirname, files) in os.walk(xml_dir_path):
        print(root,dirname,files)

        np.random.seed(100)
        np.random.shuffle(files)

        train_ratio = 0.8
        val_ratio = 0.2
        train_num = int(len(files) * train_ratio)
        val_num = int(len(files) * val_ratio)
        files_train = files[:train_num]
        files_val = files[train_num:train_num+val_num]

        # 获取图片名
        for ft in files_train:
            if(os.path.splitext(ft)[1] != ".jpg"):
                continue
            # ft是图片名字+扩展名，替换txt,xml格式
            ftxt = ft.replace(ft.split('.')[1], 'txt')
            fxml = ft.replace(ft.split('.')[1], 'xml')
            fimg = ft.replace(ft.split('.')[1], 'jpg')
            # xml文件路径
            xml_path = os.path.join(xml_dir_path, fxml)
            fimg_path = os.path.join(xml_dir_path, fimg)
            # txt文件路径
            ftxt_path = os.path.join(train_txt_path, ftxt)
            # 解析xml
            tree = ET.parse(xml_path)
            root = tree.getroot()
            # 获取weight,height
            size = root.find('size')
            w = size.find('width').text
            h = size.find('height').text
            dw = 1/float(w)
            dh = 1/float(h)
            # 初始化line
            line = ''
            for item in root.findall('object'):
                # 提取label,并获取索引
                label = item.find('name').text
                if label not in labels:
                    continue
                label = labels.index(label)
                # 提取信息labels, x, y, w, h 
                # 多框转化
                for box in item.findall('bndbox'):
                    xmin = float(box.find('xmin').text)
                    ymin = float(box.find('ymin').text)
                    xmax = float(box.find('xmax').text)
                    ymax = float(box.find('ymax').text)
                    # print(xmin,ymin,xmax,ymax)

                    # x, y, w, h归一化
                    center_x = ((xmin + xmax) / 2) * dw
                    center_y = ((ymin + ymax) / 2) * dh
                    bbox_width = (xmax-xmin) * dw
                    bbox_height = (ymax-ymin) * dh
                    # print(center_x,center_y,bbox_width,bbox_height)

                    # 传入信息，txt是字符串形式
                    line += '{} {} {} {} {}'.format(label,center_x,center_y,bbox_width,bbox_height) + '\n'

            # 将txt信息写入文件
            with open(ftxt_path, 'w') as f_txt:
                f_txt.write(line)
            shutil.copy(fimg_path,train_image_path)
            train_cnt += 1
            print('Processing (train)：', ft)

        # 获取图片名
        for ft in files_val:
            if(os.path.splitext(ft)[1] != ".jpg"):
                continue
            # ft是图片名字+扩展名，替换txt,xml格式
            ftxt = ft.replace(ft.split('.')[1], 'txt')
            fxml = ft.replace(ft.split('.')[1], 'xml')
            fimg = ft.replace(ft.split('.')[1], 'jpg')
            # xml文件路径
            xml_path = os.path.join(xml_dir_path, fxml)
            fimg_path = os.path.join(xml_dir_path, fimg)
            # txt文件路径
            ftxt_path = os.path.join(val_txt_path, ftxt)
            # 解析xml
            tree = ET.parse(xml_path)
            root = tree.getroot()
            # 获取weight,height
            size = root.find('size')
            w = size.find('width').text
            h = size.find('height').text
            dw = 1/float(w)
            dh = 1/float(h)
            # 初始化line
            line = ''
            for item in root.findall('object'):
                # 提取label,并获取索引
                label = item.find('name').text
                if label not in labels:
                    continue
                label = labels.index(label)
                # 提取信息labels, x, y, w, h 
                # 多框转化
                for box in item.findall('bndbox'):
                    xmin = float(box.find('xmin').text)
                    ymin = float(box.find('ymin').text)
                    xmax = float(box.find('xmax').text)
                    ymax = float(box.find('ymax').text)
                    # print(xmin,ymin,xmax,ymax)

                    # x, y, w, h归一化
                    center_x = ((xmin + xmax) / 2) * dw
                    center_y = ((ymin + ymax) / 2) * dh
                    bbox_width = (xmax-xmin) * dw
                    bbox_height = (ymax-ymin) * dh
                    # print(center_x,center_y,bbox_width,bbox_height)

                    # 传入信息，txt是字符串形式
                    line += '{} {} {} {} {}'.format(label,center_x,center_y,bbox_width,bbox_height) + '\n'

            # 将txt信息写入文件
            with open(ftxt_path, 'w') as f_txt:
                f_txt.write(line)
            shutil.copy(fimg_path,val_image_path)
            val_cnt += 1
            print('Processing (val)：', ft)
        print("Train num:", train_cnt)
        print("Val num:", val_cnt)


if __name__ == '__main__':
    train_txt_path = "/Users/lang/Desktop/myYOLOv5_roadCracksDetection/dataset/labels/train"
    train_image_path = "/Users/lang/Desktop/myYOLOv5_roadCracksDetection/dataset/images/train"
    val_txt_path = "/Users/lang/Desktop/myYOLOv5_roadCracksDetection/dataset/labels/val"
    val_image_path = "/Users/lang/Desktop/myYOLOv5_roadCracksDetection/dataset/images/val"

    xml_image_path = "/Users/lang/Desktop/train/Japan/images"  # 存放图片和xml 的文件目录

    labels = ['D00', 'D10', 'D20', 'D40']  # 用于获取label位置
    xml_txt(train_txt_path, train_image_path, val_txt_path, val_image_path, xml_image_path, labels)
