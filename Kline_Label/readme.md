# KLineProcessor 类：K线数据处理与分型、笔识别

## 🌟 简介
`KLineProcessor` 类是一个用于处理K线数据的工具，它可以对输入的K线数据进行预处理、去除K线包含关系、识别分型以及确定笔的端点。该类主要用于金融市场K线数据的技术分析，为后续的交易策略制定提供基础数据支持。

## 📦 安装依赖
在使用该类之前，需要确保已经安装了以下依赖库：
```bash
pip install pandas numpy
```

## 📦 具体说明

对一个时间序列k线进行打标：顶分型，底分型

```bash
Fmark：0：顶分型， 1底分型  2 上升 3下降

Fval：顶分型为high值，底分型为low值
```
## 使用说明
```
df = pd.read_csv('your_path.csv')
L = KLineProcessor(df)
df1 = L.get_data()
```