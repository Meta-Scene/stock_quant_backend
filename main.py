from flask import Flask, request, jsonify, render_template
from database.database import Database
from decimal import Decimal

app = Flask(__name__)

def get_filtered_data(data, column_names, desired_columns):
    """
    过滤数据，只保留所需的列
    :param data: 原始数据
    :param column_names: 原始列名
    :param desired_columns: 所需的列名
    :return: 过滤后的数据和列名
    """
    column_indices = [i for i, col in enumerate(column_names) if col in desired_columns]
    filtered_data = []
    for row in data:
        filtered_row = [row[i] for i in column_indices]
        filtered_data.append(filtered_row)
    filtered_column_names = [column_names[i] for i in column_indices]
    return filtered_data, filtered_column_names


def group_data_by_ts_code(data):
    """
    按 ts_code 分组数据
    :param data: 过滤后的数据
    :return: 按 ts_code 分组的数据
    """
    grouped_data = {}
    for row in data:
        ts_code = row[0]
        if ts_code not in grouped_data:
            grouped_data[ts_code] = []
        grouped_data[ts_code].append(row)
    return grouped_data


def paginate_data(grouped_data, page):
    """
    对数据进行分页处理
    :param grouped_data: 按 ts_code 分组的数据
    :param page: 当前页码
    :return: 分页后的数据、当前页码和总页数
    """
    ts_codes = list(grouped_data.keys())
    total_pages = (len(ts_codes) + 8) // 9
    # 后端验证页码有效性
    page = max(1, min(page, total_pages))
    start_index = (page - 1) * 9
    end_index = start_index + 9
    current_ts_codes = ts_codes[start_index:end_index]
    grid_data = []
    current_grid = []
    for i, ts_code in enumerate(current_ts_codes):
        current_grid.append(grouped_data[ts_code])
        if (i + 1) % 3 == 0:
            grid_data.append(current_grid)
            current_grid = []
    if current_grid:
        grid_data.append(current_grid)
    return grid_data, page, total_pages


@app.route('/api.stock_data', methods=['GET'])
def get_stock_data():
    # 获取请求参数
    date = request.args.get('target_date', '')
    page = request.args.get('page', 1, type=int)

    # 定义需要保留的字段
    desired_columns = [
        'ts_code', 'trade_date',
        'open', 'high', 'low', 'close',
        'pre_close', 'pct_chg', 'vol'
    ]

    if date:
        # 将 yyyy-MM-dd 格式转换为 yyyyMMdd 格式
        date = date
    else:
        date = '2024-01-02'

    # 构建动态 SQL 查询
    n = 10
    tj = "and ts_code LIKE '%BJ'"
    #tj = ''
    sql = f"""
    WITH FilteredStocks AS (
        SELECT *
        FROM public.all_stocks_days
        where 1=1
        {tj}
    ),
    NumberedStocks AS (
        SELECT 
            *,
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
    SELECT ns.*
    FROM NumberedStocks ns
    JOIN TargetRows tr ON ns.ts_code = tr.ts_code
    WHERE ns.rn BETWEEN tr.target_rn - {n} AND tr.target_rn + {n}
    """

    # 连接数据库并执行查询
    db = Database("stock")
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description] if cursor.description else []
    cursor.close()
    conn.close()

    # 过滤数据和列名
    filtered_data, filtered_column_names = get_filtered_data(data, column_names, desired_columns)

    # 按 ts_code 分组数据
    grouped_data = group_data_by_ts_code(filtered_data)

    # 计算股票的数量
    stock_count = len(grouped_data.keys())

    # 分页处理
    grid_data, page, total_pages = paginate_data(grouped_data, page)

    return jsonify(
        grid_data=grid_data,
        column_names=filtered_column_names,
        date=date,
        page=page,
        total_pages=total_pages,
        stock_count=stock_count
    )

if __name__ == '__main__':
    app.run(port=1234, debug=False)
