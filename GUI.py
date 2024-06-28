# -*- coding:utf-8 -*-
# @author: syh



from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject

import shutil
import sys
import os
import time
import random
import csv
import cv2
import yaml
from datetime import datetime

from ultralytics import YOLO

# UI--Logic分离
main_ui, _ = loadUiType('./UI/main.ui')


class MainGui(QMainWindow, main_ui):
    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # ------------------------- 界面相关图标 -----------------------------
        # 设置图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon/app.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icon/dirs.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_img.setIcon(icon1)

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icon/dir.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_dir.setIcon(icon2)

        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icon/shipinwenjian.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_video.setIcon(icon3)

        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("icon/shexiangtou.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_cap.setIcon(icon4)

        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("icon/data.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_data.setIcon(icon5)

        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("icon/weights.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_weights.setIcon(icon6)

        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("icon/backgroung.png")))  # 设置背景图片
        self.setPalette(palette)

        self.label_4.setPixmap(QtGui.QPixmap("icon/IOU.png"))
        self.label_5.setPixmap(QtGui.QPixmap("icon/zhixindu.png"))
        self.label_8.setPixmap(QtGui.QPixmap("icon/NVIDIA.png"))
        self.label_11.setPixmap(QtGui.QPixmap("icon/yongshi.png"))
        self.label_14.setPixmap(QtGui.QPixmap("icon/zhixindu.png"))
        self.label_15.setPixmap(QtGui.QPixmap("icon/leibie.png"))
        self.label_16.setPixmap(QtGui.QPixmap("icon/half.png"))
        self.label_17.setPixmap(QtGui.QPixmap("icon/weizhi.png"))
        self.label_22.setPixmap(QtGui.QPixmap("icon/imgs.png"))
        self.label_25.setPixmap(QtGui.QPixmap("icon/suoyoumubiao.png"))

        self.label_width, self.label_height = self.label_img.size().width(), self.label_img.size().height()

        # 单个文件名字
        self.img_name = None
        # 文件保存地址（绘图）
        self.result_img_name = None
        # 类别名（img,dir,video）
        self.start_type = None
        if self.start_type not in ["cap", "video"]:
            self.pushButton_end.setEnabled(False)

        self.img_path = None
        self.img_path_dir = None

        self.video = None
        self.video_path = None

        self.worker_thread = None

        self.names = { '黑葡萄': 'black grape', '绿葡萄': 'green grape', '樱桃': 'cherry', '西瓜': 'watermelon',
                       '龙眼': 'longan', '香蕉': 'banana', '芒果': 'mango', '菠萝': 'pineapple', '柚子': 'pomelo',
                       '草莓': 'strawberry', '苹果': 'apple', '柑橘': 'citrus', '火龙果': 'dragon fruit', '梨子': 'pear',
                       '花生': 'peanut', '黄瓜': 'cucumber', '土豆': 'potato', '大蒜': 'garlic', '茄子': 'eggplant',
                       '白萝卜': 'white radish', '辣椒': 'chili', '胡萝卜': 'carrot', '花菜': 'cauliflower',
                       '白菜': 'Chinese cabbage', '番茄': 'tomato', '西蓝花': 'broccoli', '橙子': 'orange' }
        # 字体颜色
        self.color = {"font": (255, 255, 255)}

        self.all_result = []
        self.comboBox_name = []

        self.selected_text = None
        self.number = 1
        self.RowLength = 0
        self.input_time = 0

        # ------------------------- 图片文件存储位置 -----------------------------
        # 获取当前工程文件位置
        self.ProjectPath = os.getcwd()

        # 保存所有的输出文件
        self.output_dir = os.path.join(self.ProjectPath, 'output')
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        run_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.result_time_path = os.path.join(self.output_dir, run_time)
        os.mkdir(self.result_time_path)

        self.result_img_path = os.path.join(self.result_time_path, 'img_result')
        os.mkdir(self.result_img_path)
        # 保存绘制好的图片结果
        self.result_org_img_path = os.path.join(self.result_time_path, 'org_img')
        os.mkdir(self.result_org_img_path)

        # ---------------------------- 模型参数 --------------------------------
        self.GPU = {"GPU": "0", "CPU": "cpu"}
        # 推理GPU or CPU
        self.device = 0
        # FP16 半精度
        self.half = False
        # 推理数据文件路径
        self.data_file_name = ""
        # 推理权重文件路径
        self.weights_file_name = ""
        # 推理模型
        self.model = None

        # ---------------------------- 存储可变参数 --------------------------------
        self.save_parameter = {}
        self.pre_parameter = {}

        # 修改table的宽度
        self.update_table_width()
        self.handle_buttons()

    def handle_buttons(self):


        """
        按钮控件链接
        """
        # ---------------------------- 模型文件 ---------------------------------
        self.pushButton_data.clicked.connect(self.SelectData)
        self.pushButton_weights.clicked.connect(self.SelectWeights)

        # ---------------------------- 推理文件 ---------------------------------
        self.pushButton_img.clicked.connect(self.SelectImg)
        self.pushButton_dir.clicked.connect(self.SelectImgFile)
        self.pushButton_video.clicked.connect(self.SelectVideo)
        self.pushButton_cap.clicked.connect(self.SelectCap)

        # ------------------------ （GPU or CPU） ----------------------------
        self.radioButton.clicked.connect(self.GPU_CPU)
        self.radioButton_2.clicked.connect(self.GPU_CPU)

        # ---------------------------- Half ---------------------------------
        self.radioButton_5.clicked.connect(self.HALF)
        self.radioButton_6.clicked.connect(self.HALF)

        # ---------------------------- 开始推理 ---------------------------------
        self.pushButton_start.clicked.connect(self.Infer)

        # ---------------------------- 停止推理 ---------------------------------
        self.pushButton_end.clicked.connect(self.InferEnd)

        # ---------------------------- 导出数据 ---------------------------------
        self.pushButton_export.clicked.connect(self.write_csv)

        # # ---------------------------- classes ---------------------------------
        self.comboBox.activated.connect(self.onComboBoxActivated)
        self.comboBox_2.activated.connect(self.onComboBoxActivatedDetection)

        # 表格点击事件绑定
        self.tableWidget_info.cellClicked.connect(self.cell_clicked)


    def update_table_width(self):
        """
        表格设置
        """
        # 设置每列宽度
        column_widths = [50, 220, 120, 200, 80, 80, 140]
        for column, width in enumerate(column_widths):
            self.tableWidget_info.setColumnWidth(column, width)

    def Confidence(self):
        """
        得到置信度的值
        """
        confidence = '%.2f' % self.doubleSpinBox.value()
        return eval(confidence)

    def IOU(self):
        """
        得到 IOU 的值
        """
        iou = '%.2f' % self.doubleSpinBox_2.value()
        return eval(iou)

    def GPU_CPU(self):
        """
        选择GPU or CPU
        """
        selected_button = self.widget.sender()
        if selected_button is not None and isinstance(selected_button, QRadioButton):
            device = selected_button.text()
            self.device = self.GPU[device]


    def HALF(self):
        """
        使用 FP16 半精度进行推理
        """
        selected_button = self.widget.sender()
        if selected_button is not None and isinstance(selected_button, QRadioButton):
            self.half = selected_button.text()
            if self.half == "Half":
                self.half = True
            else:
                self.half = False

    def SelectData(self):
        """
        模型数据文件选择
        """
        self.data_file_name, _ = QFileDialog.getOpenFileName(self, "选择data文件", "", "所有文件(*.yaml)")
        if self.data_file_name:
            self.label_13.setText(os.path.split(self.data_file_name)[-1])

            # 读取yaml文件
            with open(self.data_file_name, 'r', encoding="utf-8") as file:
                data = yaml.safe_load(file)

            # 获取 name 值，向下拉框中写入内容
            for name in data['names']:
                self.comboBox.addItem(name)

            self.color.update(
                {data["names"][i]: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                 for i in range(data["nc"])})

    def SelectWeights(self):
        """
        模型权重选择
        """
        self.weights_file_name, _ = QFileDialog.getOpenFileName(self, "选择权重文件", "",
                                                                "所有文件(*.pt *.onnx *.torchscript *.engine "
                                                                "*.mlmodel *.pb *.tflite *openvino_model  "
                                                                "*saved_model *paddle_model)")
        if self.weights_file_name:
            self.label_12.setText(os.path.split(self.weights_file_name)[-1])
            # 保存旧值
            old_parameter = self.save_parameter.copy()
            # 更新新值
            self.save_parameter["weights"] = self.device
            # 如果参数值有变化
            if old_parameter != self.save_parameter:
                # 更新旧值
                self.pre_parameter = old_parameter

    def SelectImg(self):
        """
        图片文件选择
        """
        self.img_path, filetype = QFileDialog.getOpenFileName(self, "选择推理文件", "",
                                                              "所有文件(*.jpg *.bmp *.dng" " *.jpeg *.jpg *.mpo"
                                                              " *.png *.tif *.tiff *.webp *.pfm)")
        if self.img_path == "":
            self.start_type = None
            return

        # 显示相对应的文字
        self.start_type = 'img'
        self.img_name = os.path.split(self.img_path)[-1]

        self.label_img_path.setText(self.img_name)
        self.label_dir_path.setText("选择图片文件夹")
        self.label_video_path.setText("选择视频文件")
        self.label_cap_path.clear()
        self.label_cap_path.setPlaceholderText("选择相机源（摄像头）")

        self.org_img_save_path = os.path.join(self.result_org_img_path, self.img_name)

        # 显示原图
        self.label_img.clear()
        self.ShowSource(cv2.imread(self.img_path))
        shutil.copy(self.img_path, self.org_img_save_path)

    def SelectImgFile(self):
        """
        图片文件夹选择
        """
        self.img_path_dir = QFileDialog.getExistingDirectory(None, "选择文件夹")
        if self.img_path_dir == '':
            self.start_type = None
            return

        self.start_type = 'dir'

        self.label_img_path.setText("选择图片文件")
        self.label_dir_path.setText(os.path.split(self.img_path_dir)[-1])
        self.label_video_path.setText("选择视频文件")
        self.label_cap_path.clear()
        self.label_cap_path.setPlaceholderText("选择相机源（摄像头）")

        self.image_files = [os.path.join(self.img_path_dir, file) for file in os.listdir(self.img_path_dir) if
                            file.lower().endswith(
                                ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff'))]
        if self.image_files:
            self.img_path = self.image_files[0]
            self.img_name = os.path.split(self.img_path)[-1]

            self.label_img.clear()
            self.ShowSource(cv2.imread(self.img_path))

    def SelectVideo(self):
        """
        视频文件选择
        """
        # 选择文件
        self.video_path, filetype = QFileDialog.getOpenFileName(self, "选择推理文件", "",
                                                                "所有文件(*.asf *.avi *.gif *.m4v *.mkv "
                                                                "*.mov *.mp4 *.mpeg *.mpg *.ts *.wmv)")
        if self.video_path == "":  # 未选择文件
            self.start_type = None
            return
        self.start_type = 'video'
        self.img_name = os.path.split(self.video_path)[-1]

        self.label_img_path.setText("选择图片文件")
        self.label_dir_path.setText("选择图片文件夹")
        self.label_video_path.setText(self.img_name)
        self.label_cap_path.clear()
        self.label_cap_path.setPlaceholderText("选择相机源（摄像头）")

        shutil.copy(self.video_path, os.path.join(self.result_org_img_path, self.img_name))

    def SelectCap(self):
        """
        摄像头
        """
        self.label_img_path.setText("选择图片文件")
        self.label_dir_path.setText("选择图片文件夹")
        self.label_video_path.setText("选择视频文件")

        if self.label_cap_path.text() != '':
            try:
                self.video_path = eval(self.label_cap_path.text())
            except:
                self.video_path = self.label_cap_path.text()
        else:
            QtWidgets.QMessageBox.warning(self, "摄像头选择", f"未选择指定的摄像头")
            return
        self.start_type = 'cap'
        self.img_name = 'camera.mp4'

    def load_model(self):
        """
        加载模型
        """
        if self.save_parameter:
            # 检测模型参数是否改变
            if self.pre_parameter.items() != self.save_parameter.items():
                self.pre_parameter = self.save_parameter

                # 加载模型的参数是否为空
                result = self.check_none_variables(weights=self.weights_file_name, data=self.data_file_name,
                                                   imgs=self.lineEdit.text())
                if not result:
                    self.model = YOLO(model=self.weights_file_name)
                    return True
                else:
                    QtWidgets.QMessageBox.warning(self, "参数选择", f"未选择的参数：{','.join(result)}")
                    return False
            else:
                return True
        else:
            QtWidgets.QMessageBox.warning(self, "参数选择", f"未选择的模型相关参数参数")
            return False

    def Infer(self):
        """
        根据 start_type 进行推理
        """
        flag = self.load_model()
        if flag:
            if self.start_type == 'video' or self.start_type == 'cap':
                self.cap = cv2.VideoCapture(self.video_path)

                self.pushButton_start.setEnabled(False)
                self.pushButton_end.setEnabled(True)

                if self.worker_thread is None or not self.worker_thread.isRunning():
                    # 开启线程，否则界面会卡死
                    self.worker_thread = WorkerThread(self)
                    self.worker_thread.start()

            elif self.start_type == 'img':
                self.pushButton_start.setEnabled(False)
                img = cv2.imread(self.img_path)
                self.predict_img(img)
                self.pushButton_start.setEnabled(True)

                self.comboBox.clear()
                self.comboBox.addItem('all')
                for name in self.comboBox_name:
                    self.comboBox.addItem(name)
                self.comboBox.setCurrentText("all")

                self.comboBox_2.clear()
                self.comboBox_2.addItem('None')
                for index in self.results_index.keys():
                    self.comboBox_2.addItem(index)
                self.comboBox_2.setCurrentText("None")

            elif self.start_type == 'dir':
                self.pushButton_start.setEnabled(False)
                if self.worker_thread is None or not self.worker_thread.isRunning():
                    self.worker_thread = WorkerThread(self)
                    self.worker_thread.start()

    def InferEnd(self):
        """
        用于视频/摄像头停止推理
        """
        if self.worker_thread is not None and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread = None

            self.pushButton_end.setEnabled(False)
            self.pushButton_start.setEnabled(True)

            self.comboBox.clear()
            self.comboBox.addItem('all')
            for name in self.comboBox_name:
                self.comboBox.addItem(name)
            self.comboBox.setCurrentText("all")

            self.comboBox_2.clear()
            self.comboBox_2.addItem('None')
            for index in self.results_index.keys():
                self.comboBox_2.addItem(index)
            self.comboBox_2.setCurrentText("None")

    def predict_img(self, img):
        """
        推理图片
        """
        start_time = time.time()
        self.result_img_name = os.path.join(self.result_img_path, self.img_name)
        results = self.model.predict(img, imgsz=eval(self.lineEdit.text()), device=self.device,
                                     conf=self.Confidence(), iou=self.IOU(), half=self.half)[0]
        self.end_time = str(round(time.time() - start_time, 4)) + 's'

        if min(results.boxes.shape) != 0:
            self.all_result = []
            self.comboBox_name = []
            for boxs, cls, conf in zip(results.boxes.xyxy.tolist(), results.boxes.cls.tolist(),
                                       results.boxes.conf.tolist()):
                self.all_result.extend([[round(i, 2) for i in boxs] + [results.names[int(cls)]] + [round(conf, 4)]])
                if results.names[int(cls)] not in self.comboBox_name:
                    self.comboBox_name.append(results.names[int(cls)])

            if self.all_result:
                # 保存结果图片
                im_array = results.orig_img
                self.draw = self.draw_info(im_array, self.all_result)
                cv2.imwrite(self.result_img_name, self.draw)

                self.results_index = {f'目标{index + 1}': result for index, result in enumerate(self.all_result)}

                self.input_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 显示识别信息
                self.show_table()
                self.number += 1
        else:
            self.draw = img

        self.ShowSource(self.draw)
        self.clear_info()
        self.label_time.setText(self.end_time)

    def ShowSource(self, img):
        """
        显示图片
        """
        # 获取图片的尺寸
        image_height, image_width, _ = img.shape
        if image_width <= self.label_width and image_height <= self.label_height:
            scaled_pixmap = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif image_width > self.label_width and image_height <= self.label_height:
            scale_factor = self.label_width / image_width
            new_height = image_height * scale_factor
            # 缩放图片以适应QLabel的大小
            scaled_pixmap = cv2.resize(img, (self.label_width, int(new_height)))
            scaled_pixmap = cv2.cvtColor(scaled_pixmap, cv2.COLOR_BGR2RGB)
            self.label_img.resize(self.label_width, int(new_height))
        elif image_width <= self.label_width and image_height > self.label_height:
            scale_factor = self.label_height / image_height
            new_width = image_width * scale_factor
            scaled_pixmap = cv2.resize(img, (int(new_width), self.label_height))
            scaled_pixmap = cv2.cvtColor(scaled_pixmap, cv2.COLOR_BGR2RGB)
            self.label_img.resize(int(new_width), self.label_height)
        else:
            # 缩放图片以适应QLabel的大小
            scaled_pixmap = cv2.resize(img, (self.label_width, self.label_height))
            scaled_pixmap = cv2.cvtColor(scaled_pixmap, cv2.COLOR_BGR2RGB)

        QtImg = QtGui.QImage(scaled_pixmap[:], scaled_pixmap.shape[1], scaled_pixmap.shape[0],
                             scaled_pixmap.shape[1] * 3, QtGui.QImage.Format_RGB888)
        self.label_img.setPixmap(QtGui.QPixmap.fromImage(QtImg))
        self.update()

    def show_table(self):
        """
        将推理结果显示在表格中
        """
        # 显示表格
        self.RowLength = self.RowLength + 1
        self.tableWidget_info.setRowCount(self.RowLength)
        for column, content in enumerate(
                [self.number, self.org_img_save_path, self.input_time, self.all_result, len(self.all_result),
                 self.end_time,
                 self.result_img_name]):
            row = self.RowLength - 1
            item = QtWidgets.QTableWidgetItem(str(content))
            # 居中
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            # 设置字体颜色
            item.setForeground(QColor.fromRgb(197, 223, 250))
            # 创建一个字体对象
            font = QtGui.QFont()
            # 设置字体大小为10
            font.setPointSize(10)
            # 设置字体对象到 QTableWidgetItem
            item.setFont(font)
            self.tableWidget_info.setItem(row, column, item)
        # 滚动到底部
        self.tableWidget_info.scrollToBottom()

    def cell_clicked(self, row):
        """
        表格点击事件
        """
        if self.tableWidget_info.item(row, 1) is None:
            return
        # 图片路径
        self.org_img_save_path = self.tableWidget_info.item(row, 1).text()
        # 识别结果
        self.all_result = eval(self.tableWidget_info.item(row, 3).text())
        # 推理时间
        self.infer_time = self.tableWidget_info.item(row, 5).text()
        # 保存路径
        self.result_img_name = self.tableWidget_info.item(row, 6).text()

        self.results_index = {f'目标{index + 1}': result for index, result in enumerate(self.all_result)}

        self.label_img.clear()
        draw_img = cv2.imread(self.result_img_name)
        self.ShowSource(draw_img)

        names = []
        for data in self.all_result:
            names.append(data[4])
        self.comboBox.clear()
        self.comboBox.addItem('all')
        for name in list(set(names)):
            self.comboBox.addItem(name)
        self.comboBox.setCurrentText("all")

        self.comboBox_2.clear()
        self.comboBox_2.addItem('None')
        for index in self.results_index.keys():
            self.comboBox_2.addItem(index)

        self.label_time.setText(self.infer_time)
        self.clear_info()

    def show_info(self, result):
        """
        显示的坐标和置信度
        """
        self.label_score.setText(str(result[5]))
        self.label_xmin_v.setText(str(result[0]))
        self.label_ymin_v.setText(str(result[1]))
        self.label_xmax_v.setText(str(result[2]))
        self.label_ymax_v.setText(str(result[3]))
        # 刷新界面
        self.update()

    def clear_info(self):
        """
        清除显示的坐标和置信度
        """
        self.label_score.clear()
        self.label_xmin_v.clear()
        self.label_ymin_v.clear()
        self.label_xmax_v.clear()
        self.label_ymax_v.clear()
        # 刷新界面
        self.update()

    @staticmethod
    def check_none_variables(**args):
        """
        用于检测是否有变量被选择
        """
        none_variables = []
        for var_name, var_value in args.items():
            if var_value == '':
                none_variables.append(var_name)
        return none_variables

    def onComboBoxActivated(self):
        """
        图片单个类别查看
        """
        self.selected_text = self.comboBox.currentText()
        if self.all_result:
            lst_info = []
            if self.selected_text != 'all':
                for result in self.all_result:
                    if self.selected_text == result[4]:
                        lst_info.append(result)
            else:
                lst_info = self.all_result

            self.results_index = {f'目标{index + 1}': result for index, result in enumerate(lst_info)}
            self.comboBox_2.clear()
            self.comboBox_2.addItem('None')
            for index in self.results_index.keys():
                self.comboBox_2.addItem(index)

            draw_img = self.draw_info(cv2.imread(self.org_img_save_path), lst_info)
            self.label_img.clear()
            self.ShowSource(draw_img)
            self.clear_info()

    def onComboBoxActivatedDetection(self):
        """
        单个目标查看
        """
        self.selected_text = self.comboBox_2.currentText()
        if self.selected_text != 'None':
            lst_info = self.results_index[self.selected_text]
            draw_img = cv2.imread(self.org_img_save_path)

            draw_img = self.draw_info(draw_img, [lst_info])
            self.label_img.clear()
            self.ShowSource(draw_img)
            self.show_info(lst_info)
        else:
            draw_img = cv2.imread(self.result_img_name)
            self.ShowSource(draw_img)
            self.clear_info()

    def draw_info(self, draw_img, results):
        """
        绘制识别结果
        """
        lw = max(round(sum(draw_img.shape) / 2 * 0.003), 2)  # line width
        tf = max(lw - 1, 1)  # font thickness
        sf = lw / 3  # font scale
        for result in results:
            box = result[:4]
            cls_name = result[4]
            conf = result[5]

            color = self.color[cls_name]
            label = f'{self.names[cls_name]} {conf}'

            p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            # 绘制矩形框
            cv2.rectangle(draw_img, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
            # text width, height
            w, h = cv2.getTextSize(label, 0, fontScale=sf, thickness=tf)[0]
            # label fits outside box
            outside = box[1] - h - 3 >= 0
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            # 绘制矩形框填充
            cv2.rectangle(draw_img, p1, p2, color, -1, cv2.LINE_AA)
            # 绘制标签
            cv2.putText(draw_img, label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                        0, sf, self.color["font"], thickness=2, lineType=cv2.LINE_AA)

        return draw_img

    def write_csv(self):
        """
        导出推理文件信息
        """
        result_csv = os.path.join(self.result_time_path, 'result.csv')

        num_rows = self.tableWidget_info.rowCount()
        num_cols = self.tableWidget_info.columnCount()
        datas = []
        for row in range(num_rows):
            row_data = []
            for col in range(num_cols):
                item = self.tableWidget_info.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            datas.append(row_data)

        with open(result_csv, "w", newline="") as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(['序号', '图片名称', '录入时间', '识别结果', '目标数目', '推理用时', '保存路径'])
            for data in datas:
                writer.writerow(data)

        QMessageBox.information(None, "成功", f"数据已保存！save path {result_csv}", QMessageBox.Yes)

    def closeEvent(self, event):
        """
        界面关闭事件，询问用户是否关闭
        """
        reply = QMessageBox.question(self, '退出', "是否要退出该界面？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.worker_thread is not None:
                # 确保线程安全地停止
                self.worker_thread.terminate()

            self.close()
            event.accept()
        else:
            event.ignore()


class WorkerThread(QThread):
    """
    识别视频/摄像头/文件夹 进程
    """

    def __init__(self, main_window):
        super().__init__()
        self.running = True
        self.main_window = main_window

    def run(self):
        if self.main_window.start_type == 'video' or self.main_window.start_type == "cap":
            if not self.main_window.cap.isOpened():
                raise ValueError("Unable to open video file or cam")
            video_name = self.main_window.img_name if '.mp4' in self.main_window.img_name else \
                self.main_window.img_name.split(".")[0] + '.mp4'
            frame_num = 0
            save_path = os.path.join(self.main_window.result_img_path, video_name)
            fps = 30.0 if 'camera' in video_name else self.main_window.cap.get(cv2.CAP_PROP_FPS)
            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps,
                                         (int(self.main_window.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                          int(self.main_window.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            while self.running:
                self.main_window.img_name = video_name.split(".")[0] + '_' + str(frame_num) + '.jpg'

                ret, frame = self.main_window.cap.read()
                if ret:
                    self.main_window.org_img_save_path = os.path.join(self.main_window.result_org_img_path,
                                                                      self.main_window.img_name)
                    cv2.imwrite(self.main_window.org_img_save_path, frame)

                    self.main_window.predict_img(frame)

                    frame_num += 1

                    vid_writer.write(self.main_window.draw)
                else:
                    break
            self.main_window.cap.release()
            vid_writer.release()

        elif self.main_window.start_type == 'dir':
            for img_path in self.main_window.image_files:
                img = cv2.imread(img_path)
                self.main_window.img_name = os.path.split(img_path)[-1]
                self.main_window.org_img_save_path = os.path.join(self.main_window.result_org_img_path,
                                                                  self.main_window.img_name)
                shutil.copy(img_path, self.main_window.org_img_save_path)
                self.main_window.predict_img(img)

        self.main_window.comboBox.clear()
        self.main_window.comboBox.addItem('all')
        for name in self.main_window.comboBox_name:
            self.main_window.comboBox.addItem(name)
        self.main_window.comboBox.setCurrentText("all")

        self.main_window.comboBox_2.clear()
        self.main_window.comboBox_2.addItem('None')
        for index in self.main_window.results_index.keys():
            self.main_window.comboBox_2.addItem(index)
        self.main_window.comboBox_2.setCurrentText("None")

        self.main_window.pushButton_end.setEnabled(False)
        self.main_window.pushButton_start.setEnabled(True)

    def stop(self):
        self.running = False
        self.wait()


def main():
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
