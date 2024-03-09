import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import requests
import re
import time
from bs4 import BeautifulSoup
import json
from login import login
from xkqk import xkqk
import os
import subprocess
from clear import clear
monitor_process = None
is_auto_submitting = False
jianting_process = None


def open_config_window_if_empty():
    try:
        with open("config.json", "r") as json_file:
            config_data = json.load(json_file)
        if not config_data.get("XH") or not config_data.get("PWD") or not config_data.get("TO_EMAIL") or not config_data.get("URL"):
            open_config_window()
            messagebox.showinfo("提示","请先设置配置信息")
    except FileNotFoundError:
        open_config_window()


def on_close():
    global monitor_process
    if monitor_process and monitor_process.poll() is None:
        monitor_process.terminate()
        monitor_process.wait()
    root.destroy()

def get_login_url():
    max_try = 0
    while max_try < 3 :
        try:
            config = None
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            if config:
                login_url = login(config["URL"], config["XH"], config["PWD"])
                if "string indices must be integers" in login_url:
                    show_log("Cookies已经过期，正在重新获取")
                else:
                    show_log(f"登录后的页面URL: {login_url}", True)
                    break
        except Exception as e:
            show_alert(f"获取登录URL失败：{str(e)}")
            clear()
            time.sleep(1)
        max_try += 1



def get_current_selection():
    try:
        config = None
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        if config:
            result = xkqk(config["MAINURL"])
            i = 0
            show_log("当前选课情况:", True)
            for item in result:
                i += 1
                show_log(f'{i}.{item}', False)

    except Exception as e:
        show_alert(f"获取选课情况失败：{str(e)}")

