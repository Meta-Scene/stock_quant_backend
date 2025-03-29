import json
import csv
import os
import datetime
from selenium import webdriver
import time
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir) 
sys.path.append(root_dir)

# 导入database模块
from database.database import Database


def CrawlerWeb():
    # 启动浏览器（这里以 Chrome 为例，Selenium 4.6+ 可自动管理驱动）
    driver = webdriver.Chrome()

    try:
        # 打开网页
        driver.get('https://data.eastmoney.com/bkzj/hy.html')

        # 显式等待，等待“概念资金流”元素出现，最长等待 10 秒
        concept_funds_flow = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-value="gn"]'))
        )

        # 使用 JavaScript 点击“概念资金流”元素
        driver.execute_script("arguments[0].click();", concept_funds_flow)

        # 等待页面加载一段时间，可根据实际情况调整等待时间
        time.sleep(2)

        # 显式等待，等待包含数据的表格元素出现，最长等待 10 秒
        table_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )

        all_links_info = {}
        for i in range(1, 11):
            if i > 1:
                # 显式等待，等待下一页按钮出现，最长等待 10 秒
                next_page_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[data-page="{i}"]')))

                # 尝试使用 JavaScript 点击按钮，确保点击操作能成功触发
                driver.execute_script("arguments[0].click();", next_page_button)

                # 等待页面加载一段时间，可根据实际情况调整等待时间
                time.sleep(3)

                # 等待新页面的数据加载完成，这里以表格元素再次可用为例
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table')))

            # 获取当前页面源代码
            page_source = driver.page_source
            # 使用 BeautifulSoup 解析页面
            soup = BeautifulSoup(page_source, 'html.parser')

            # 查找所有符合条件的 <a> 标签
            links = soup.select('td a[href^="//quote.eastmoney.com/unify/r/"]')
            for link in links:
                s = str(link)
                link_name = link.text
                all_links_info[link_name] = "https://quote.eastmoney.com/bk/90.%s.html#fullScreenChart" % s[
                                                                                         s.index("90.") + 3:s.index(
                                                                                             "90.") + 3 + 6]

    except Exception as e:
        print(f"出现错误: {e}")
    finally:
        # 关闭浏览器
        driver.quit()
    # 返回链接信息字典中的值，即链接列表
    return list(all_links_info.values())


class DailySector:
    def __init__(self):
        urls = CrawlerWeb()
        print(len(urls))
        # 传入的网址列表
        self.urls = urls
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
        # 数据库连接参数
        # 创建 Database 类的实例
        self.db = Database("dailyquote")

    def create_table(self, table_name):
        try:
            # 调用数据库类的 connect 方法建立连接
            conn = self.db.connect()
            if conn:
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
                cursor.close()
                # 调用数据库类的 close 方法关闭连接
                self.db.close(conn)
        except Exception as e:
            print(f"创建表 {table_name} 时出错: {e}")

    def insert_data_to_db(self, table_name, data):
        try:
            # 调用数据库类的 connect 方法建立连接
            conn = self.db.connect()
            if conn:
                cursor = conn.cursor()
                insert_query = f"""INSERT INTO "{table_name}" (date, time, price, amount) VALUES (%s, %s, %s, %s);"""
                for row in data:
                    cursor.execute(insert_query, (row['date'], row['time'], row['price'], row['amount']))
                conn.commit()
                cursor.close()
                # 调用数据库类的 close 方法关闭连接
                self.db.close(conn)
                print(f"数据已插入到 {table_name} 表中")
        except Exception as e:
            print(f"插入数据到 {table_name} 表时出错: {e}")

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
                                print(code)
                                # 生成 CSV 文件名
                                csv_filename = f"{code} {date}.csv"
                                # 构建完整的 CSV 文件保存路径
                                full_path = os.path.join(self.base_path, csv_filename)

                                # 提取 trends 数据
                                trends = json_data['data']['trends']
                                data_to_insert = []
                                with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
                                    fieldnames = ['date', 'time', 'price', 'amount']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                                    # 写入表头
                                    writer.writeheader()

                                    for trend in trends:
                                        parts = trend.split(',')
                                        date = parts[0].split(' ')[0]
                                        time_part = parts[0].split(' ')[1]
                                        price = parts[2]
                                        amount = parts[5]
                                        writer.writerow({
                                            'date': date,
                                            'time': time_part,
                                            'price': price,
                                            'amount': amount
                                        })
                                        data_to_insert.append({
                                            'date': date,
                                            'time': time_part,
                                            'price': price,
                                            'amount': amount
                                        })

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


x=DailySector()
# 调用 run 方法开始爬取和数据处理
x.run()
