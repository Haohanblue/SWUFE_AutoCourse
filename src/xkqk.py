# xkqk.py
import requests
from bs4 import BeautifulSoup
import re
from login import login
import csv
import json
import ast# 添加这一行
import urllib
from urllib import parse
def xkqk(load,timeout=3):
    try:
        with open('config.json', 'r',encoding='utf-8') as config_file:
            config = json.load(config_file)
        if config:
            load = config["MAINURL"]
            cookies = config["COOKIES"]
            # 从json文件中读取姓名，转化为url编码
            xm = config["XM"]
            xm = urllib.parse.quote(xm, encoding='gbk')
            if cookies and type(cookies) == type("a"):
                cookies = ast.literal_eval(cookies)
        s = requests.Session()
        s.cookies.update(cookies)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding':'gzip,deflate',
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connectiong':'keep-alive',
            'Referer': load,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
             }
        document_url=load[:-24]+'xsxkqk.aspx?xh='+config["XH"]+"&xm="+xm+"&gnmkdm=N121615"
        content = s.get(document_url,headers=headers,timeout=3)
        if content.url != document_url:
            login(config["URL"], config["XH"], config["PWD"])
            return "获取失败，请重试"
        else:
            soup = BeautifulSoup(content.text, 'html.parser')
            xkqk=[]
            xkmc=[]
            result=soup.find_all('td', text=re.compile(r'\(\d{4}-\d{4}-\d{1,2}\)-[A-Z]+\d+-\d+'))
            mc=soup.find_all('a',href='#')
            text=[]
            for x in mc:
                text.append(x.text)
            for i in range(0,len(text),2):
                xkmc.append("{}:{}".format(text[i],text[i+1]))
            # 输出找到的结果
            for td_tag in result:
                if td_tag:
                    xkqk.append(td_tag.text)
            csv_file_name = 'xkmc.csv'
            # 打开 CSV 文件进行写入
            if xkqk is not None:
                with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    # 创建 CSV writer 对象
                    csv_writer = csv.writer(csvfile)
                    # 写入数据到 CSV 文件
                    for item in xkmc:
                        csv_writer.writerow([item])
            return xkmc
    except requests.Timeout:
        return "请求超时"
    except Exception as e:
        return e

if __name__ == "__main__":
    config = None
    with open('config.json', 'r',encoding='utf-8') as config_file:
        config = json.load(config_file)
    if config:
        load = config["MAINURL"]
        result = xkqk(load)
        print(result)