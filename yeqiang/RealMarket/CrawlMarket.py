import tushare as ts
import time
import pandas as pd
import datetime
import os

# 获取今天的日期并格式化为YYYYMMDD形式
today = datetime.date.today()
fortoday = today.strftime("%Y%m%d")

# 设置你的token
ts.set_token('1c7f85b9026518588c0d0cdac712c2d17344332c9c8cfe6bc83ee75c')
# 创建pro_api对象
pro = ts.pro_api()

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建数据保存的基础路径
base_path = os.path.join(current_dir,'data', fortoday)
print(base_path)
# 检查目录是否存在，如果不存在则创建
if not os.path.exists(base_path):
    os.makedirs(base_path)

# 定义交易时间范围
morning_start = datetime.time(9, 23)
morning_end = datetime.time(11, 32)
afternoon_start = datetime.time(12, 58)
afternoon_end = datetime.time(15, 2)

def CrawlMarket(ts_code):
    # 标记是否为第一次写入文件，第一次写入时需要写入表头
    now = datetime.datetime.now()
    first_write = now.hour < 10
    # 用于存储已经记录过的时间，避免重复记录同一时间的数据
    timel = []
    while True:
        now = datetime.datetime.now().time()
        # 判断当前时间是否在交易时间段内
        if (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end):
            try:
                # 从东方财富数据源获取指定股票代码的实时行情数据
                doca = ts.realtime_quote(ts_code=ts_code, src='dc')
                # 如果获取的数据不是DataFrame类型，则将其转换为DataFrame
                if not isinstance(doca, pd.DataFrame):
                    doca = pd.DataFrame(doca)
                # 获取股票代码，用于生成文件名
                ts_code = doca["TS_CODE"].iloc[0]
                # 生成文件名，包含股票代码、日期和说明信息
                filename = f"{ts_code} {fortoday}"
                # 拼接完整的文件路径
                full_path = os.path.join(base_path, filename)
                # 检查当前时间是否已经记录过，如果没有记录过则写入文件
                if str(doca["TIME"]) not in timel:
                    # 将数据追加到CSV文件中，第一次写入时写入表头
                    doca.to_csv(full_path + '.csv', mode='a', header=first_write, index=False)
                    # 打印获取到的行情数据
                    # 第一次写入后，后续写入不再需要表头
                    first_write = False
                    # 将当前时间添加到已记录时间列表中
                    timel.append(str(doca["TIME"]))
                    print(doca)
                # 程序暂停，避免频繁请求数据
                time.sleep(2.5)
            except Exception as e:
                # 打印发生的错误信息
                print(f"发生错误: {e}")
                time.sleep(2.5)
        else:
            break
