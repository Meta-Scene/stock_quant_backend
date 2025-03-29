import pandas as pd
import os
import csv
import datetime
import threading
import sys
import tushare as ts
import psycopg2

# 获取当前文件所在目录并添加根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# 导入 Database 和 Tushareapi 类
from database.database import Database
from Tushareapi.Tushareapi import Tushareapi


def get_non_st_stock_codes():
    """
    获取所有正常上市交易的非ST、*ST股票代码
    """
    # 使用 Tushareapi 类获取 Pro API 实例
    pro = Tushareapi()
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    ts_codes = list(data["ts_code"])
    non_st_codes = []
    for index, row in data.iterrows():
        stock_name = row['name']
        if "ST" not in stock_name and "*ST" not in stock_name:
            non_st_codes.append(row['ts_code'])
    return non_st_codes


class RealDeal:
    def __init__(self):
        # 获取当前日期，格式为 YYYYMMDD
        self.today = datetime.date.today().strftime("%Y%m%d")
        # 获取当前 Python 文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建数据保存的基础路径，格式为当前目录下的 data/YYYYMMDD
        self.base_path = os.path.join(current_dir, 'data', self.today)
        # 如果基础路径不存在，则创建该文件夹
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        # 使用 Tushareapi 类获取 Pro API 实例
        self.pro = Tushareapi()
        # 初始化数据库连接对象
        self.db = Database("stock")

    def crawl_single_stock(self, ts_code, empty_codes):
        """
        爬取指定股票代码的实时分笔数据并保存为CSV文件
        """
        # 获取指定股票代码的实时分笔数据
        df = ts.realtime_tick(ts_code=ts_code, src='dc')
        # 如果数据为空，创建一个空的 DataFrame 并设置列名
        if df.empty:
            empty_codes.append(ts_code)
        else:
            # 如果数据不为空，在 DataFrame 开头插入日期列
            df.insert(0, 'DATE', self.today)
            # 构建 CSV 文件的文件名，格式为 股票代码_YYYYMMDD.csv
            name = f"{ts_code}.csv"
            # 构建 CSV 文件的完整保存路径
            full_path = os.path.join(self.base_path, name)
            # 将 DataFrame 保存为 CSV 文件，不保存索引
            df.to_csv(full_path, index=False)

    def crawl_stock_data(self, ts_codes, empty_codes):
        """
        使用多线程爬取股票数据
        """
        n = 90
        for i in range(0, len(ts_codes), n):
            if i + n > len(ts_codes):
                batch_codes = ts_codes[i:]
            else:
                batch_codes = ts_codes[i:i + n]
            threads = []
            for elem in batch_codes:
                thread = threading.Thread(target=self.crawl_single_stock, args=(elem, empty_codes,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    def save_data_to_db(self, ts_codes):
        """
        将爬取的CSV数据保存到PostgreSQL数据库
        """
        # 建立数据库连接
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            for ts_code in ts_codes:
                # 获取表名（去掉 .csv 扩展名）
                table_name = os.path.splitext(f"{ts_code}.csv")[0]

                # 检查数据库中是否存在该表
                check_sql = f"""SELECT EXISTS (SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'stock_second' AND table_name = '{table_name}');"""
                cursor.execute(check_sql)
                result = cursor.fetchone()[0]

                if not result:
                    # 如果表不存在，则创建表
                    create_sql = f"""
                    CREATE TABLE stock_second."{table_name}" (
                        "DATE" VARCHAR(255),
                        "TIME" VARCHAR(255),
                        "PRICE" DECIMAL(10, 2),
                        "CHANGE" DECIMAL(10, 2),
                        "VOLUME" DECIMAL(15, 2),
                        "AMOUNT" DECIMAL(15, 2),
                        "TYPE" VARCHAR(255));"""
                    cursor.execute(create_sql)
                    conn.commit()
                    print(f"{table_name} 数据表创建成功！")

                # 打开 CSV 文件并插入数据
                full_path = os.path.join(self.base_path, f"{ts_code}.csv")
                try:
                    with open(full_path, 'r', encoding='utf-8') as csvfile:
                        # 跳过表头
                        next(csvfile)
                        cursor.copy_expert(f"COPY stock_second.\"{table_name}\" FROM STDIN WITH (FORMAT CSV, HEADER FALSE)", csvfile)
                    # 提交事务
                    conn.commit()
                    print(f"{table_name} 数据插入成功！")
                except psycopg2.Error as e:
                    print(f"数据插入出错: {e}")
                    conn.rollback()
                    continue

            cursor.close()
            # 关闭数据库连接
            self.db.close(conn)

    def run(self):
        """
        主运行函数，协调整个爬取和保存流程
        """
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        print(time_str)
        ts_codes = get_non_st_stock_codes()
        print(len(ts_codes))
        empty_codes = []
        self.crawl_stock_data(ts_codes, empty_codes)
        print(empty_codes)
        for i in empty_codes:
            ts_codes.remove(i)
        self.save_data_to_db(ts_codes)


x = RealDeal()
x.run()
