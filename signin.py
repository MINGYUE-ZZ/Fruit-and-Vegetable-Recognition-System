# -*- coding:utf-8 -*-
# @author: syh

import sys
import mysql.connector
from PyQt5.uic import loadUiType
from mysql.connector import Error
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QMainWindow
from GUI import MainGui
from vng_admin import VnF_admin
# UI--Logic分离
main_ui, _ = loadUiType('./UI/signin.ui')


class Sign(QMainWindow, main_ui):
    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_buttons()
        self.other_window = None  # 初始化为 None



    def handle_buttons(self):
        self.pushButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.register)
        self.radioButton_user.toggled.connect(self.on_radio_toggled)
        self.radioButton_admin.toggled.connect(self.on_radio_toggled)






    def on_radio_toggled(self):
        if self.radioButton_user.isChecked():
            QMessageBox.information(self, "提示", "普通用户选中！")
            # 这里执行普通用户选中后的操作，例如显示特定信息或者执行特定函数
        elif self.radioButton_admin.isChecked():
            QMessageBox.information(self, "提示", "管理员选中！")
            # 这里执行管理员选中后的操作，例如显示特定信息或者执行特定函数
    def login(self):
        username = self.lineEdit_1.text()
        password = self.lineEdit_2.text()

        if self.radioButton_user.isChecked():
            role = "user"
        elif self.radioButton_admin.isChecked():
            role = "admin"
        else:
            QMessageBox.warning(self, "警告", "请选择用户类型！")
            return

        if self.validate_login(username, password):
            QMessageBox.information(self, "成功", "登录成功！")
            self.open_window(role)
        else:
            QMessageBox.warning(self, "失败", "用户名或密码错误。")

    def validate_login(self, username, password):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='vegetable',
                user='root',
                password='SUNYUHANG'
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM idnpwd WHERE id = %s AND password = %s", (username, password))
                record = cursor.fetchone()
                if record:
                    return True
        except Error as e:
            QMessageBox.critical(self, "错误", f"数据库连接失败: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return False

    def register(self):
        username = self.lineEdit_1.text()
        password = self.lineEdit_2.text()
        if self.validate_registration(username, password):
            QMessageBox.information(self, "成功", "注册成功！")
        else:
            QMessageBox.warning(self, "失败", "用户名已存在或其他错误。")

    def validate_registration(self, username, password):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='vegetable',
                user='root',
                password='SUNYUHANG'
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM idnpwd WHERE id = %s", (username,))
                record = cursor.fetchone()
                if record:
                    return False
                cursor.execute("INSERT INTO idnpwd (id, password) VALUES (%s, %s)", (username, password))
                connection.commit()
                return True
        except Error as e:
            QMessageBox.critical(self, "错误", f"数据库连接失败: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return False

    def open_window(self, role):
        self.hide()  # 隐藏登录窗口
        if role == "user":
            self.other_window = MainGui()  # 创建普通用户界面对象
        else:
            self.other_window = VnF_admin()  # 创建管理员界面对象
        self.other_window.show()  # 显示另一个界面


def main():
    app = QApplication(sys.argv)
    window = Sign()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()