import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QMainWindow
import mysql.connector
from PyQt5.uic import loadUiType
from mysql.connector import Error

main_ui, _ = loadUiType('./UI/vnf_admin.ui')



def create_connection():
    return mysql.connector.connect(
        host='localhost',
        database='vegetable',
        user='root',
        password='SUNYUHANG'  # 替换为实际的数据库密码
    )

def query_product_names():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM vp")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Error as e:
        print(f"查询产品名称失败: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_product_details(name):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name, price, num, category FROM vp WHERE name = %s", (name,))
        row = cursor.fetchone()
        return row
    except Error as e:
        print(f"查询产品详情失败: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_product(name, price, num, category):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO vp (name, price, num, category) VALUES (%s, %s, %s, %s)",
                       (name, price, num, category))
        connection.commit()
        return True
    except Error as e:
        print(f"添加产品失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_product(name, price, num, category):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE vp SET price = %s, num = %s, category = %s WHERE name = %s",
                       (price, num, category, name))
        connection.commit()
        return True
    except Error as e:
        print(f"更新产品失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_product(name):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM vp WHERE name = %s", (name,))
        connection.commit()
        return True
    except Error as e:
        print(f"删除产品失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
class VnF_admin(QMainWindow, main_ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)


        # 连接按钮
        self.pushButton_add.clicked.connect(self.add_product)
        self.pushButton_update.clicked.connect(self.update_product)
        self.pushButton_delete.clicked.connect(self.delete_product)
        self.comboBox.currentIndexChanged.connect(self.load_product_details)




        # 加载产品名称
        self.load_product_names()


    def load_product_names(self):
        products = query_product_names()
        self.comboBox.clear()
        self.comboBox.addItem("")  # 添加一个空选项
        self.comboBox.addItems(products)

    def load_product_details(self):
        name = self.comboBox.currentText()
        if name:
            details = get_product_details(name)
            if details:
                self.lineEdit_name.setText(details[0])
                self.lineEdit_price.setText(str(details[1]))
                self.lineEdit_num.setText(str(details[2]))
                self.lineEdit_category.setText(details[3])
        else:
            self.lineEdit_name.clear()
            self.lineEdit_price.clear()
            self.lineEdit_num.clear()
            self.lineEdit_category.clear()

    def add_product(self):
        name = self.lineEdit_name.text()
        price = self.lineEdit_price.text()
        num = self.lineEdit_num.text()
        category = self.lineEdit_category.text()

        if name and price and num and category:
            if add_product(name, float(price), int(num), category):
                QMessageBox.information(self, "成功", "产品添加成功！")
                self.load_product_names()
            else:
                QMessageBox.warning(self, "失败", "产品添加失败。")
        else:
            QMessageBox.warning(self, "输入错误", "请填写所有字段。")

    def update_product(self):
        name = self.lineEdit_name.text()
        price = self.lineEdit_price.text()
        num = self.lineEdit_num.text()
        category = self.lineEdit_category.text()

        if name and price and num and category:
            if update_product(name, float(price), int(num), category):
                QMessageBox.information(self, "成功", "产品更新成功！")
            else:
                QMessageBox.warning(self, "失败", "产品更新失败。")
        else:
            QMessageBox.warning(self, "输入错误", "请填写所有字段。")

    def delete_product(self):
        name = self.lineEdit_name.text()
        if name:
            if delete_product(name):
                QMessageBox.information(self, "成功", "产品删除成功！")
                self.load_product_names()
            else:
                QMessageBox.warning(self, "失败", "产品删除失败。")
        else:
            QMessageBox.warning(self, "选择错误", "请先选择一个产品。")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = VnF_admin()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
