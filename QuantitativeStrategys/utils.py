from pandas_market_calendars import get_calendar
from datetime import datetime

# 判断date是否为交易日
def is_trading_day(today_date):
    # today_date = datetime.strptime(today_date, "%Y%m%d")
    # 获取上海证券交易所的交易日历
    sse_calendar = get_calendar('XSHG')

    # 判断是否为交易日
    is_trading_day = sse_calendar.valid_days(start_date=today_date, end_date=today_date).shape[0] > 0
    return is_trading_day