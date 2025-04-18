# python部分后端接口
## 五日调整
举例 url:`http://120.27.208.55:10015/stock_bay?page=1&date=2025-04-17`

返回数据格式：
```
"column_names": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay"
  ],
```
## fmark查询
举例 url:`http://120.27.208.55:10015/stock_fmark?ts_code=000998.SZ`

返回数据格式：
```
{
  "columns": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay",
    "Fmark",
    "MA120",
    "MA250"
  ],
```

## 最终版
### 五日调整
url:`http://172.16.32.93:10015/stock_bay`

返回数据格式：
```
{
  "columns": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay",
    "MA120",
    "MA250",
    "name"
  ],
```

### fmark查询
url:`http://172.16.32.93:10015/stock_fmark`

返回数据格式：
```
{
  "columns": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay",
    "Fmark",
    "MA120",
    "MA250",
    "name"
  ],
```
# Java部分后端接口
## 最终版
所有：`http://120.27.208.55:8080/api/stock/data`

涨停：`http://120.27.208.55:8080/api/stock/limit-up`

跌停：`http://120.27.208.55:8080/api/stock/limit-down`

半年线：`http://120.27.208.55:8080/api/stock/half-year-line`

年线：`http://120.27.208.55:8080/api/stock/year-line`

返回数据格式全部改成：
```
{
  "columns": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay",
    "MA120",
    "MA250",
    "name"
  ],
```

## 当前版本
目前看到的服务器版本是：

```
  "column_names": [
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "pct_chg",
    "vol",
    "bay",
    "ma5",
    "ma10",
    "ma120",
    "ma250"
  ],
```

局域网ip：
`172.16.32.88`



