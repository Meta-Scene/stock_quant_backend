from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from copy import deepcopy


class KLineProcessor:
    """输入一个含有low和high字段的时间序列进行顶分线和底分线打标
    """
    def __init__(self, df):
        """
        类的构造函数，初始化对象并进行一系列的数据处理操作。
        参数:
        df (pandas.DataFrame): 包含原始K线数据的DataFrame,必须包含high和low的成交价格
        """
        self._validate_input(df)

        # 数据预处理
        self.data = df

    @staticmethod
    def _validate_input(df: pd.DataFrame):
        """输入数据校验"""
        required_cols = {'trade_date', 'high', 'low'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"输入数据缺少必要列：{missing}")

    # 给原始的数据加上需要求出的列设置为默认值
    def _preprocess_data(self):
        kline = [row.to_dict() for _, row in self.data.iterrows()]

        res = []
        for k in kline:
            k['Fmark'], k['Fval'], k['line'] = 0, None, None
            res.append(k)
        return res

    # 按照定义将k线的包含关系去除得到新的k线
    def _remove_merged_kline(self):
        kline = deepcopy(self.kline)
        new_kline = kline[:2]

        # 初始化dir，dir表示目前是增长还是下降
        # dir ： 1上升， -1下降
        for k in kline[2:]:
            k1, k2 = new_kline[-2 : ]
            if k2['high'] > k1['high']:
                dir = 1
            elif k2['low'] < k1['low']:
                dir = -1
            else:
                dir = 1

            cur_high, cur_low = k['high'], k['low']
            last_high, last_low = k2['high'], k2['low']

            """
            如果上升
            高点与低点分别为两者高点与低点的较大值
            反之较小值
            """
            if (cur_high <= last_high and cur_low >= last_low) or (cur_high >= last_high and cur_low <= last_low):
                if dir == 1:
                   new_high = max(last_high, cur_high)
                   new_low = max(last_low, cur_low)
                elif dir == -1:
                    new_high = min(last_high, cur_high)
                    new_low = min(last_low, cur_low)
                else: raise ValueError
                ktmp = k
                k['high'] = new_high
                k['low'] = new_low
                new_kline.pop(-1)
                if (cur_high <= last_high and cur_low >= last_low): tmp = k2
                else : tmp = ktmp
                new_kline.append(tmp)
            else:
                new_kline.append(k)

        return new_kline

    # 按照基本定义求出所有分型， 不考虑笔的限制条件
    def _identify_fractals(self):
        kn = deepcopy(self.processed_kline)
        i = 0
        while(i < len(kn)):
            if i == 0 or i == len(kn) - 1:
                i += 1
                continue
            k1, k2, k3 = kn[i - 1: i + 2]
            i += 1
            if k1['high'] < k2['high'] > k3['high']:
                k2['Fmark'] = 1
                k2['Fval'] = k2['high']

            if k1['low'] > k2['low'] < k3['low']:
                k2['Fmark'] = -1
                k2['Fval'] = k2['low']

        self.processed_kline = kn
        F = [{"trade_date" : x['trade_date'], "Fmark" : x['Fmark'], "Fval" : x['Fval']} for x in self.processed_kline if x['Fmark'] in [1, -1]]
        return F


    # 求出所有的笔的端点所在的k线。
    def getpreLine(self):
        kn = deepcopy(self.processed_kline)
        Fp = sorted(deepcopy(self.fractals), key=lambda  x:x['trade_date'], reverse=False)
        line = []

        """
        当前的分型相较于栈顶的分型类型相同，如果当前更高或者更低将栈弹出，以当前作为新的笔结束点。
                                 如果不同，那么作为笔的结束，需要满足与之前分型中间有一个k线的条件
        """
        for i in range(len(Fp)):
            k = deepcopy(Fp[i])
            if len(line) == 0:
                line.append(k)
            else :
                kpre = line[-1]
               # print(kpre, k)
                if kpre['Fmark'] == k['Fmark']:
                    if (kpre['Fmark'] == 1 and kpre['Fval'] < k['Fval']) or (kpre['Fmark'] == -1 and kpre['Fval'] > k['Fval']):
                        line.pop(-1)
                        line.append(k)
                else:
                    # 如果前面一个是顶分型那么下一个分型必须是底分型，这样下一个分型的值必须小于上一个分型的值，否则上一个顶分型会被pop掉。反之同理。
                    if (kpre['Fmark'] == 1 and k['Fval'] >= kpre['Fval']) or (kpre['Fmark'] == -1 and k['Fval'] <= kpre['Fval']):
                        line.pop(-1)
                        continue

                    knum = [x for x in kn if kpre['trade_date'] <= x['trade_date'] <= k['trade_date']]
                    if len(knum) >= 5:
                        line.append(k)
                        # 当确定了一个笔后如果新加入的这个笔为顶，那么如果与上一个笔之间有更高的点，那么这个笔会被去除，底同理。
                        maxx, minn = 0, 0x3f3f3f3f
                        for x in kn:
                            if kpre['trade_date'] <= x['trade_date'] <= k['trade_date']:
                                maxx = max(x['high'], maxx)
                                minn = min(x['low'], minn)
                        if (kpre['Fmark'] == -1 and k['Fval'] < maxx) or (kpre['Fmark'] == 1 and k['Fval'] > minn):
                            line.pop(-1)
        return line

    def getLine(self):
        line = self.getpreLine()

        datelist = [x['trade_date'] for x in line]
        for k in self.processed_kline:
            if k['trade_date'] in datelist:
                k['line'] = k['Fval']
        return line

    def get_fractals(self):
        flag = 0
        for i in range(self.fractals.shape[0]):
            if self.fractals[i][-2] != 0:
                flag = self.fractals[i][-2]  # 倒数第二列为 Fmark={1,-1,0}
                continue
            if flag == -1:
                self.fractals[i][-2] = 2
            if flag == 1:
                self.fractals[i][-2] = -2
        flag = 0
        for i in range(self.fractals.shape[0] - 1, -1, -1):  # 逆序
            if self.fractals[i][-2] == -1 or self.fractals[i][-2] == 1:
                flag = self.fractals[i][-2]
                continue
            if flag == -1:
                self.fractals[i][-2] = -2
            if flag == 1:
                self.fractals[i][-2] = 2
        # 只标记顶和底
        # i = 1
        # while i < self.fractals.shape[0] - 1:
        #     if self.fractals[i][-2] == 1 or self.fractals[i][-2] == -1:
        #         self.fractals[i + 1, -2] = self.fractals[i - 1, -2] = self.fractals[i, -2]
        #         i += 1
        #     i += 1
        return self.fractals

    def get_data(self):
        self.kline = self._preprocess_data()  # kline: 添加列Fmark， Fval， line
        self.processed_kline = self._remove_merged_kline()  #processed_kline: 去除包含关系后的k线
        self.fractals = self._identify_fractals() # F：所有满足基本定义的分型， {trade_date, Fmark, Fval} Fmark：1：顶分型， -1底分型  Fval：顶分型为high值，底分型为low值
        self.line = self.getLine() # 笔的端点，按照时间排序 {trade_date, Fmark, Fval} Fmark：1：顶分型， -1底分型  Fval：顶分型为high值，底分型为low值
        self.line = pd.DataFrame(self.line)

        # 将笔的数据，加入到raw_data中
        # raw_data多出两列：Fmark， Fval
        self.data['Fmark'] = np.zeros(self.data.shape[0])
        self.data['Fval'] = np.zeros(self.data.shape[0]) #Fval是分型对应的值，如果是顶分型，那么为当日股价最小值，反之最大值
        for i in range(self.data.shape[0]):
            for j in range(self.line.shape[0]):
                if self.data.iloc[i]['trade_date'] == self.line.iloc[j]['trade_date']:
                    self.data.loc[i + self.data.index[0], 'Fmark'] = self.line.loc[j + self.line.index[0], 'Fmark']
                    self.data.loc[i + self.data.index[0], 'Fval'] = self.line.loc[j + self.line.index[0], 'Fval']
                    break
        self.fractals = self.data.values
        self.fractals = self.get_fractals()
        self.data = pd.DataFrame(self.fractals,
                                 columns=self.data.columns)
        # 设置未来行为选项
        pd.set_option('future.no_silent_downcasting', True)
        # 定义替换规则
        replace_dict = {1: 0, -1: 1, -2: 3}
        # 替换指定列中的值
        self.data['Fmark'] = self.data['Fmark'].replace(replace_dict)

        # 将该列转换为整数类型
        self.data['Fmark'] = self.data['Fmark'].astype(int)

        #print("数据标注完毕")

        return self.data

if __name__ == '__main__':
    df = pd.read_csv('000008.SZ.csv')
    L = KLineProcessor(df)
    df1 = L.data
    print(df1)
