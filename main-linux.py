import requests
import json
from common import get_header
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sqlite3
import time
import random
import toml

# 初始化UserAgent对象
ua = UserAgent()
conn = None
curs = None

import toml

# 读取配置文件
config_file_path = 'config.toml'

with open(config_file_path, 'r') as f:
    config = toml.load(f)
    number = config.get("number", 232)  # 提供一个默认值为0
    print(f"The number is: {number}")


def _get_global_dynamic_proxy():
    """海外动态ip，必须在国外服务器上使用"""
    ret = requests.get(
        "http://api.tq.roxlabs.cn/getProxyIp?num=1&return_type=json&lb=1&sb=&flow=1&regions=us&protocol=http").json()
    ip = ret["data"][0]
    # print("reset proxy,exp:", proxy_time, ip)
    return f"""http://{ip["ip"]}:{ip["port"]}"""


# proxy = _get_global_dynamic_proxy()
# proxies = {
#     "http": proxy,
#     "https": proxy
# }

# 配置代理
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809',
}


def func3(url):
    try:
        response = requests.get(url, headers=get_header(), cookies=get_cookie(), proxies=proxies)
        if response.status_code == 200 and response.text != '{}':
            json_data = response.json()

            for item in json_data:
                # 插入一行数据
                # 注意，我们不需要指定id字段，因为它会自动递增
                curs.execute("INSERT INTO my_table (title, url) VALUES (?, ?)", (item['title'], item['uri']))

                # 提交事务
                conn.commit()

            return True
        else:
            return False
    except requests.ConnectionError:
        return False


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # ret = requests.get("https://www.google.com/", headers={"User-Agent": ua.random}, proxies=proxies)

    conn = sqlite3.connect('example.db')
    # 创建一个游标对象
    curs = conn.cursor()

    # 创建一个表，包含自增ID、title和url字段
    # 如果表已经存在，则忽略CREATE TABLE命令
    curs.execute('''CREATE TABLE IF NOT EXISTS my_table (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL)''')

    # 提交事务
    conn.commit()

    for i in range(number, 27000):
        url = f'https://homework.study.com/learn/assetPage.ajax?assetDirectoryId=251&assetType=STUDY_ANSWER&pageNumber={i}'
        print(url)
        b = func3(url)
        print(b)

        if b is False:
            break

        # 更新这个整数值
        new_number = i + 1

        # 写入配置文件
        config['number'] = new_number

        with open(config_file_path, 'w') as f:
            toml.dump(config, f)

        print(f"Updated number to: {new_number}")

        # 生成一个10到30之间的随机整数
        random_sleep_time = random.randint(5, 10)

        # 休眠随机生成的时间
        time.sleep(random_sleep_time)

    # 关闭游标
    curs.close()

    # 关闭数据库连接
    conn.close()
