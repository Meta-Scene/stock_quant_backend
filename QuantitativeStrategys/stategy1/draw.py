import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_top_bay(df):
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    # 添加K线
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='K线',
        increasing_line_color='red',   # 阳线颜色
        decreasing_line_color='green'  # 阴线颜色
    ))

    # 添加顶部标记（红色倒三角）
    top_dates = df.index[df['top']==1]
    fig.add_trace(go.Scatter(
        x=top_dates,
        y=df.loc[top_dates, 'high'] * 1.01,
        mode='markers',
        marker=dict(
            color='red',
            size=13,
            symbol='triangle-down'
        ),
        name='顶部信号'
    ))

    # 添加买入标记（绿色正三角）
    bay_dates = df.index[df['bay']==1]
    fig.add_trace(go.Scatter(
        x=bay_dates,
        y=df.loc[bay_dates, 'low'] * 0.99,
        mode='markers',
        marker=dict(
            color='green',
            size=13,
            symbol='triangle-up'
        ),
        name='买入信号'
    ))

    # 添加底分型信号（蓝色正三角）
    low_dates = df.index[df['Fmark']==1]
    fig.add_trace(go.Scatter(
        x=low_dates,
        y=df.loc[low_dates, 'low'] * 0.99,
        mode='markers',
        marker=dict(
            color='blue',
            size=13,
            symbol='triangle-up'
        ),
        name='底部信号'
    ))

    # 配置图表布局
    fig.update_layout(
        title=f"{df['ts_code'][0]} K线图 - [顶部-买入信号]",
        xaxis_title='日期',
        yaxis_title='价格',
        xaxis_rangeslider_visible=True,  # 显示范围滑动条
        template='plotly_white',         # 使用白色主题
        hovermode='x unified',           # 显示统一悬停信息
        height=1000,
        width=2000,
        legend=dict(
            orientation="h",  # 水平图例
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1
        )
    )

    # 显示图表
    #fig.show()