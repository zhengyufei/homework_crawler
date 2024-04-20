import requests
import json
from common import get_header, get_cookie
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sqlite3
import time
import random
import re
from urllib.parse import urlparse, unquote
import toml

# 初始化UserAgent对象
ua = UserAgent()
conn = None
curs = None

END = False

# 读取配置文件
config_file_path = 'config.toml'
number2 = 0
with open(config_file_path, 'r') as f:
    config = toml.load(f)
    number2 = config.get("number2", 223)  # 提供一个默认值为0
    print(f"The number is: {number2}")


def get_global_dynamic_proxy():
    """海外动态IP，必须在国外服务器上使用"""
    response = requests.get(
        "http://api.tq.roxlabs.cn/getProxyIp?num=1&return_type=html&lb=4&sb=&flow=1&regions=&protocol=http"
    )

    if response.status_code != 200:
        raise Exception("Failed to get proxy")
    print(f'dynamic proxy: {response.text.strip()}')
    return f"http://{response.text.strip()}"

proxy_num = 0
proxies = None

def func5(url):
    global END
    global proxy_num
    global proxies

    print(f'test0, {proxy_num}')

    if proxy_num > 5:
        proxy_num = 0

    if proxy_num == 0:
        # 获取第二个代理，即海外动态IP
        second_proxy = get_global_dynamic_proxy()

        # 设置第二个代理
        proxies = {
            "http": second_proxy,
            "https": second_proxy
        }

    proxy_num += 1

    try:
        response = requests.get(url, headers=get_header(), proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 初始化JSON数据结构
            json_data = {
                'url': url,
                'title': '',
                'question': '',
                'answer': '',
                'expand': ''
            }

            # 提取 title
            title_tag = soup.find('title')
            if title_tag:
                json_data['title'] = title_tag.get_text().strip()

            # 提取 h2 标签
            for h2_tag in soup.find_all('h2'):
                header_text = h2_tag.get_text().strip().split('\n')[0].strip()

                tmp_tag = h2_tag
                key = None
                if header_text == 'Answer and Explanation:':
                    key = 'answer'
                    tmp_tag = tmp_tag.find_next_sibling()
                    second_layer_div = tmp_tag.find('div', {'itemprop': 'text'}) if tmp_tag else None

                    if second_layer_div:
                        for p_tag in second_layer_div.find_all('p', recursive=False):
                            json_data['answer'] += p_tag.get_text().strip() + '\n'

                        for ol_tag in second_layer_div.find_all('ol', recursive=False):
                            for li_tag in ol_tag.find_all('li', recursive=False):
                                json_data['answer'] += li_tag.get_text().strip() + '\n'
                    else:
                        # 如果没有找到，我们假设它是第二种页面结构
                        # 如果tmp_tag是一个div标签，直接从这个div标签里面提取<p>标签
                        if tmp_tag and tmp_tag.name == 'div':
                            for p_tag in tmp_tag.find_all('p', recursive=False):
                                json_data[key] += p_tag.get_text().strip() + '\n'
                            # 也查找<ol>标签，以防它们存在于这个部分
                            for ol_tag in tmp_tag.find_all('ol', recursive=False):
                                for li_tag in ol_tag.find_all('li', recursive=False):
                                    json_data[key] += li_tag.get_text().strip() + '\n'
                    break
                elif header_text == 'Question:':
                    key = 'question'
                else:
                    key = 'expand'
                    json_data['expand'] += header_text + '\n'

                next_tag = tmp_tag.find_next_sibling()
                while next_tag and next_tag.name not in ['h2', 'div']:
                    if next_tag.name == 'p':
                        json_data[key] += next_tag.get_text().strip() + '\n'
                    next_tag = next_tag.find_next_sibling()

                if next_tag and next_tag.name == 'div':
                    for p_tag in next_tag.find_all('p', recursive=False):
                        json_data[key] += p_tag.get_text().strip() + '\n'

            # 检查是否有有效数据
            if len(json_data['answer']) == 0:
                print('No answer data found.')
                END = True
                return False, {}

            # 将字典转换为JSON字符串
            return True, json_data
        else:
            print(f'''test1, code:{response.status_code}, text:{response.text}''')
            return False, {}
    except requests.ConnectionError as e:
        print(f'''test2. {e}''')
        return False, {}


def func4():
    global END
    global number2

    conn = sqlite3.connect('example.db')
    # 创建一个游标对象
    cur = conn.cursor()
    cur.execute('SELECT * FROM my_table')

    rows = cur.fetchall()

    for row in rows:
        num = 0
        row_num, title, url, data, read = row
        if row_num < number2 and read == 1:
            continue
        print(f"{row_num}: {title}, {'https://homework.study.com' + url}")
        while True:
            num += 1
            success, json_data = func5('https://homework.study.com' + url)
            # success, json_data = func5('https://www.google.com')

            if success:
                json_output = json.dumps(json_data, ensure_ascii=False)
                # Use parameter substitution (question marks) to safely insert values
                cur.execute("UPDATE my_table SET data = ?, read = 1 WHERE id = ?", (json_output, row_num))
                # Commit the changes to the database
                conn.commit()

                # 更新这个整数值
                number2 += 1

                # 写入配置文件
                config['number2'] = number2

                with open(config_file_path, 'w') as f:
                    toml.dump(config, f)

                print(f"Updated number to: {number2}")
                break
            else:
                if END:
                    return

                time.sleep(10)

            if num > 3:
                return

        random_sleep_time = random.randint(5, 10)
        time.sleep(random_sleep_time)

        if row_num > 2000:
            print('test end')
            return

    # 关闭数据库连接
    conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    func4()
