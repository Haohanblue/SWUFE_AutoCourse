import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QRadioButton, QButtonGroup,
    QMessageBox, QFileDialog, QScrollArea, QFrame, QDialog,
    QTextEdit, QFormLayout, QListWidget, QInputDialog
)
import requests
import re
import time
from bs4 import BeautifulSoup
import json
import subprocess
import os

from login import login
from xkqk import xkqk
from clear import clear

monitor_process = None
is_auto_submitting = False
jianting_process = None


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改配置文件")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.entries = {}
        labels = ["学号:", "密码:", "邮箱:", "教务系统URL:", "有容量的xkkh:", "系统主页", "Cookies"]
        names = ['XH', 'PWD', 'TO_EMAIL', 'URL', "XKKH", "MAINURL", "COOKIES"]

        try:
            with open("config.json", "r") as json_file:
                config_data = json.load(json_file)
                for label, name in zip(labels, names):
                    entry = QLineEdit(config_data.get(name, ""))
                    layout.addRow(QLabel(label), entry)
                    self.entries[name] = entry
        except FileNotFoundError:
            for label, name in zip(labels, names):
                entry = QLineEdit()
                layout.addRow(QLabel(label), entry)
                self.entries[name] = entry

        button_save = QPushButton("保存")
        button_save.clicked.connect(self.save_config)
        layout.addRow(button_save)

        self.setLayout(layout)

    def save_config(self):
        try:
            with open("config.json", "r") as json_file:
                config_data = json.load(json_file)

            for name, entry in self.entries.items():
                config_data[name] = entry.text()

            with open("config.json", "w") as json_file:
                json.dump(config_data, json_file, indent=4)
            QMessageBox.information(self, "成功", "配置文件已更新")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存配置文件：{str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("西财教务系统脚本")
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.main_layout = QVBoxLayout()

        self.server_script_url = QLineEdit()
        self.course_code_entries = [QLineEdit()]

        self.init_main_controls()
        self.init_course_controls()
        self.init_log_area()

        main_widget.setLayout(self.main_layout)

    def init_main_controls(self):
        self.main_layout.addWidget(QLabel("本专业选课界面URL："))
        self.main_layout.addWidget(self.server_script_url)

        button_load_codes = QPushButton("填充选课代码")
        button_load_codes.clicked.connect(self.load_selection_codes)
        self.main_layout.addWidget(button_load_codes)

        self.radio_group = QButtonGroup()
        radio_button_yes = QRadioButton("是")
        radio_button_no = QRadioButton("否")
        radio_button_no.setChecked(True)
        self.radio_group.addButton(radio_button_yes, 1)
        self.radio_group.addButton(radio_button_no, 0)

        self.main_layout.addWidget(QLabel("是否订购教材："))
        self.main_layout.addWidget(radio_button_yes)
        self.main_layout.addWidget(radio_button_no)

    def init_course_controls(self):
        self.course_layout = QVBoxLayout()

        self.course_layout.addWidget(QLabel("选课代码(参考全校课表)："))
        for entry in self.course_code_entries:
            self.course_layout.addWidget(entry)

        button_add_entry = QPushButton("添加选课代码文本框")
        button_add_entry.clicked.connect(self.add_course_entry)
        self.course_layout.addWidget(button_add_entry)

        button_remove_entry = QPushButton("删除选课代码文本框")
        button_remove_entry.clicked.connect(self.remove_course_entry)
        self.course_layout.addWidget(button_remove_entry)

        button_submit = QPushButton("提交")
        button_submit.clicked.connect(self.submit_form)
        self.course_layout.addWidget(button_submit)

        button_auto_submit = QPushButton("自动抢课")
        button_auto_submit.clicked.connect(self.toggle_auto_submitting)
        self.course_layout.addWidget(button_auto_submit)

        button_auto_fill = QPushButton("自动填充")
        button_auto_fill.clicked.connect(self.auto_fill)
        self.course_layout.addWidget(button_auto_fill)

        button_get_login_url = QPushButton("获取登录URL")
        button_get_login_url.clicked.connect(self.get_login_url)
        self.course_layout.addWidget(button_get_login_url)

        button_get_selection = QPushButton("获取当前选课情况")
        button_get_selection.clicked.connect(self.get_current_selection)
        self.course_layout.addWidget(button_get_selection)

        button_config_window = QPushButton("修改配置文件")
        button_config_window.clicked.connect(self.open_config_window)
        self.course_layout.addWidget(button_config_window)

        button_start_stop_monitor = QPushButton("启动监听")
        button_start_stop_monitor.clicked.connect(self.start_stop_monitor)
        self.course_layout.addWidget(button_start_stop_monitor)

        self.custom_interval = QLineEdit("1")
        self.course_layout.addWidget(QLabel("抢课间隔（秒）："))
        self.course_layout.addWidget(self.custom_interval)

        self.main_layout.addLayout(self.course_layout)

    def init_log_area(self):
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.main_layout.addWidget(self.log_area)

    def show_log(self, message, is_time=False):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_message = f"[{current_time}] {message}\n" if is_time else f"{message}\n"
        self.log_area.append(log_message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def show_alert(self, alert_message):
        self.show_log(alert_message, True)

    def add_course_entry(self):
        new_entry = QLineEdit()
        self.course_code_entries.append(new_entry)
        self.course_layout.insertWidget(len(self.course_code_entries), new_entry)

    def remove_course_entry(self):
        if len(self.course_code_entries) > 1:
            entry_to_remove = self.course_code_entries.pop()
            self.course_layout.removeWidget(entry_to_remove)
            entry_to_remove.deleteLater()

    def open_config_window(self):
        config_dialog = ConfigDialog(self)
        config_dialog.exec()

    def load_selection_codes(self):
        try:
            file_path = "选课代码.txt"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read().splitlines()
                    for i, code in enumerate(content, start=1):
                        if i <= len(self.course_code_entries):
                            self.course_code_entries[i - 1].setText(code)
                        else:
                            self.add_course_entry()
                            self.course_code_entries[-1].setText(code)
                    self.show_alert("已全部填充完毕")
            else:
                self.show_alert("选课代码.txt 文件不存在")
        except Exception as e:
            self.show_alert(f"加载选课代码失败：{str(e)}")

    def submit_form(self):
        server_script_url = self.server_script_url.text()
        is_textbook_ordered = self.radio_group.checkedId()
        course_codes = [entry.text() for entry in self.course_code_entries]
        config = None
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        if config:
            cookies = config["COOKIES"]
        for i, course_code in enumerate(course_codes, start=1):
            if course_code != "":
                form_data = {
                    'serverScriptUrl': server_script_url,
                    'RadioButtonList1': is_textbook_ordered,
                    'xkkh': course_code,
                    '__EVENTTARGET': 'Button1',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATEGENERATOR': 'AC27D4D4'
                }
                response = requests.post(server_script_url, data=form_data, cookies=cookies)
                if response.status_code == 200:
                    content = self.extract_alert(response.text)
                    alert_message = f"第{i}个：" + content
                    self.show_log(alert_message, True)
                    if "教师" in content or "重修" in content:
                        with open('config.json', 'r') as config_file:
                            config = json.load(config_file)
                        if config:
                            self.show_log("已经自动重新获取选课URL", True)
                            login(config["URL"], config["XH"], config["PWD"])
                            self.auto_fill()
                else:
                    self.show_alert(f"请求失败，状态码: {response.status_code}")

    def extract_alert(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        alert_message = soup.find('script', language="javascript").text
        alert_content = re.search(r"alert\('(.*?)'\);", alert_message)
        if alert_content:
            return alert_content.group(1)
        else:
            message = soup.find_all('script')[-1].text
            alert_content = re.search(r"alert\('(.*?)'\);", message)
            if alert_content:
                content = alert_content.group(1)
                return content
            else:
                return "出现错误"

    def toggle_auto_submitting(self):
        global is_auto_submitting
        is_auto_submitting = not is_auto_submitting
        if is_auto_submitting:
            self.show_log("已开始自动抢课", True)
            self.auto_submit_form()
        else:
            self.show_log("已停止自动抢课", True)

    def auto_submit_form(self):
        global is_auto_submitting
        if is_auto_submitting:
            self.submit_form()
            QTimer.singleShot(int(float(self.custom_interval.text()) * 1000), self.auto_submit_form)

    def get_login_url(self):
        try:
            max_try = 0
            while max_try < 3:
                try:
                    config = None
                    with open('config.json', 'r') as config_file:
                        config = json.load(config_file)
                    if config:
                        login_url = login(config["URL"], config["XH"], config["PWD"])
                        if "string indices must be integers" in login_url:
                            self.show_log("Cookies已经过期，正在重新获取")
                        else:
                            self.show_log(f"登录后的页面URL: {login_url}", True)
                            break
                except Exception as e:
                    self.show_alert(f"获取登录URL失败：{str(e)}")
                    clear()
                    time.sleep(1)
                max_try += 1
        except Exception as e:
            self.show_alert(f"获取登录URL失败：{str(e)}")

    def start_stop_monitor(self):
        global jianting_process
        if jianting_process is None:
            try:
                jianting_process = subprocess.Popen(["jianting.exe"], text=True,
                                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.show_log("监听执行中", True)
            except Exception as e:
                self.show_alert(f"启动监听失败：{str(e)}")
        else:
            try:
                jianting_process.terminate()
                jianting_process.wait()
                self.show_alert("已经关闭监听")
                jianting_process = None
            except Exception as e:
                self.show_alert(f"结束监听失败：{str(e)}")

    def get_current_selection(self):
        try:
            config = None
            with open('./config.json', 'r') as config_file:
                config = json.load(config_file)
            if config:
                result = xkqk(config["MAINURL"])
                i = 0
                self.show_log("当前选课情况:", True)
                for item in result:
                    i += 1
                    self.show_log(f'{i}.{item}', False)
        except Exception as e:
            self.show_alert(f"获取选课情况失败：{str(e)}")

    def auto_fill(self):
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            if config:
                baseurl = config["MAINURL"]
                xkkh = config["XKKH"]
                xh = config["XH"]
                xkurl = re.match(r"(http?://[^/]+/[^/]+/)", baseurl).group(1)
                result = xkurl + "xsxjs.aspx?xkkh=" + xkkh + "&xh=" + xh
                if result == "三秒防刷":
                    self.show_log(result, True)
                else:
                    self.server_script_url.setText(result)
                    self.show_log(f"获取到的URL为:\n{result}", True)
        except Exception as e:
            self.show_log(str(e), True)
            self.server_script_url.setText("自动填充失败")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
