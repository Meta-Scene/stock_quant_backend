# 股票数据查询接口文档

## 1. 接口基本信息
- **接口地址**：`http://127.0.0.1:1234/api.stock_data`
- **请求方法**：`GET`
- **功能描述**：获取指定日期（前后十天共21天）的股票历史数据，支持分页展示，返回包含股票代码、交易日期、开盘价、收盘价、最高价、最低价等关键指标的结构化数据。

---

## 2. 请求参数
| 参数名称       | 数据类型 | 是否必填 | 描述                          | 示例值         | 备注                          |
|----------------|----------|----------|-------------------------------|----------------|-------------------------------|
| `target_date`  | string   | 否       | 查询日期（格式：`yyyy-MM-dd`）| `2024-01-12`    | 未输入日期时默认为`2024-01-02` |
| `page`         | number   | 否       | 目标页码（从1开始）           | `1`            | 后端自动验证，超出范围时调整  |

---

## 3. 响应数据结构

### 3.1 整体结构示例
```json
{
  "column_names": [
    "ts_code", "trade_date", "open", "high", 
    "low", "close", "pre_close", "pct_chg", "vol"],

  "date": "2024-01-12",

  "grid_data": [
                    [
                        [
                            ["430017.BJ","20240111",14.32,14.93,14.03,14.23,13.92,2.23,30076.77],
                            ["430017.BJ","20240112",13.96,14.14,13.27,13.27,14.23,-6.75,35741.96],
                            ["430017.BJ","20240115",13.23,13.41,12.72,12.75,13.27,-3.92,23413.75]],
                        [
                            ["430047.BJ","20240111",17.25,18.5,17.25,18.12,17.08,6.09,30244.24],
                            ["430047.BJ","20240112",17.94,18.27,17.52,17.66,18.12,-2.54,18176.61],
                            ["430047.BJ","20240115",17.52,18.15,17.52,17.84,17.66,1.02,15487.43]],
                        [
                            ["430090.BJ","20240111",5.01,5.3,5.01,5.12,5.04,1.59,113921.8],
                            ["430090.BJ","20240112",5.1,5.12,4.39,4.41,5.12,-13.87,195351.01],
                            ["430090.BJ","20240115",4.36,4.44,4.06,4.07,4.41,-7.71,136154.68]]],
                    [
                        [
                            ["430139.BJ","20240111",13.2,13.6,13.17,13.47,13.19,2.12,23430.29],
                            ["430139.BJ","20240112",13.35,13.57,12.53,12.55,13.47,-6.83,32109.02],
                            ["430139.BJ","20240115",12.51,13.16,11.95,12.55,12.55,0.0,34289.83]],
                        [
                            ["430198.BJ","20240111",8.96,9.3,8.84,9.05,8.89,1.8,46919.64],
                            ["430198.BJ","20240112",9.06,9.07,7.87,7.91,9.05,-12.6,71167.1],
                            ["430198.BJ","20240115",7.98,8.0,7.44,7.5,7.91,-5.18,54171.58]],
                        [
                            ["430300.BJ","20240111",12.19,12.68,12.19,12.3,12.33,-0.24,22148.13],
                            ["430300.BJ","20240112",12.11,12.35,10.45,10.45,12.3,-15.04,40485.19],
                            ["430300.BJ","20240115",10.45,10.9,10.0,10.34,10.45,-1.05,26087.01]]],
                    [
                        [
                            ["430418.BJ","20240111",16.23,16.56,15.81,16.25,16.42,-1.04,16843.22],
                            ["430418.BJ","20240112",16.11,16.34,14.53,14.55,16.25,-10.46,27629.35],
                            ["430418.BJ","20240115",14.34,15.09,13.92,14.55,14.55,0.0,23918.28]],
                        [
                            ["430425.BJ","20240111",16.88,16.97,16.42,16.81,16.81,0.0,16275.92],
                            ["430425.BJ","20240112",16.91,16.91,14.26,14.27,16.81,-15.11,30662.16],
                            ["430425.BJ","20240115",14.07,14.91,13.83,14.08,14.27,-1.33,16026.4]],
                        [
                            ["430476.BJ","20240111",12.93,13.24,12.84,13.18,12.93,1.93,6864.85],
                            ["430476.BJ","20240112",13.25,13.71,12.39,12.45,13.18,-5.54,11543.37],
                            ["430476.BJ","20240115",12.47,12.54,11.81,11.96,12.45,-3.94,10675.44]]]],
  "page":1,
  "stock_count":239,
  "total_pages":27
  }