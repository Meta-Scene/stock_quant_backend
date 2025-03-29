import json
import csv
import os
import datetime
from selenium import webdriver
import time
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)
# 导入database模块
from database.database import Database


class DailyQuotes:
    def __init__(self):
        # 定义要打开的网页列表
        self.urls = [
            "https://quote.eastmoney.com/zs000001.html#fullScreenChart",
            "https://quote.eastmoney.com/zs399001.html#fullScreenChart",
            "https://quote.eastmoney.com/zs399006.html#fullScreenChart",
            "https://quote.eastmoney.com/zs399005.html#fullScreenChart",
            "https://quote.eastmoney.com/zs000300.html#fullScreenChart",
            "https://quote.eastmoney.com/zs000016.html#fullScreenChart",
            "https://quote.eastmoney.com/zs000003.html#fullScreenChart",
            "https://quote.eastmoney.com/zs000688.html#fullScreenChart"
        ]
        self.options = webdriver.ChromeOptions()
        self.options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        self.driver = None
        self.target_url_start = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
        # 获取当前日期，格式为 YYYYMMDD
        self.today = datetime.date.today().strftime("%Y%m%d")
        # 获取当前 Python 文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建数据保存的基础路径，格式为当前目录下的 data/YYYYMMDD
        self.base_path = os.path.join(current_dir, 'data', self.today)
        # 如果基础路径不存在，则创建该文件夹
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        # 创建 Database 类的实例
        self.db = Database("dailyquote")

    def create_table(self, table_name):
        conn = self.db.connect()
        if conn:
            try:
                cursor = conn.cursor()
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    date DATE,
                    time TIME,
                    price DECIMAL,
                    amount DECIMAL
                );
                """
                cursor.execute(create_table_query)
                conn.commit()
                print(f"表 {table_name} 创建成功")
            except Exception as e:
                print(f"创建表 {table_name} 时出错: {e}")
            finally:
                self.db.close(conn)

    def insert_data_to_db(self, table_name, data):
        conn = self.db.connect()
        if conn:
            try:
                cursor = conn.cursor()
                insert_query = f"""INSERT INTO "{table_name}" (date, time, price, amount) VALUES (%s, %s, %s, %s);"""
                for row in data:
                    cursor.execute(insert_query, (row['date'], row['time'], row['price'], row['amount']))
                conn.commit()
                print(f"数据已插入到 {table_name} 表中")
            except Exception as e:
                print(f"插入数据到 {table_name} 表时出错: {e}")
            finally:
                self.db.close(conn)

    def create_csv_file(self, csv_filename):
        """
        创建 CSV 文件并写入表头
        :param csv_filename: CSV 文件的完整路径
        """
        fieldnames = ['date', 'time', 'price', 'amount']
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def append_to_csv(self, csv_filename, data):
        """
        向 CSV 文件中追加数据
        :param csv_filename: CSV 文件的完整路径
        :param data: 要追加的数据，是一个字典列表
        """
        fieldnames = ['date', 'time', 'price', 'amount']
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for row in data:
                writer.writerow(row)

    def run(self):
        try:
            # 初始化浏览器驱动
            self.driver = webdriver.Chrome(options=self.options)
            for url in self.urls:
                self.driver.get(url)
                print(f"已打开网页: {url}")
                time.sleep(5)  # 等待请求完成

                logs = self.driver.get_log('performance')
                found = False

                for entry in logs:
                    try:
                        log = json.loads(entry['message'])
                        msg = log.get('message', {})
                        if msg.get('method') != 'Network.responseReceived':
                            continue
                        response = msg.get('params', {}).get('response', {})
                        if response.get('url', '').startswith(self.target_url_start):
                            request_id = msg['params']['requestId']
                            try:
                                # 获取响应体
                                body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                # 去除 JSONP 包装
                                body_text = body['body'].strip()
                                start_index = body_text.find('{')
                                end_index = body_text.rfind('}')
                                json_data = json.loads(body_text[start_index:end_index + 1])

                                # 提取代码和时间
                                code = json_data['data']['code']
                                # 假设 trends 列表不为空，取第一个元素的日期部分
                                date = json_data['data']['trends'][0].split(',')[0].replace('-', '')[:8]

                                # 生成 CSV 文件名
                                csv_filename = f"{code} {date}.csv"
                                # 构建完整的 CSV 文件保存路径
                                full_path = os.path.join(self.base_path, csv_filename)

                                # 提取 trends 数据
                                trends = json_data['data']['trends']
                                data_to_insert = []
                                for trend in trends:
                                    parts = trend.split(',')
                                    date = parts[0].split(' ')[0]
                                    time_part = parts[0].split(' ')[1]
                                    price = parts[2]
                                    amount = parts[5]
                                    data_to_insert.append({
                                        'date': date,
                                        'time': time_part,
                                        'price': price,
                                        'amount': amount
                                    })

                                # 创建 CSV 文件并写入表头
                                self.create_csv_file(full_path)
                                # 向 CSV 文件中追加数据
                                self.append_to_csv(full_path, data_to_insert)

                                print(f"trends 数据已保存到 {full_path}")

                                # 表名
                                table_name = f"{code}"
                                # 创建表
                                self.create_table(table_name)
                                # 插入数据到数据库
                                self.insert_data_to_db(table_name, data_to_insert)

                                found = True
                                break
                            except Exception as e:
                                print(f"获取响应或处理数据失败: {e}")
                    except Exception as e:
                        print(f"解析日志出错: {e}")

                if not found:
                    print(f"未找到目标请求: {url}")
        except Exception as e:
            print(f"运行过程中出现错误: {e}")
        finally:
            # 关闭浏览器驱动
            if self.driver:
                self.driver.quit()



x=DailyQuotes()
x.run()