def start_stop_monitor():
    global jianting_process
    if jianting_process is None:
        try:
            jianting_process = subprocess.Popen(["jianting.exe"], text=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            show_log("监听执行中", True)
        except Exception as e:
            show_alert(f"启动监听失败：{str(e)}")
    else:
        try:
            jianting_process.terminate()
            jianting_process.wait()
            show_alert("已经关闭监听")
            jianting_process = None
        except Exception as e:
            show_alert(f"结束监听失败：{str(e)}")

def open_config_window():
    config_window = tk.Toplevel(main_frame)
    config_window.title("修改配置文件")
    config_window.attributes('-topmost',True)
    labels = ["学号:", "密码:", "邮箱:", "教务系统URL:","有容量的xkkh:","系统主页","Cookies"]
    names = ['XH', 'PWD', 'TO_EMAIL', 'URL',"XKKH","MAINURL","COOKIES"]
    entries = [tk.Entry(config_window, width=40) for _ in range(len(labels))]

    try:
        with open("config.json", "r") as json_file:
            config_data = json.load(json_file)
            for entry, name in zip(entries, names):
                entry.insert(0, config_data.get(name, ""))
    except FileNotFoundError:
        pass

    for label, entry in zip(labels, entries):
        tk.Label(config_window, text=label).grid(sticky="w", padx=10, pady=5)
        entry.grid(sticky="w", padx=10, pady=5)

    def save_config():
        try:
            with open("config.json", "r") as json_file:
                config_data = json.load(json_file)

            for name, entry in zip(names, entries):
                config_data[name] = entry.get()

            with open("config.json", "w") as json_file:
                json.dump(config_data, json_file, indent=4)

            config_window.destroy()
            messagebox.showinfo("成功", "配置文件已更新")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存配置文件：{str(e)}")

    button_save = tk.Button(config_window, text="保存", command=save_config)
    button_save.grid(row=2*len(labels), column=0, columnspan=4, pady=10)

def show_log(message, is_time=False):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_message = f"[{current_time}] {message}\n" if is_time else f"{message}\n"
    text_result.config(state=tk.NORMAL)
    text_result.insert(tk.END, log_message)
    text_result.yview(tk.END)
    text_result.config(state=tk.DISABLED)

def show_alert(alert_message):
    show_log(alert_message, True)

def extract_alert(response_text):
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

def submit_form():
    server_script_url = entry_server_script_url.get()
    is_textbook_ordered = radio_var.get()
    course_codes = [entry.get() for entry in entry_course_codes]
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
            response = requests.post(server_script_url, data=form_data,cookies=cookies)
            if response.status_code == 200:
                content = extract_alert(response.text)
                alert_message = f"第{i}个：" + content
                show_log(alert_message, True)
                if "教师" in content or "重修" in content:
                    with open('config.json', 'r') as config_file:
                        config = json.load(config_file)
                    if config:
                        show_log("已经自动重新获取选课URL", True)
                        login(config["URL"],config["XH"],config["PWD"])
                        auto_fill()
            else:
                show_alert(f"请求失败，状态码: {response.status_code}")

def auto_submit_form():
    global is_auto_submitting
    if is_auto_submitting:
        submit_form()
        main_frame.after(int(float(custom_interval.get()) * 1000), auto_submit_form)

def toggle_auto_submitting():
    global is_auto_submitting
    is_auto_submitting = not is_auto_submitting
    if is_auto_submitting:
        show_log("已开始自动抢课", True)
        auto_submit_form()
    else:
        show_log("已停止自动抢课", True)

def auto_fill():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        if config:
            baseurl=config["MAINURL"]
            xkkh = config["XKKH"]
            xh = config["XH"]
            xkurl = re.match(r"(http?://[^/]+/[^/]+/)", baseurl).group(1)
            result = xkurl+"xsxjs.aspx?xkkh="+xkkh+"&xh="+xh
            if result == "三秒防刷":
                show_log(result, True)
            else:
                entry_server_script_url.delete(0, tk.END)
                entry_server_script_url.insert(0, result)
                show_log(f"获取到的URL为:\n{result}", True)
    except Exception as e:
        show_log(e, True)
        entry_server_script_url.delete(0, tk.END)
        show_log(0, "自动填充失败")

def add_course_entry():
    new_entry = tk.Entry(main_frame, width=40)
    new_entry.grid(row=len(entry_course_codes) + 3, column=1, padx=10, pady=5, sticky="w")
    entry_course_codes.append(new_entry)
    if len(entry_course_codes)>2:
        adjust_layout()

def remove_course_entry():
    if len(entry_course_codes) > 1:
        entry_to_remove = entry_course_codes.pop()
        entry_to_remove.destroy()
        if len(entry_course_codes) > 1:
            adjust_layout()

def get_logged_in_url():
    try:
        server_script_url = entry_server_script_url.get()
        logged_in_url = login(server_script_url)
        show_log(f"登录后页面URL: {logged_in_url}", True)
    except Exception as e:
        show_alert(f"获取登录后页面URL失败：{str(e)}")
def open_selection_editor():
    selection_editor_window = tk.Toplevel(main_frame)
    selection_editor_window.title("选课代码编辑器")

    # 读取选课代码.txt文件内容
    file_path = "选课代码.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().splitlines()
    else:
        content = []

    listbox_editor = tk.Listbox(selection_editor_window, selectmode=tk.SINGLE, height=20, width=50)
    listbox_editor.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    # 填充Listbox
    for item in content:
        listbox_editor.insert(tk.END, item)

    def add_course():
        new_course = simpledialog.askstring("添加选课号", "请在输入新的选课号（格式形如\"(2023-2024-2)-BBA306-20064057-1\"，不包含引号）:")
        if new_course:
            listbox_editor.insert(tk.END, new_course)

    def delete_courses():
        selected_indices = listbox_editor.curselection()
        for index in reversed(selected_indices):
            listbox_editor.delete(index)

    def edit_course(event):
        selected_index = listbox_editor.curselection()
        if selected_index:
            selected_course = listbox_editor.get(selected_index[0])
            edited_course = simpledialog.askstring("编辑选课号", f"修改选课号 '{selected_course}'为:", initialvalue=selected_course)
            if edited_course and edited_course != selected_course:
                listbox_editor.delete(selected_index[0])
                listbox_editor.insert(selected_index[0], edited_course)

    def save_and_close():
        with open(file_path, "w", encoding="utf-8") as file:
            for i in range(listbox_editor.size()):
                file.write(listbox_editor.get(i) + "\n")
        selection_editor_window.destroy()

    def on_select(event):
        selection_editor_window.drag_data = {'x': event.x, 'y': event.y, 'selected': listbox_editor.nearest(event.y)}

    def on_release(event):
        if hasattr(selection_editor_window, 'drag_data'):
            del selection_editor_window.drag_data

    def on_drag(event):
        if hasattr(selection_editor_window, 'drag_data'):
            selected_index = selection_editor_window.drag_data['selected']
            new_index = listbox_editor.nearest(event.y)
            if new_index != selected_index:
                text = listbox_editor.get(selected_index)
                listbox_editor.delete(selected_index)
                listbox_editor.insert(new_index, text)
                selection_editor_window.drag_data['selected'] = new_index

    listbox_editor.bind("<Double-1>", edit_course)  # 绑定双击事件
    listbox_editor.bind("<<ListboxSelect>>", on_select)  # 绑定列表选择事件
    listbox_editor.bind("<B1-Motion>", on_drag)  # 绑定鼠标拖拽事件
    listbox_editor.bind("<ButtonRelease-1>", on_release)  # 绑定鼠标释放事件

    button_add_course = tk.Button(selection_editor_window, text="添加选课号", command=add_course)
    button_add_course.grid(row=1, column=0, pady=5)

    button_delete_courses = tk.Button(selection_editor_window, text="删除选中课程", command=delete_courses)
    button_delete_courses.grid(row=1, column=2, pady=5)

    button_save_close = tk.Button(selection_editor_window, text="保存并关闭", command=save_and_close)
    button_save_close.grid(row=1, column=1, columnspan=1, pady=5)

def clearlogin():
    clear()
    show_log("已清空MAINURL和COOKIES",True)
def load_selection_codes():
    try:
        file_path = "选课代码.txt"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read().splitlines()
                for i, code in enumerate(content, start=1):
                    if i <= len(entry_course_codes):
                        entry_course_codes[i - 1].delete(0, tk.END)
                        entry_course_codes[i - 1].insert(tk.END, code)
                    else:
                        add_course_entry()
                        entry_course_codes[-1].delete(0, tk.END)
                        entry_course_codes[-1].insert(tk.END, code)
                show_alert("已全部填充完毕")
        else:
            show_alert("选课代码.txt 文件不存在")
    except Exception as e:
        show_alert(f"加载选课代码失败：{str(e)}")
def adjust_layout():
    for idx, entry in enumerate(entry_course_codes, start=3):
        entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        button_start_stop_monitor.grid(row=len(entry_course_codes) + 8, column=0, columnspan=1, pady=10)
        button_submit.grid(row=len(entry_course_codes) + 4, column=1, columnspan=2, pady=10)
        label_custom_interval.grid(row=len(entry_course_codes) + 3, column=0, padx=10, pady=5, sticky="w")
        custom_interval.grid(row=len(entry_course_codes) + 3, column=1, padx=10, pady=5, sticky="w")
        button_auto_submit.grid(row=len(entry_course_codes) + 4, column=0, columnspan=2, pady=5)
        button_get_selection.grid(row=len(entry_course_codes) + 8, column=2, columnspan=1, pady=10)
        text_result.grid(row=len(entry_course_codes) + 7, column=0, columnspan=3, pady=10)
        button_get_login_url.grid(row=len(entry_course_codes) + 8, column=1, columnspan=1, pady=10)





root = tk.Tk()
root.title("西财教务系统脚本")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.protocol("WM_DELETE_WINDOW", on_close)
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10)
button_load_codes = tk.Button(main_frame, text="填充选课代码", command=load_selection_codes)
button_load_codes.grid(row=4, column=0, pady=5)
label_server_script_url = tk.Label(main_frame, text="本专业选课界面URL：")
entry_server_script_url = tk.Entry(main_frame, width=40)
label_code = tk.Label(main_frame, text="选课代码(参考全校课表)：")
label_textbook_ordered = tk.Label(main_frame, text="是否订购教材：")
radio_var = tk.StringVar(value="0")
radio_button_yes = ttk.Radiobutton(main_frame, text="是", variable=radio_var, value="1")
radio_button_no = ttk.Radiobutton(main_frame, text="否", variable=radio_var, value="0")

