import requests
import json
from common import get_header
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
from urllib.parse import urlparse, unquote
import toml
import datetime

# 初始化UserAgent对象
# sconn = None
curs = None

END = False
no_answer = 0

# 配置代理
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809',
}


def func5(url):
    global END
    global no_answer

    try:
        response = requests.get(url, headers=get_header(), proxies=proxies, timeout=10)  #  
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
                no_answer += 1
                if no_answer >= 3:
                    END = True
                    return False, {}

                return True, {}
            else:
                no_answer = 0

            # 将字典转换为JSON字符串
            return True, json_data
        else:
            print(f'''test1, code:{response.status_code}, text:{response.text}''')
            if response.status_code == 403:
                END = True

            return False, {}
    except requests.exceptions.ReadTimeout as e:
        print(f"Timeout occurred when accessing {url}: {str(e)}")
        return False, {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")
        return False, {}


def func4():
    global END
    conn = sqlite3.connect('example.db')
    # 创建一个游标对象
    cur = conn.cursor()
    cur.execute('SELECT * FROM my_table2 WHERE (read NOT IN (1, 3) OR read IS NULL) ORDER BY id;')

    rows = cur.fetchall()

    for row in rows:
        num = 0
        row_num, title, url, data, read = row

        print(f"{row_num}: {title}, {'https://homework.study.com' + url}")
        while True:
            num += 1
            print(f"Current time1: {datetime.datetime.now()}")
            success, json_data = func5('https://homework.study.com' + url)

            if success:
                if json_data == {}:
                    if read == 2:
                        cur.execute("UPDATE my_table2 SET read = 3 WHERE id = ?", (row_num,))
                    elif read != 3:
                        cur.execute("UPDATE my_table2 SET read = 2 WHERE id = ?", (row_num,))
                else:
                    json_output = json.dumps(json_data, ensure_ascii=False)
                    # Use parameter substitution (question marks) to safely insert values
                    cur.execute("UPDATE my_table2 SET data = ?, read = 1 WHERE id = ?", (json_output, row_num))

                # Commit the changes to the database
                conn.commit()

                print(f"Current time2: {datetime.datetime.now()}")
                break
            else:
                if END:
                    return

                time.sleep(10)

            if num > 30:
                return

        # random_sleep_time = random.randint(0, 1)
        # time.sleep(random_sleep_time)

    # 关闭数据库连接
    conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    func4()
