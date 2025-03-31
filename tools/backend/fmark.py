from flask import Flask, request, render_template, jsonify
from decimal import Decimal
from flask_cors import CORS
import os
import sys
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(root_dir)
from yeqiang.database.database import Database  # type: ignore
from QuantitativeStrategys.stategy1.add_signal import add_signal  # 假设此函数已正确实现

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def show_stocks():
    # 获取请求参数
    date = request.args.get('date', '2024-07-08')
    page = int(request.args.get('page', 1))

    # 定义需要保留的字段
    desired_columns = [
        'ts_code', 'trade_date',
        'open', 'high', 'low', 'close',
        'pre_close', 'pct_chg', 'vol'
    ]

    # 构建动态 SQL 查询
    n = 2
    target_pct = 5

    columns_str = ', '.join([f'ns.{col}' for col in desired_columns])
    sql = f"""
    WITH FilteredStocks AS (
        SELECT {', '.join(desired_columns)}
        FROM public.all_stocks_days
        where 1=1
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
        WHERE trade_date = '{date}' 
    )
    SELECT {columns_str}, ns.rn
    FROM NumberedStocks ns
    JOIN TargetRows tr ON ns.ts_code = tr.ts_code
    WHERE ns.rn BETWEEN tr.target_rn - {n} AND tr.target_rn + {n}
    """
    print(sql)
    sql="select * from public.all_stocks_days"
    # 连接数据库并执行查询
    db = Database("stock")
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    c=0
    for i in data:
        print(i)
        c=c+1
        if c==3:
            break
    # 将查询结果转换为 DataFrame
    df = pd.DataFrame(data, columns=desired_columns + ['rn'])

    # 按 ts_code 分组并应用 add_signal 函数
    grouped = df.groupby('ts_code')

    result_arrays = []
    columns_to_keep = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'pct_chg', 'vol', 'bay']
    for name, group in grouped:
        processed_group = add_signal(group)
        # 将 trade_date 列转换为字符串格式
        processed_group['trade_date'] = processed_group['trade_date'].dt.strftime('%Y-%m-%d')
        processed_group = processed_group[columns_to_keep]
        result_arrays.append(processed_group.values.tolist())

    items_per_page = 9
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_stocks = result_arrays[start_index:end_index]
    total_pages = len(result_arrays) // items_per_page + (1 if len(result_arrays) % items_per_page != 0 else 0)

    return jsonify(
                           column_names=columns_to_keep,
                           date=date,
                           stock_count=len(result_arrays),
                           grid_data=paginated_stocks,
                           page=page,
                           total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=False)
