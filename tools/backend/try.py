from flask import Flask, request, jsonify, render_template
from decimal import Decimal
from flask_cors import CORS
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 假设这些模块已经正确实现
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from yeqiang.database.database import Database
from QuantitativeStrategys.stategy1.add_signal import add_signal

app = Flask(__name__)
CORS(app)

n = 10
target_pct = 6


def parse_date(date_str):
    """
    解析日期字符串，如果解析失败则使用默认日期。
    :param date_str: 日期字符串，格式为 'YYYY-MM-DD'
    :return: 解析后的日期对象
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return datetime.strptime('2024-10-22', '%Y-%m-%d')


def execute_query(conn, date_str, n, target_pct, type):
    """
    执行 SQL 查询并返回结果。
    :param conn: 数据库连接对象
    :param date_str: 日期字符串，格式为 'YYYY-MM-DD'
    :param n: 用于 SQL 查询的范围参数
    :return: 查询结果
    """
    cursor = conn.cursor()
    desired_columns = [
        'ts_code', 'trade_date',
        'open', 'high', 'low', 'close',
        'pre_close', 'pct_chg', 'vol'
    ]
    columns_str = ', '.join([f'ns.{col}' for col in desired_columns])
    if type:
        type = '> '
    else:
        type = '< -'
    sql = f"""
    WITH FilteredStocks AS (
        SELECT 
            ts_code,
            -- 转换 trade_date 格式
            SUBSTRING(trade_date FROM 1 FOR 4) || '-' || 
            SUBSTRING(trade_date FROM 5 FOR 2) || '-' || 
            SUBSTRING(trade_date FROM 7 FOR 2) AS trade_date,
            open, high, low, close, pre_close, pct_chg::numeric, vol
        FROM public.all_stocks_days
        WHERE 1=1 AND ts_code LIKE '%BJ'
    ),
    NumberedStocks AS (
        SELECT 
            {', '.join(desired_columns)},
            ROW_NUMBER() OVER (PARTITION BY ts_code ORDER BY trade_date) AS rn
        FROM FilteredStocks
    ),
    TargetRows AS (
        SELECT 
            ts_code,
            rn AS target_rn
        FROM NumberedStocks
        WHERE trade_date = '{date_str}' AND pct_chg::numeric {type}{target_pct}
    )
    SELECT {columns_str}, ns.rn
    FROM NumberedStocks ns
    JOIN TargetRows tr ON ns.ts_code = tr.ts_code
    WHERE ns.rn BETWEEN tr.target_rn - {n} AND tr.target_rn + {n}
    """

    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception as e:
        print(f"数据库查询出错: {e}")
        data = []
    finally:
        cursor.close()
    return data


def process_data(data, date_str, type):
    """
    处理查询结果，包括数据类型转换、分组处理和排序。
    :param data: 查询结果
    :param date_str: 日期字符串，格式为 'YYYY-MM-DD'
    :return: 处理后的结果数组和 pct_chg 字典
    """
    desired_columns = [
        'ts_code', 'trade_date',
        'open', 'high', 'low', 'close',
        'pre_close', 'pct_chg', 'vol'
    ]
    df = pd.DataFrame(data, columns=desired_columns + ['rn'])
    numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'pct_chg', 'vol']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    grouped = df.groupby('ts_code')
    result_arrays = []
    columns_to_keep = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'pct_chg', 'vol', 'bay']
    pct_chg_dict = {}
    for name, group in grouped:
        processed_group = add_signal(group)
        processed_group['trade_date'] = processed_group['trade_date'].astype(str)
        processed_group = processed_group[columns_to_keep]
        result_arrays.append(processed_group.values.tolist())
        current_date_data = processed_group[processed_group['trade_date'] == date_str]
        if not current_date_data.empty:
            pct_chg_dict[name] = current_date_data['pct_chg'].values[0]
    type = True if type == 1 else False
    result_arrays.sort(key=lambda x: pct_chg_dict.get(x[0][0], 0), reverse=True)
    return result_arrays, pct_chg_dict


def paginate_data(result_arrays, page):
    """
    对结果数组进行分页处理。
    :param result_arrays: 处理后的结果数组
    :param page: 当前页码
    :return: 分页后的数据、总页数和股票总数
    """
    items_per_page = 9
    total_pages = len(result_arrays) // items_per_page + (1 if len(result_arrays) % items_per_page != 0 else 0)

    # 边界检查
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_data = result_arrays[start_index:end_index]

    stock_count = len(result_arrays)
    return paginated_data, total_pages, stock_count, page


@app.route('/1', methods=['GET'])
def sda():
    print(1)
@app.route('/up_stop', methods=['GET'])
def get_up_stop():
    # 获取请求中的日期参数，如果没有则使用默认日期
    date_str = request.args.get('date', '2024-10-22')
    page = request.args.get('page', 1, type=int)
    date = parse_date(date_str)  # 检查日期
    type = 1
    # 连接数据库并执行查询
    db = Database("stock")
    try:
        conn = db.connect()
        data = execute_query(conn, date_str, n, target_pct, type)
        conn.close()
    except Exception as e:
        print(f"数据库连接出错: {e}")
        return jsonify(error="数据库连接出错"), 500

    # 处理数据
    result_arrays, pct_chg_dict = process_data(data, date_str, type)

    # 分页逻辑
    paginated_data, total_pages, stock_count, page = paginate_data(result_arrays, page)

    columns_to_keep = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'pct_chg', 'vol', 'bay']
    return render_template("index1.html", grid_data=paginated_data, columns=columns_to_keep, date=date_str,
                           page=page,
                           total_pages=total_pages, stock_count=stock_count)


@app.route('/down_stop', methods=['GET'])
def get_down_stop():
    # 获取请求中的日期参数，如果没有则使用默认日期
    date_str = request.args.get('date', '2024-10-22')
    page = request.args.get('page', 1, type=int)
    date = parse_date(date_str)  # 检查日期
    type = 0
    # 连接数据库并执行查询
    db = Database("stock")
    try:
        conn = db.connect()
        data = execute_query(conn, date_str, n, target_pct, type)
        conn.close()
    except Exception as e:
        print(f"数据库连接出错: {e}")
        return jsonify(error="数据库连接出错"), 500

    # 处理数据
    result_arrays, pct_chg_dict = process_data(data, date_str, type)

    # 分页逻辑
    paginated_data, total_pages, stock_count, page = paginate_data(result_arrays, page)

    columns_to_keep = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'pct_chg', 'vol', 'bay']
    return render_template("index2.html", grid_data=paginated_data, columns=columns_to_keep, date=date_str,
                           page=page,
                           total_pages=total_pages, stock_count=stock_count)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3211, debug=False)
