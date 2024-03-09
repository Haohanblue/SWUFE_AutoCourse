# read.py
import time

import requests
import random
from bs4 import BeautifulSoup
import re
from login import login
import json  # 添加这一行
def read(load,timeout=3):
    try:
        config = None
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        if config:
            load = config["MAINURL"]
            cookies = config["COOKIES"]
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
        document_url=load[:-24]+'xsxk.aspx?xh='+config["XH"]+"&xm=%C0%EE%BA%AB&gnmkdm=N121101"
        content = s.get(document_url,headers=headers,timeout=3)
        if content.url!=document_url:
            login(config["URL"], config["XH"], config["PWD"])
            return "获取失败，请重试"
        else:
            if content.text=="三秒防刷":
                return "三秒防刷"
            else:
                soup = BeautifulSoup(content.text, 'html.parser')
                xsxkurl=[]
                result=soup.find_all('a',onclick=re.compile(r"xsxjs\.aspx"))
                for i in result:
                    value = i.get('onclick')
                    match = re.search(r"window\.open\('([^']+)',", value)
                    if match:
                        link = match.group(1)
                        xkurl=re.match(r"(http?://[^/]+/[^/]+/)", load).group(1)
                        str=xkurl+link
                        if str not in xsxkurl:
                            contents=s.get(str,timeout=timeout)
                            print(contents.url)
                            if contents.url != str:
                                login(config["URL"], config["XH"], config["PWD"])
                                return "获取失败，请重试"
                            else:
                                xsxkurl.append(str)
                if len(xsxkurl)!=0:
                    random_number = random.randint(0, len(xsxkurl)-1)
                    return xsxkurl[random_number]
                else:
                    return "获取的空的列表"
    except requests.Timeout:
        return "请求超时"
    except Exception as e:
        return e

if __name__ == "__main__":
    config = None
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    if config:
        load = config["MAINURL"]
        cookies = config["COOKIES"]
        result = read(load)
        print(result)