entry_course_codes = [tk.Entry(main_frame, width=40)]
entry_course_codes[0].grid(row=3, column=1, padx=10, pady=5, sticky="w")
button_start_stop_monitor = tk.Button(main_frame, text="启动监听", command=start_stop_monitor)
button_start_stop_monitor.grid(row=len(entry_course_codes) + 9, column=0, columnspan=1, pady=10)
button_add_entry = tk.Button(main_frame, text="添加选课代码文本框", command=add_course_entry)
button_add_entry.grid(row=3, column=2, padx=10, pady=5)
button_remove_entry = tk.Button(main_frame, text="删除选课代码文本框", command=remove_course_entry)
button_remove_entry.grid(row=4, column=2, padx=10, pady=5)
button_submit = tk.Button(main_frame, text="提交", command=submit_form)
button_submit.grid(row=len(entry_course_codes) + 5, column=1, columnspan=2, pady=10)
button_get_login_url = tk.Button(main_frame, text="获取登录URL", command=get_login_url)
button_get_login_url.grid(row=len(entry_course_codes) + 9, column=1, columnspan=1, pady=10)

button_get_login_url = tk.Button(main_frame, text="清空登录状态", command=clearlogin)
button_get_login_url.grid(row=6, column=1, columnspan=1, pady=5)

