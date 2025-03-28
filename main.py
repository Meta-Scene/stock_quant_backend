from flask import Flask, render_template, request, jsonify
from database.database import Database
from decimal import Decimal

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_stock_data():
    db = Database("stock")
    conn = db.connect()
    cursor = conn.cursor()
    date = request.args.get('target_date', '')

    # 定义需要保留的字段
    desired_columns = [
        'ts_code', 'trade_date', 
        'open', 'high', 'low', 'close', 
        'pre_close', 'pct_chg', 'vol'
    ]

    data = []
    column_names = []

    if date:
        # 将 yyyy-MM-dd 格式转换为 yyyyMMdd 格式
        date = date.replace('-', '')
    else:
        date = '20240102'

    # 构建动态 SQL 查询
    sql = f"""
    WITH FilteredStocks AS (
        SELECT *
        FROM public.all_stocks_days
        WHERE ts_code LIKE '%BJ'
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
    WHERE ns.rn BETWEEN tr.target_rn - 1 AND tr.target_rn + 1
    """

    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
    except Exception as e:
        print(f"数据库查询出错: {e}")
        data = []
        column_names = []

    # 过滤数据和列名
    column_indices = [i for i, col in enumerate(column_names) if col in desired_columns]
    filtered_data = []
    for row in data:
        filtered_row = [row[i] for i in column_indices]
        filtered_data.append(filtered_row)

    filtered_column_names = [column_names[i] for i in column_indices]

    cursor.close()
    conn.close()

    # 将日期转换回 yyyy-MM-dd 格式用于前端显示
    date = date[0:4] + "-" + date[4:6] + "-" + date[6:]

    # 按 ts_code 分组数据
    grouped_data = {}
    for row in filtered_data:
        ts_code = row[0]
        if ts_code not in grouped_data:
            grouped_data[ts_code] = []
        grouped_data[ts_code].append(row)

    # 获取当前页码并进行后端验证
    page = request.args.get('page', 1, type=int)
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
    '''
    return jsonify(
        grid_data=grid_data,
        column_names=filtered_column_names,
        date=date,
        page=page,
        total_pages=total_pages)'''
    return render_template(
        "index.html",
        grid_data=grid_data,
        column_names=filtered_column_names,
        date=date,
        page=page,
        total_pages=total_pages)

if __name__ == '__main__':
    app.run(port=3211, debug=False)
