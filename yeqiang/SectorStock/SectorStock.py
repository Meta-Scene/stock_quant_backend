import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)
# 导入database模块
from database.database import Database

class SectorStock:
    def __init__(self, db_params=None):
        # 创建 Database 类的实例
        self.db = Database("sectorstock")

    def CrawlerWeb(self):
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
                    all_links_info[link_name] = "https://data.eastmoney.com/bkzj/%s.html" % s[
                                                                                             s.index("90.") + 3:s.index(
                                                                                                 "90.") + 3 + 6]

        except Exception as e:
            print(f"出现错误: {e}")
        finally:
            # 关闭浏览器
            driver.quit()
        return all_links_info

    def ProcessUrls(self, urls):
        # 启动浏览器（这里以 Chrome 为例，Selenium 4.6+ 可自动管理驱动）
        driver = webdriver.Chrome()
        all_soups = []
        try:
            for name in urls:
                p = [[name, urls[name][urls[name].index(".html") - 6:urls[name].index(".html")]]]
                k = []
                try:
                    # 打开网页
                    driver.get(urls[name])
                    page_num = 1
                    while True:
                        # 显式等待，等待包含数据的表格元素出现，最长等待 10 秒
                        table_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'table')))

                        # 获取当前页面源代码
                        page_source = driver.page_source

                        # 使用 BeautifulSoup 解析页面
                        soup = BeautifulSoup(page_source, 'html.parser')
                        # 找到所有的 <tr> 标签
                        rows = soup.find_all('tr')
                        for row in rows:
                            # 找到每行中的所有 <td> 标签
                            cells = row.find_all('td')
                            data = [cell.get_text(strip=True) for cell in cells]

                            if data and "详情数据股吧" in data:
                                k.append((data[1], data[2]))
                        page_num += 1
                        try:
                            # 显式等待，检查下一页按钮是否存在且可点击，最长等待 2 秒
                            next_page_button = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[data-page="{page_num}"]'))
                            )

                            # 尝试使用 JavaScript 点击按钮，确保点击操作能成功触发
                            driver.execute_script("arguments[0].click();", next_page_button)

                            # 等待页面加载一段时间，可根据实际情况调整等待时间
                            time.sleep(3)

                            # 等待新页面的数据加载完成，这里以表格元素再次可用为例
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, 'table'))
                            )
                        except Exception:
                            # 如果下一页按钮不存在或不可点击，说明已经到最后一页，退出循环
                            break
                    p.append(k)
                    all_soups.append(p)
                except Exception as e:
                    print(f"处理 {urls[name]} 时出现错误: {e}")
        except Exception as e:
            print(f"出现全局错误: {e}")
        finally:
            # 关闭浏览器
            driver.quit()
        return all_soups

    def create_tables_if_not_exists(self, conn):
        cursor = conn.cursor()
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sector'
            );
        """)
        sector_table_exists = cursor.fetchone()[0]

        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock'
            );
        """)
        stock_table_exists = cursor.fetchone()[0]

        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sector_stock_relation'
            );
        """)
        relation_table_exists = cursor.fetchone()[0]

        if not sector_table_exists:
            # 创建板块表
            cursor.execute("""
                CREATE TABLE sector (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL UNIQUE
                );
            """)
        if not stock_table_exists:
            # 创建股票表
            cursor.execute("""
                CREATE TABLE stock (
                    id SERIAL PRIMARY KEY,
                    ts_code VARCHAR(20) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL
                );
            """)
        if not relation_table_exists:
            # 创建板块和股票的关联表
            cursor.execute("""
                CREATE TABLE sector_stock_relation (
                    id SERIAL PRIMARY KEY,
                    sector_id INT NOT NULL,
                    stock_id INT NOT NULL,
                    FOREIGN KEY (sector_id) REFERENCES sector(id),
                    FOREIGN KEY (stock_id) REFERENCES stock(id),
                    UNIQUE (sector_id, stock_id)
                );
            """)
        conn.commit()
        cursor.close()

    def insert_data_to_db(self, data):
        try:
            # 使用 Database 类的 connect 方法建立数据库连接
            conn = self.db.connect()
            if conn:
                # 检查并创建表
                self.create_tables_if_not_exists(conn)
                cursor = conn.cursor()

                for sector_info in data:
                    sector_name = sector_info[0][0]
                    sector_ts_code = sector_info[0][1]

                    # 插入板块信息
                    cursor.execute("INSERT INTO sector (name, ts_code) VALUES (%s, %s) ON CONFLICT (ts_code) DO NOTHING RETURNING id;",
                                   (sector_name, sector_ts_code))
                    sector_id = cursor.fetchone()
                    if sector_id is None:
                        # 如果板块已经存在，获取其 id
                        cursor.execute("SELECT id FROM sector WHERE ts_code = %s;", (sector_ts_code,))
                        sector_id = cursor.fetchone()[0]
                    else:
                        sector_id = sector_id[0]

                    for stock_name, stock_ts_code in sector_info[1]:
                        # 插入股票信息
                        cursor.execute("INSERT INTO stock (name, ts_code) VALUES (%s, %s) ON CONFLICT (ts_code) DO NOTHING RETURNING id;",
                                       (stock_name, stock_ts_code))
                        stock_id = cursor.fetchone()
                        if stock_id is None:
                            # 如果股票已经存在，获取其 id
                            cursor.execute("SELECT id FROM stock WHERE ts_code = %s;", (stock_ts_code,))
                            stock_id = cursor.fetchone()[0]
                        else:
                            stock_id = stock_id[0]

                        # 插入板块和股票的关联信息
                        cursor.execute("INSERT INTO sector_stock_relation (sector_id, stock_id) VALUES (%s, %s) ON CONFLICT (sector_id, stock_id) DO NOTHING;",
                                       (sector_id, stock_id))

                # 提交事务
                conn.commit()
                print("数据插入成功！")
        except Exception as e:
            print(f"插入数据时出现错误: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                # 使用 Database 类的 close 方法关闭数据库连接
                self.db.close(conn)

    def run(self):
        urls = self.CrawlerWeb()
        print(len(urls))
        data = self.ProcessUrls(urls)
        self.insert_data_to_db(data)


x=SectorStock()
x.run()