button_config_window = tk.Button(main_frame, text="修改配置文件", command=open_config_window)
button_config_window.grid(row=5, column=2, pady=5)
button_get_selection = tk.Button(main_frame, text="获取当前选课情况", command=get_current_selection)
button_get_selection.grid(row=len(entry_course_codes) + 9, column=2, columnspan=1, pady=10)
label_custom_interval = tk.Label(main_frame, text="抢课间隔（秒）：")
custom_interval = tk.Entry(main_frame, width=10)
custom_interval.insert(tk.END, "1")
button_edit_selection = tk.Button(main_frame, text="编辑选课号", command=open_selection_editor)
button_edit_selection.grid(row= 6, column=2, pady=5)
button_auto_submit = tk.Button(main_frame, text="自动抢课", command=toggle_auto_submitting)
button_auto_fill = tk.Button(main_frame, text="自动填充", command=auto_fill)

text_result = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, width=70, state=tk.DISABLED)
text_result.grid(row=7, column=0, columnspan=5, pady=10)

label_server_script_url.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_server_script_url.grid(row=0, column=1, padx=10, pady=5, sticky="w")
label_code.grid(row=3, column=0, padx=5, pady=1, sticky='w')
label_textbook_ordered.grid(row=1, column=0, padx=10, pady=5, sticky="w")
radio_button_yes.grid(row=1, column=1, padx=10, pady=5, sticky="w")
radio_button_no.grid(row=1, column=2, padx=10, pady=5, sticky="w")
button_auto_fill.grid(row=0, column=2, padx=10, pady=5)

label_custom_interval.grid(row=5, column=0, padx=10, pady=5, sticky="w")
custom_interval.grid(row=5, column=1, padx=10, pady=5, sticky="w")
button_auto_submit.grid(row=6, column=0, columnspan=2, pady=5)
open_config_window_if_empty()
root.mainloop()
