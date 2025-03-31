import pandas as pd
from globleconfig.tushare_api import pro
from datetime import date, timedelta
from QuantitativeStrategys.utils import is_trading_day
from crawlers.StockCrawler import StockCrawler
from SQL.pgsql import pgsql

'''
- [ ] 负向筛选
    - [1 ] 1 St的去掉
    - [1 ] 2 权重股票去掉     市值前200
    - [1 ] 3 新股次新股去掉    上市时间一年内
    - [1 ] 4 人气在后面1/2的去掉
    - [ ] 5 前面连续多天停牌的去掉
    - [ ] 6 5天调整当中有触及涨停的去掉
    - [ ] 7 
- [ ] 正向筛选
    - [1 ] 1 人气排名在前的优先；
    - [ ] 2 在上涨的第一阶段调整的优先；
    - [ ] 3 调整方式幅度不大，5日平的方式优先；
    - [ ] 4 历史股价中出现涨停次数多的优先；
    '''

# 筛选股票
class FilteringStocks():
    def __init__(self):
        # 获取所有正常上市的股票基础信息
        self.data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,list_date,list_status')
        self.data.loc[:, 'list_date'] = pd.to_datetime(self.data['list_date'])
        self.data = self.data[self.data['list_status'] == 'L']

        # 获取市值数据
        today = date.today()
        while not is_trading_day(today):
            today -= timedelta(days=1)
        today = today.strftime('%Y%m%d')
        df_market = pro.daily_basic(ts_code='', trade_date=today, fields='ts_code,total_mv')
        # 合并数据
        self.data = pd.merge(self.data, df_market, on='ts_code', how='left')
        # 股票总数
        self.total_num = self.data.shape[0]

    def get_stocks_data(self):
        return self.data

    # 筛除名称包含ST的股票
    def del_st(self,data):

        no_st_stocks = data[~data['name'].str.contains('ST')]
        print(f"已剔除ST股票，剔除{data.shape[0] - no_st_stocks.shape[0]}支股票. 剩余{no_st_stocks.shape[0]}支股票.")
        return no_st_stocks

    # 筛除上市时间不足一年的股票
    def del_new(self, data):
        old_stocks = data[data['list_date'] < pd.to_datetime('today') - pd.Timedelta(days=365)]
        print(f"已剔除新股和次新股，剔除{data.shape[0] - old_stocks.shape[0]}支股票. 剩余{old_stocks.shape[0]}支股票.")
        return old_stocks

    # 筛选权重股（按市值排名前10%）
    def del_weight(self, data, top_k=100):
        """
        按市值筛选权重股（需先获取市值数据）
        :param top_percent: 市值排名前百分比（默认前10%）
        :return: DataFrame
        """
        # 按市值降序排序
        data = data.sort_values('total_mv', ascending=False)
        # 去除前top_k的股票
        weight_stocks = data[top_k:]
        print(f"已筛除市值前{top_k}的权重股，剩余{len(weight_stocks)}支股票.")
        return weight_stocks

    # 选择人气排行前1/2的股票,并按人气排行排序（升序）
    def select_top_half(self, data):
        SC = StockCrawler()
        # 选择人气前50%, 增加10%冗余查询
        top_half = int(data.shape[0]/2 * 1.1)
        top_codes = SC.get_top_popularity_codes(top_half)
        top_codes_df = pd.DataFrame(top_codes, columns = ['code_num', 'popularity_ranking'])

        data['code_num'] = data['ts_code'].str.extract(r'(\d+)')

        select_bool = data['code_num'].isin(top_codes_df['code_num'])
        topK_stocks = data[select_bool][:top_half]
        topK_stocks = pd.merge(topK_stocks, top_codes_df, on='code_num')

        topK_stocks.drop('code_num', axis=1, inplace = True)
        # 将人气排行榜数据转成整数
        topK_stocks['popularity_ranking'] = topK_stocks['popularity_ranking'].astype(int)
        topK_stocks = topK_stocks.sort_values(by = 'popularity_ranking')

        topK_stocks = topK_stocks[:int(data.shape[0]/2)]

        print(f"已选择股吧人气排行前1/2的股票，剩余{len(topK_stocks)}支股票.")
        return topK_stocks

    # 按照涨跌停次数排序（降序）
    def sort_by_limit_up(self, data):
        PG = pgsql('stock')
        query = 'select * from limitup_pool'
        limit_up_data = PG.view_table_data(query,'limitup_pool')
        print(limit_up_data)


if __name__ == '__main__':
    FS = FilteringStocks()
    stock_data = FS.get_stocks_data()
    # print(stock_data.head())
    stock_data = FS.del_st(stock_data)
    stock_data = FS.del_new(stock_data)
    stock_data = FS.del_weight(stock_data,200)
    # print(stock_data.head())
    stock_data = FS.select_top_half(stock_data)
    stock_data.to_csv('selected_ts_code.csv', index=False)
    # df = pd.read_csv('selected_ts_code.csv')
    FS.sort_by_limit_up(stock_data)
    # print(df)