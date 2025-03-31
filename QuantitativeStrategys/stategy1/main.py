#-*- coding: utf-8 -*-
import pandas as pd
from globleconfig.database import *
from draw import plot_top_bay
from add_signal import add_signal
from back_test import BackTest
from utils import stock_ts_codes
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# 将深圳证券交易所的股票代码保存至txt文件
# SZ = stock_ts_codes('SZ', 'SZ.txt')

# 将上海证券交易所的股票代码保存至txt文件
# SH = stock_ts_codes('SH', 'SH.txt')

# 将北京证券交易所的股票代码保存至txt文件
# BJ = stock_ts_codes('BJ', 'BJ.txt')


# 1. 数据读取
db = Database('stock')
cnn = db.getcnn() #数据库连接

ts_codes = pd.read_csv("SZ.txt")
SIZE = 1
sampleed_codes = ts_codes.sample(n=SIZE).values
print(len(sampleed_codes))

Final_principal = []
Win_rate = []
principal, loss_threshold, profit_threshold = 10000, 0.04, 0.07
for i in range(len(sampleed_codes)):
    ts_code = sampleed_codes[i][0]
    sql_query = f"""SELECT ts_code,trade_date,open,high,low,close,pre_close FROM all_stocks_days where ts_code='{ts_code}' """
    stock_df = pd.read_sql_query(sql_query, cnn)
    # 2. 数据预处理：添加底分型/顶分型信号、top/bay信号
    stock_df['pre_close'] = stock_df['pre_close'].astype('float64')
    df = add_signal(stock_df)

    df.drop(['last_Fval', 'Fval', 'prev_5d_max', 'last_Fmark_date', 'days_since_last_Fmark'], axis = 1, inplace = True)

    # 3. 创建交互式图表
    #plot_top_bay(df)

    # 4. 回测
    BT = BackTest(df, principal, loss_threshold, profit_threshold)
    BT.start_test()
    final_equity, win_rate = BT.print_report()
    Final_principal.append(final_equity)
    Win_rate.append(win_rate)

print("=" * 40)
print(f"{SIZE}支股票 {'回测报告':^20}")
print("=" * 40)
print(f"止损率: {loss_threshold * 100:.2f}%")
print(f"止盈率: {profit_threshold * 100:.2f}%")
print(f"综合净盈亏额：{sum(Final_principal) - principal*SIZE:.2f}元")
print(f"综合盈利率：{(sum(Final_principal) - principal*SIZE) / principal*SIZE:.2f}%")
print(f"平均胜率：{sum(Win_rate) / SIZE:.2f}%")

# 000338.SZ
# 美的集团  长江电力  工商银行 新易盛(300502.SZ) 浪潮信息(000977.SZ) 比亚迪 up
# 五粮液(000858.SZ) 药明康德(603259.SH) 隆基绿能 海康威视(002415.SZ) 海天味业 金龙鱼 down

