from globleconfig.database import *
import pandas as pd

def stock_ts_codes(plate, file_dir):
    db = Database('stock')
    cnn = db.getcnn()  # 数据库连接

    # SQL查询，使用DISTINCT去重
    sql_query = f"""
    SELECT DISTINCT ts_code 
    FROM all_stocks_days 
    WHERE ts_code LIKE '%.{plate}'
    """
    # 执行查询并将结果存储在DataFrame中
    ts_codes = pd.read_sql_query(sql_query, cnn)
    # 将深圳证券交易所的股票代码保存至txt文件
    ts_codes['ts_code'].to_csv(file_dir, index=False, header=False)
    return ts_codes