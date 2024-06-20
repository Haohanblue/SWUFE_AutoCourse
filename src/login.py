# login.py
import time
import requests
import os
import ddddocr
from bs4 import BeautifulSoup
import re
import json
import ast
def read_config(file_path='./config.json'):  # 修改这一行
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r',encoding='utf-8') as file:
        config_data = json.load(file)  # 修改这一行
    return config_data
def login(url, xh, pwd,timeout=3):
    try:
        config = read_config()  # 修改这一行
        mainurl = config['MAINURL']
        cookies = config['COOKIES']
        if cookies and type(cookies) == str:
            cookies = ast.literal_eval(cookies)
        #现获取MAINURL，看看MAINURL的格式是否正确
        if mainurl=="" or mainurl[-8:]!=xh or cookies == "":
            login_url=requests.get(url).url

        else:
            x = requests.get(mainurl,timeout=timeout,cookies=cookies)
            login_url = x.url
        if login_url[-8:]==xh:

            return login_url
        else:

            ocr = ddddocr.DdddOcr(show_ad=False)
            captcha_url = re.match(r"(http?://[^/]+/[^/]+/)", login_url).group(1)+"CheckCode.aspx"
            # 获取登录页面，以便获取验证码
            session = requests.Session()
            index = session.get(login_url,timeout=timeout)
            img = session.get(captcha_url,stream=True,timeout=timeout)
            set_cookie_header = index.headers.get('Set-Cookie')
            soup = BeautifulSoup(index.content, 'lxml')
            value1 = soup.find('input', {'name': "__VIEWSTATE"}).get('value')
            value2 = soup.find('input', {'name': "__VIEWSTATEGENERATOR"}).get('value')
            with open('captcha.gif', 'wb') as file:
                file.write(img.content)
            with open('captcha.gif', 'rb') as f:
                img_bytes = f.read()
            captcha_text = ocr.classification(img_bytes)
            if len(captcha_text) == 4 and captcha_text.isalnum():
                # 尝试登录
                payload = {
                    "__VIEWSTATE":value1,
                    '__VIEWSTATEGENERATOR': value2,
                    'txtUserName': xh,
                    'TextBox2': pwd,
                    'txtSecretCode': captcha_text,
                    'RadioButtonList1':'%D1%A7%C9%FA',
                    'Button1':'',
                    'lbLanguage':'',
                    'hidPdrs':'',
                    'hidsc':'',

                }
                if type(set_cookie_header) == type("a"):
                    parts = set_cookie_header.split(";")
                    # 初始化一个空字典
                    cookie_dict = {}
                    # 遍历每个部分，提取键值对
                    for part in parts:
                        # 通过等号分割键和值
                        key_value = part.strip().split("=")
                        key = key_value[0]
                        value = key_value[1] if len(key_value) > 1 else ""
                        # 将键值对添加到字典中
                        cookie_dict[key] = value
                    cookies = cookie_dict
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': f'route={cookies["route"]}',
                    'Host': 'xk.swufe.edu.cn',
                    'Origin': 'http://xk.swufe.edu.cn',
                    'Referer': login_url,
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                }
                session.cookies.update(cookies)
                session.headers.update(headers)
                response = session.post(login_url, data=payload,timeout=timeout)
                if response.url[-8:]==xh:
                    soup = BeautifulSoup(response.text, 'lxml')
                    xhxm = soup.find('span', id='xhxm').text
                    # 从xhxm提取人名，在"同学"之前的任意字符
                    xm = re.match(r"(.+?)同学", xhxm).group(1)
                    with open("config.json", "r",encoding = 'utf-8') as json_file:
                        config_data = json.load(json_file)
                        config_data['MAINURL']=response.url
                        # 以中文字符存储姓名
                        config_data['XM'] = xm
                        parts = set_cookie_header.split(";")
                        # 初始化一个空字典
                        cookie_dict = {}
                        # 遍历每个部分，提取键值对
                        for part in parts:
                            # 通过等号分割键和值
                            key_value = part.strip().split("=")
                            key = key_value[0]
                            value = key_value[1] if len(key_value) > 1 else ""
                            # 将键值对添加到字典中
                            cookie_dict[key] = value
                        config_data['COOKIES'] = cookie_dict
                        # 写入新的配置值到 config.json
                        with open("config.json", "w",encoding = 'utf-8') as json_file:
                            json.dump(config_data, json_file, indent=4,ensure_ascii=False)
                    return response.url
                else:
                    if response.url.endswith("zdy.htm?aspxerrorpath=/Default.aspx"):
                        return "ERROR!出错啦"

                    else:

                        print("登录失败")
    except requests.Timeout:
        # 处理超时异常
        return "请求超时。正在重试..."
    except Exception as e:
        print(e)
        return e

if __name__ == "__main__":
    config = read_config()  # 修改这一行
    if config:
        load = login(config["URL"], config["XH"], config["PWD"])  # 修改这一行
        if load:
            print(f"{load}")