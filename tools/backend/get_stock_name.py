import pandas as pd

def get_stock_name(ts_code):
    """
    根据 ts_code 从 stock_basic.csv 中查询股票名称
    :param ts_code: 股票代码（如 '000001.SZ'）
    :return: 股票名称（若未找到或文件异常，返回 None）
    """
    file_path = 'stock_basic.csv'
    try:
        # 读取 CSV 文件并构建字典
        df = pd.read_csv(file_path, encoding='GBK')
        stock_dict = {row['ts_code']: row['name'] for _, row in df.iterrows()}
        # 返回对应股票名称，若不存在则返回 None
        return stock_dict.get(ts_code)
    except Exception as e:
        print(f"读取文件或查询股票名称时出错：{e}")
        return None

# 示例用法
# print(get_stock_name('000001.SZ'))  # 输出：平安银行
