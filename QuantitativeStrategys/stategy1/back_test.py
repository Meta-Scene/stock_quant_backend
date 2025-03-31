import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.rc("font",family='SimHei')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 多字体备选
plt.rcParams['axes.unicode_minus'] = False

class BackTest:
    def __init__(self, test_data, principal, loss_threshold, profit_threshold):
        self.data = test_data
        self.principal = principal
        self.initial_principal = principal
        self.loss_threshold = loss_threshold
        self.profit_threshold = profit_threshold
        self.number_of_transactions = 0
        self.number_of_wins = 0
        self.equity_curve = [principal]  # 总资产历史记录
        self.trades = []  # 交易记录
        self.current_buy_price = None
        self.current_buy_date = None
        self.current_pre_5_low = None
        self.current_pre_5_mean = None
        self.break_ma5_flag = False
        # 计算MA5（动态五日均价，包括当天）
        self.data['ma5'] = self.data['close'].rolling(window=5, min_periods=1).mean()

    def start_test(self):
        pos = 0
        holding = False
        current_shares = 0

        while pos < len(self.data):
            row = self.data.iloc[pos]

            # 计算当前总资产
            if holding:
                total_equity = current_shares * row['close']
            else:
                total_equity = self.principal
            self.equity_curve.append(total_equity)

            # 交易逻辑
            if not holding:
                if row['bay'] != 0:  # 买入信号
                    buy_price = row['open']
                    amount_after_fee = self.principal * (1 - 0.0001)
                    current_shares = amount_after_fee / buy_price
                    self.principal = 0
                    holding = True
                    self.current_buy_price = buy_price
                    self.current_buy_date = pos
                    # 计算前5日最低价和均价
                    window_start = max(0, pos - 5)
                    window_end = pos
                    self.current_pre_5_low = self.data.iloc[window_start:window_end]['low'].min()
                    self.current_pre_5_mean = self.data.iloc[window_start:window_end]['close'].mean()
                    self.break_ma5_flag = False
                    self.number_of_transactions += 1
                    self.trades.append({
                        'type': 'buy',
                        'date': pos,
                        'price': buy_price,
                        'shares': current_shares
                    })
                    pos += 1
                    continue
            else:
                days_held = pos - self.current_buy_date

                # 条件1：第二天检查买入当天收盘价是否跌破前5日最低价
                if days_held == 1:
                    buy_day_close = self.data.iloc[self.current_buy_date]['close']
                    if buy_day_close < self.current_pre_5_low:
                        sell_price = row['open']  # 第二天开盘卖出
                        self._execute_sell(pos, sell_price, current_shares, 'condition1')
                        holding = False
                        self._reset_holding_vars()
                        pos += 1
                        continue

                # 条件2：第三天检查三天内是否未突破前5日均价
                if days_held == 3:
                    start_day = self.current_buy_date + 1
                    end_day = self.current_buy_date + 3
                    condition_met = True
                    for day in range(start_day, min(end_day + 1, len(self.data))):
                        if self.data.iloc[day]['close'] > self.current_pre_5_mean:
                            condition_met = False
                            break
                    if condition_met:
                        sell_price = row['close']  # 第三天收盘卖出
                        self._execute_sell(pos, sell_price, current_shares, 'condition2')
                        holding = False
                        self._reset_holding_vars()
                        pos += 1
                        continue

                # 条件3：三天后突破MA5后再次跌破
                if days_held > 3:
                    current_ma5 = row['ma5']
                    if not self.break_ma5_flag:
                        if row['close'] > current_ma5:
                            self.break_ma5_flag = True
                    else:
                        if row['close'] < current_ma5:
                            sell_price = row['close']  # 当天收盘卖出
                            self._execute_sell(pos, sell_price, current_shares, 'condition3')
                            holding = False
                            self._reset_holding_vars()
                            pos += 1
                            continue

                # 强制平仓检查
                if pos == len(self.data) - 1:
                    sell_price = row['close']
                    self._execute_sell(pos, sell_price, current_shares, 'force')
                    holding = False
                    self._reset_holding_vars()

            pos += 1

    def _execute_sell(self, pos, sell_price, shares, sell_type):
        # 计算卖出金额（扣除0.06%手续费和印花税）
        sell_amount = shares * sell_price
        self.principal = sell_amount * (1 - 0.0006)
        # 记录交易
        profit = self.principal - (shares * self.current_buy_price)
        self.trades.append({
            'type': 'sell',
            'date': pos,
            'price': sell_price,
            'profit': profit,
            'sell_type': sell_type
        })
        # 更新胜率统计
        if profit > 0:
            self.number_of_wins += 1

    def _reset_holding_vars(self):
        self.current_buy_price = None
        self.current_buy_date = None
        self.current_pre_5_low = None
        self.current_pre_5_mean = None
        self.break_ma5_flag = False


    def plot_performance(self):
        sns.set_style("whitegrid")
        plt.figure(figsize=(14, 8))

        # 绘制资金曲线
        plt.plot(self.equity_curve, label='Total Capital', color='dodgerblue', lw=1.5)

        # 标记买卖点
        buy_dates = [t['date'] for t in self.trades if t['type'] == 'buy']
        buy_prices = [t['price'] for t in self.trades if t['type'] == 'buy']
        plt.scatter(buy_dates, [self.equity_curve[i + 1] for i in buy_dates],
                    marker='^', color='limegreen', s=100, label='bay')

        sell_dates = [t['date'] for t in self.trades if t['type'] == 'sell']
        plt.scatter(sell_dates, [self.equity_curve[i + 1] for i in sell_dates],
                    marker='v', color='tomato', s=100, label='sell')

        plt.title("Capital curves and trading signals", fontsize=14)
        plt.xlabel("datetime")
        plt.ylabel("Asset amount (yuan)")
        plt.legend()

        # 绘制统计图表
        plt.figure(figsize=(12, 4))
        plt.subplot(131)
        self._plot_win_rate()
        plt.subplot(132)
        self._plot_profit_dist()
        plt.subplot(133)
        self._plot_drawdown()
        plt.tight_layout()
        plt.show()

    def _plot_win_rate(self):
        win_trades = len([t for t in self.trades if t['type'] == 'sell' and t['profit'] > 0])
        loss_trades = len(self.trades) // 2 - win_trades
        plt.pie([win_trades, loss_trades],
                labels=[f'Profit ({win_trades})', f'Loss ({loss_trades})'],
                colors=['#4CAF50', '#F44336'],
                autopct='%1.1f%%', startangle=90)
        plt.title('Win Rate Distribution')

    def _plot_profit_dist(self):
        profits = [t['profit'] for t in self.trades if t['type'] == 'sell']
        sns.histplot(profits, bins=20, kde=True, color='purple')
        plt.axvline(0, color='gray', linestyle='--')
        plt.title('Profit and loss distribution of a single transaction')
        plt.xlabel('Profit and loss amount (yuan)')

    def _plot_drawdown(self):
        # 计算最大回撤
        peak = self.equity_curve[0]
        max_dd = 0
        dd = []
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd.append((peak - equity) / peak)
        max_dd = max(dd) * 100

        plt.plot(dd, color='darkorange')
        plt.fill_between(range(len(dd)), dd, color='gold', alpha=0.3)
        plt.title(f'Max retracement: {max_dd:.1f}%')
        plt.ylabel('retracement ratio')

    def print_report(self, out = False):
        final_equity = self.equity_curve[-1]
        total_return = final_equity - self.initial_principal
        return_pct = (total_return / self.initial_principal) * 100
        win_rate = (self.number_of_wins / (len(self.trades) // 2)) * 100 if self.trades else 0

        if out:
            print("=" * 40)
            print(f"{self.data.loc[0,'ts_code'] } {'回测报告':^20}")
            print("=" * 40)
            print(f"止损率: {self.loss_threshold * 100:.2f}%")
            print(f"止盈率: {self.profit_threshold * 100:.2f}%")
            print(f"初始本金: {self.initial_principal:.2f}元")
            print(f"最终资产: {final_equity:.2f}元")
            print(f"总收益率: {return_pct:.2f}%")
            print(f"交易次数: {len(self.trades) // 2}次")
            print(f"胜   率: {win_rate:.2f}%")
            print("-" * 40)
        #self.plot_performance()
        return final_equity, win_rate
