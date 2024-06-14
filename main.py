import requests
import json
from common import get_header
import sqlite3
import time
import random
import toml
import datetime
import sys

# 初始化UserAgent对象
conn = None
curs = None

# 读取配置文件
config_file_path = 'config.toml'

with open(config_file_path, 'r') as f:
    config = toml.load(f)
    number = config.get("number", 232)  # 提供一个默认值为0
    print(f"The number is: {number}")

# 配置代理
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809',
}


def func3(url, page):
    try:
        response = requests.get(url, headers=get_header(), timeout=10)
        if response.status_code == 200 and response.text != '{}':
            json_data = response.json()

            for item in json_data:
                # 插入一行数据
                # 注意，我们不需要指定id字段，因为它会自动递增
                curs.execute("INSERT INTO my_table91 (title, url, page) VALUES (?, ?, ?)",
                             (item['title'], item['uri'], page))

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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    conn = sqlite3.connect('example4.db')
    # 创建一个游标对象
    curs = conn.cursor()

    # 创建一个表，包含自增ID、title和url字段
    # 如果表已经存在，则忽略CREATE TABLE命令
    curs.execute('''CREATE TABLE IF NOT EXISTS my_table91 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        data TEXT,
                        read INTEGER,
                        page INTEGER NOT NULL)''')

    # 提交事务
    conn.commit()

    res_error_num = 0

    for i in range(number, 26491):
        while True:
            print(f"Current time1: {datetime.datetime.now()}")
            url = f'https://homework.study.com/learn/assetPage.ajax?assetDirectoryId=251&assetType=STUDY_ANSWER&pageNumber={i}'
            print(url)
            b = func3(url, i)
            print(b)
            print(f"Current time2: {datetime.datetime.now()}")

            if b is False:
                res_error_num += 1
                if res_error_num > 3:
                    sys.exit(0)
                else:
                    random_sleep_time = random.randint(1, 3)
                    time.sleep(random_sleep_time)
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
            random_sleep_time = random.randint(0, 1)

            # 休眠随机生成的时间
            time.sleep(random_sleep_time)

            break

    # 关闭游标
    curs.close()

    # 关闭数据库连接
    conn.close()
