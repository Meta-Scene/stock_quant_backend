from Kline_Label.Label import KLineProcessor
import pandas as pd
def add_signal(stock_df):
    df = stock_df.copy()
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y-%m-%d')
    KP = KLineProcessor(df)
    df = KP.get_data()

    # 确保trade_date是日期类型并按升序排列
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)

    # 填充最近的底分型Fval
    df['last_Fval'] = df['Fval'].where(df['Fmark'] == 1).ffill()

    # 计算前5日的最高价（不包含当日）
    df['prev_5d_max'] = df['high'].shift(1).rolling(5, min_periods=5).max()

    # 新增列记录最近的底分型日期（Fmark=1的日期）
    df['last_Fmark_date'] = df['trade_date'].where(df['Fmark'] == 1).ffill()

    # 计算当前日期与最近底分型日期的天数差
    df['days_since_last_Fmark'] = (df['trade_date'] - df['last_Fmark_date']).dt.days - 1

    # 条件判断
    cond1 = (df['high'] > df['prev_5d_max']) & (df['high'] > df['high'].shift(-1)) & (df['high'] > df['high'].shift(-2))# 当日最高价大于前五日最高价且大于次日最高价
    cond2 = df['last_Fval'].notna() # 前面存在底分型
    cond3 = (df['high'] - df['last_Fval']) / df['last_Fval'] >= 0.1  # 当日相对最近底分型涨幅大于8%
    cond4 = df['last_Fmark_date'].notna() & (df['days_since_last_Fmark'] > 4) #当日相对最近底分型间隔4天（包含休市时间）

    # 标记top信号
    df['top'] = (cond1 & cond2 & cond3 & cond4).astype(int)

    # 标记bay信号（top后第6天）
    df['bay'] = 0.0
    top_indices = df.index[df['top'] == 1]
    for idx in top_indices:

        if idx + 6 < len(df)-1:
            df['pre_close'] = df['pre_close'].astype('float64')
            df.loc[idx + 6, 'bay'] = df.loc[idx+6,"pre_close"]
    return df