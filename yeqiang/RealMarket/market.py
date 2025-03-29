from RealMarket.CrawlMarket import CrawlMarket
from RealMarket.SaveMarket import SaveMarket
import threading

ts_codes = ['000002.SZ', '000333.SZ', '000338.SZ', '000596.SZ',
            '002984.SZ', '300059.SZ', '300181.SZ', '300760.SZ',
            '600009.SH', '600030.SH', '600066.SH', '601066.SH',
            '601225.SH', '601318.SH', '603195.SH', '688516.SH']


def main():
    # 创建线程列表，用于存储每个股票爬取任务的线程
    threads = []
    # 遍历每个股票代码
    for ts_code in ts_codes:
        # 创建一个线程，目标函数为 CrawlMarket，传入当前股票代码作为参数
        thread = threading.Thread(target=CrawlMarket, args=(ts_code,))
        # 启动线程，开始执行 CrawlMarket 函数
        thread.start()
        # 将线程添加到线程列表中，方便后续管理和等待所有线程完成
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    #SaveMarket(ts_codes)# 手动开启

if __name__ == "__main__":
    #main()
    s=1
    SaveMarket(ts_codes)
