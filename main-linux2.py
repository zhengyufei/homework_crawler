import requests
import json
from common import get_header
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sqlite3
import time
import random
import toml
from config import prs as cfg_proxies

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


def proxy_generator(pr_list):
    while True:
        for proxy in pr_list:
            yield proxy


# 创建代理生成器
proxy_gen = proxy_generator(cfg_proxies)


def get_proxies():
    # 获取下一个代理字符串
    next_proxy = next(proxy_gen)
    print(f"next_proxy: {next_proxy}")
    proxy_url = f'http://{next_proxy}'

    # 生成代理字典
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    return proxies


def get_cached_proxies():
    # 静态变量用于存储调用次数和当前代理
    if not hasattr(get_cached_proxies, "counter"):
        get_cached_proxies.counter = 0
        get_cached_proxies.current_proxies = None

    # 每访问5次更新一次代理
    if get_cached_proxies.counter % 1 == 0:
        get_cached_proxies.current_proxies = get_proxies()
    # 调用次数增加
    get_cached_proxies.counter += 1

    return get_cached_proxies.current_proxies


def func3(url):
    try:
        proxies = get_cached_proxies()
        response = requests.get(url, headers=get_header(), proxies=proxies, timeout=10)
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
    except requests.exceptions.ReadTimeout as e:
        print(f"Timeout occurred when accessing {url}: {str(e)}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# 封装的函数


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

    res_error_num = 0

    for i in range(number, 27000):
        while(True):
            url = f'https://homework.study.com/learn/assetPage.ajax?assetDirectoryId=251&assetType=STUDY_ANSWER&pageNumber={i}'
            print(url)
            b = func3(url)
            print(b)

            if b is False:
                res_error_num += 1
                if res_error_num > 3:
                    break
                else:
                    continue

            res_error_num = 0

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

            break

    # 关闭游标
    curs.close()

    # 关闭数据库连接
    conn.close()
