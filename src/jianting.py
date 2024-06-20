# jianting.py
import time
import difflib
from xkqk import xkqk
from login import login
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json  # 添加这一行
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return None

def get_diff(content1, content2):
    differ = difflib.Differ()
    diff = list(differ.compare(content1.splitlines(), content2.splitlines()))
    return diff
def stmp(content,list):
    # 创建邮件内容
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "选课成功!{}".format(content)
    # 邮件正文
    body = "恭喜你成功选到了\n{}\n\n目前选课情况:\n{}".format(content,list)
    message.attach(MIMEText(body, "plain"))
    # 连接到SMTP服务器
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 使用TLS加密连接
        server.login(from_email, password)
    except Exception as e:
        print("无法连接到SMTP服务器:", e)
    # 发送邮件
    try:
        server.sendmail(from_email, to_email, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败:", e)
    # 退出SMTP服务器
    server.quit()
def jianting():
    # 获取初始文件内容
    config = None
    with open('config.json', 'r',encoding='utf-8') as config_file:
        config = json.load(config_file)
    if config:
        global smtp_server,smtp_port,from_email,password,to_email,file_path,url,xh,pwd,load
        file_path = config["FILE_PATH"]
        smtp_server = config["SMTP_SERVER"]
        smtp_port = config["SMTP_PORT"]
        from_email = config["FROM_EMAIL"]
        password = "ojcxbljvpbxehijh"
        to_email = config["TO_EMAIL"]
        url = config["URL"]
        xh = config["XH"]
        pwd = config["PWD"]
        load = config["MAINURL"]
    last_content = read_file_content(file_path)
    while True:
        # 等待一分钟
        get = xkqk(load)
        if type(get)!=list:
            print(get)
        else:
            # 读取当前文件内容
            current_content = read_file_content(file_path)
            print(current_content)
            different_str=[]
            if current_content is not None and current_content != last_content:
                # 找出具体的差异并打印
                diff=get_diff(last_content, current_content)
                for x in diff:
                    if x[0]=='+':
                        different_str.append(x)
                    else:
                        continue
                if len(different_str)>=1:
                    print("文件内容发生变化！",different_str)
                    # 在这里可以添加处理文件内容变化的逻 辑
                    stmp(different_str,diff)
                last_content = current_content
        time.sleep(60)
if __name__ == "__main__":
    print("监听启动中...")
    jianting()

