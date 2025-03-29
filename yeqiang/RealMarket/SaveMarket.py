import psycopg2
import csv
import datetime
import os
from datetime import datetime as dt

today = datetime.date.today()
fortoday = today.strftime("%Y%m%d")
def process_single_csv(ts_code):
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建数据保存的基础路径
    base_path = os.path.join(current_dir, '..', 'data', 'RealMarket', fortoday)
    filename = f"{ts_code} {fortoday}.csv"
    full_path = os.path.join(base_path, filename)

    def is_in_target_range(time_str):
        try:
            time_obj = dt.strptime(time_str.strip(), '%H:%M:%S').time()
            time_925 = dt.strptime('09:25:00', '%H:%M:%S').time()
            time_1130 = dt.strptime('11:30:00', '%H:%M:%S').time()
            time_1300 = dt.strptime('13:00:00', '%H:%M:%S').time()
            time_1500 = dt.strptime('15:00:00', '%H:%M:%S').time()
            return (time_925 <= time_obj <= time_1130) or (time_1300 <= time_obj <= time_1500)
        except ValueError:
            return False

    try:
        valid_rows = []
        with open(full_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # 读取表头
            time_index = headers.index('TIME')  # 找到 TIME 字段的索引

            # 筛选出在指定时间范围内的数据
            for row in reader:
                if is_in_target_range(row[time_index]):
                    valid_rows.append(row)

        # 将筛选后的数据覆盖原文件
        with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # 写入表头
            writer.writerows(valid_rows)  # 写入筛选后的数据

        print(f"文件 {ts_code} {fortoday} 已更新，保留了指定时间范围内的数据。")
    except Exception as e:
        print(f"处理文件 {full_path} 时出错: {e}")


def SaveMarket(ts_codes):
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建数据保存的基础路径
    base_path = os.path.join(current_dir, '..', 'data', 'RealMarket', fortoday)

    db_params = {
        "host": "localhost",
        "port": "5432",
        "database": "realmarket",
        "user": "postgres",
        "password": "123456"
    }
    # 连接到 PostgreSQL 数据库
    conn = psycopg2.connect(**db_params)
    # 创建游标对象
    cursor = conn.cursor()

    for ts_code in ts_codes:
        # 调用第一个函数处理单个 ts_code 的 CSV 文件
        process_single_csv(ts_code)

        filename = f"{ts_code} {fortoday}.csv"
        full_path = os.path.join(base_path, filename)

        try:
            # 检查表格是否存在
            check_sql = f"""SELECT EXISTS (
                SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{ts_code}'
            );"""
            cursor.execute(check_sql)
            result = cursor.fetchone()[0]

            if not result:
                # 如果表不存在，则创建它
                create_sql = f"""
                CREATE TABLE "{ts_code}" (
                    "NAME" VARCHAR(255),
                    "TS_CODE" VARCHAR(255),
                    "DATE" VARCHAR(255),
                    "TIME" VARCHAR(255),
                    "OPEN" DECIMAL(10, 2),
                    "PRE_CLOSE" DECIMAL(10, 2),
                    "PRICE" DECIMAL(10, 2),
                    "HIGH" DECIMAL(10, 2),
                    "LOW" DECIMAL(10, 2),
                    "BID" DECIMAL(10, 2),
                    "ASK" DECIMAL(10, 2),
                    "VOLUME" DECIMAL(20, 2),
                    "AMOUNT" DECIMAL(20, 2),
                    "B1_V" DECIMAL(10, 2),
                    "B1_P" DECIMAL(10, 2),
                    "B2_V" DECIMAL(10, 2),
                    "B2_P" DECIMAL(10, 2),
                    "B3_V" DECIMAL(10, 2),
                    "B3_P" DECIMAL(10, 2),
                    "B4_V" DECIMAL(10, 2),
                    "B4_P" DECIMAL(10, 2),
                    "B5_V" DECIMAL(10, 2),
                    "B5_P" DECIMAL(10, 2),
                    "A1_V" DECIMAL(10, 2),
                    "A1_P" DECIMAL(10, 2),
                    "A2_V" DECIMAL(10, 2),
                    "A2_P" DECIMAL(10, 2),
                    "A3_V" DECIMAL(10, 2),
                    "A3_P" DECIMAL(10, 2),
                    "A4_V" DECIMAL(10, 2),
                    "A4_P" DECIMAL(10, 2),
                    "A5_V" DECIMAL(10, 2),
                    "A5_P" DECIMAL(10, 2)
                );
                """
                cursor.execute(create_sql)
                conn.commit()  # 提交创建表的事务
                print(f"{ts_code} 数据表创建成功！")

            with open(full_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # 跳过第一行（字段名）

                # 获取列数
                first_row = next(reader)  # 读取第二行来确定列数
                columns_count = len(first_row)
                placeholders = ', '.join(['%s'] * columns_count)
                insert_query = f"""INSERT INTO "{ts_code}" VALUES ({placeholders})"""
                # 插入第一行数据
                cursor.execute(insert_query, first_row)

                # 插入剩余行数据
                try:
                    for row in reader:
                        cursor.execute(insert_query, row)

                    # 提交插入数据的事务
                    conn.commit()
                    print(f"{ts_code} 数据插入成功！")
                except Exception as e:
                    print(f"插入 {ts_code} 数据时出错: {e}")

        except Exception as e:
            print(f"处理文件 {full_path} 时出错: {e}")

    cursor.close()
    conn.close()

