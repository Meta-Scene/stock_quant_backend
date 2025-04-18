# python部分后端接口
## 五日调整
url:`http://120.27.208.55:10015/stock_bay?page=1&date=2025-04-17`

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
url:`http://120.27.208.55:10015/stock_fmark?ts_code=000998.SZ`

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


