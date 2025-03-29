import pandas as pd

class StockDataProcessor:
    def process_data(self, df):
        # 检查数据量是否足够，如果数据行数小于等于1，则打印提示信息并返回空字典
        if len(df) <= 1:
            print("数据不足，跳过...")
            return {}

        # 将日期和时间列合并为一个日期时间列
        df['DATETIME'] = pd.to_datetime(df['DATE'].astype(str) + ' ' + df['TIME'])
        # 过滤掉开盘集合竞价的数据（09:25的数据）
        df = df[~df['DATETIME'].dt.time.astype(str).str.startswith('09:25')]
        # 过滤掉早于09:30的数据
        df = df[df['DATETIME'].dt.time >= pd.to_datetime('09:30:00').time()]
        # 将日期时间列设置为索引
        df.set_index('DATETIME', inplace=True)

        # 定义需要生成K线数据的时间间隔
        intervals = ['1min', '5min']
        # 用于存储不同时间间隔的K线数据
        kline_data = {}

        # 遍历不同的时间间隔
        for interval in intervals:
            # 对价格列按指定时间间隔进行重采样
            resampled = df['PRICE'].resample(interval)
            # 计算每个时间间隔的开盘价
            open_price = resampled.first()
            # 计算每个时间间隔的最高价
            high_price = resampled.max()
            # 计算每个时间间隔的最低价
            low_price = resampled.min()
            # 计算每个时间间隔的收盘价
            close_price = resampled.last()
            # 对成交量列按指定时间间隔进行重采样并求和
            volume = df['VOLUME'].resample(interval).sum()
            # 对成交额列按指定时间间隔进行重采样并求和
            amount = df['AMOUNT'].resample(interval).sum()

            # 创建一个包含K线数据的DataFrame
            kline = pd.DataFrame({
                'OPEN': open_price,
                'HIGH': high_price,
                'LOW': low_price,
                'CLOSE': close_price,
                'VOLUME': volume,
                'AMOUNT': amount
            })

            # 调整索引，将1分钟K线数据的索引向后移动1分钟
            if interval == '1min':
                kline.index += pd.Timedelta(minutes=1)
            # 调整索引，将5分钟K线数据的索引向后移动5分钟
            elif interval == '5min':
                kline.index += pd.Timedelta(minutes=5)

            # 定义早盘交易开始时间
            morning_start = pd.to_datetime('09:31:00').time()
            # 定义早盘交易结束时间
            morning_end = pd.to_datetime('11:30:00').time()
            # 定义午盘交易开始时间
            afternoon_start = pd.to_datetime('13:01:00').time()
            # 定义午盘交易结束时间
            afternoon_end = pd.to_datetime('15:00:00').time()

            # 生成过滤条件，筛选出早盘和午盘交易时间内的数据
            condition = (
                (kline.index.time >= morning_start) & (kline.index.time <= morning_end) |
                (kline.index.time >= afternoon_start) & (kline.index.time <= afternoon_end)
            )
            # 根据过滤条件筛选K线数据
            kline = kline[condition]

            # 处理1分钟K线数据的特殊情况
            if interval == '1min':
                # 对缺失值进行前向填充
                kline = kline.ffill()
                # 将成交量列的缺失值填充为0
                kline['VOLUME'] = kline['VOLUME'].fillna(0)
                # 将成交额列的缺失值填充为0
                kline['AMOUNT'] = kline['AMOUNT'].fillna(0)

            # 处理最后一分钟的数据
            if not kline.empty:
                # 获取K线数据的最后一个索引
                last_index = kline.index[-1]
                # 检查最后一分钟的成交量和成交额是否都为0
                if kline.loc[last_index, 'VOLUME'] == 0 and kline.loc[last_index, 'AMOUNT'] == 0:
                    # 获取最后一分钟的原始数据
                    last_minute_data = df[df.index >= last_index - pd.Timedelta(minutes=1)].iloc[0]
                    # 将最后一分钟的成交量替换为原始数据的成交量
                    kline.loc[last_index, 'VOLUME'] = last_minute_data['VOLUME']
                    # 将最后一分钟的成交额替换为原始数据的成交额
                    kline.loc[last_index, 'AMOUNT'] = last_minute_data['AMOUNT']

            # 将处理好的K线数据存入字典
            kline_data[interval] = kline

        # 返回不同时间间隔的K线数据
        return kline_data


if __name__ == "__main__":
    # 指定单个CSV文件的路径
    file_path = r"C:\Users\dell\Desktop\yeqiang\RealDeal\data\20250228\000001.SZ.csv"
    # 从指定路径读取CSV文件并转换为DataFrame
    df = pd.read_csv(file_path)
    # 创建StockDataProcessor类的实例
    processor = StockDataProcessor()
    # 调用process_data方法处理数据
    results = processor.process_data(df)
    if results:
        # 提取文件名（不包含路径和扩展名）
        base_name = file_path.split("\\")[-1].split('.')[0]
        # 遍历结果中的每个文件名及其对应的K线数据
        print(f"\nResults for {base_name}:")
        # 遍历每个时间间隔及其对应的K线数据
        for interval, data in results.items():
            print(f"\n{interval}线数据：")
            # 打印该时间间隔的K线数据
            print(data)
    else:
        
        print(f"Skipped {file_path} due to no data.")
    
