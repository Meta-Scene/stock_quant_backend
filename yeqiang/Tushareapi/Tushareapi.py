import tushare as ts

class Tushareapi:
    def __new__(cls):
        # 直接使用提供的 token 进行初始化
        ts.set_token('1c7f85b9026518588c0d0cdac712c2d17344332c9c8cfe6bc83ee75c')
        pro = ts.pro_api()  # 创建 Pro API 实例
        return pro

'''
# 使用示例
if __name__ == "__main__":
    # 初始化连接，此时得到的就是 Pro API 实例
    pro = TushareApi()
    # 示例调用
    data = pro.stock_basic(exchange='', list_status='L')
    print(data.head())
'''
