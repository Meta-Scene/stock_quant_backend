import psycopg2

class Database:
    def __init__(self, database):
        # 初始化数据库连接参数，将传入的 database 参数整合到连接参数中
        self.db_params = {
            "host": "localhost",
            "port": "5432",
            "database": database,
            "user": "postgres",
            "password": "123456"
        }

    def connect(self):
        try:
            # 使用 psycopg2 建立数据库连接
            connection = psycopg2.connect(**self.db_params)
            return connection
        except (Exception, psycopg2.Error) as error:
            # 若连接过程中出现异常，打印错误信息
            print("连接数据库时发生错误：", error)
            return None

    def close(self, connection):
        if connection:
            # 关闭数据库连接
            connection.close()
'''
# 以下是使用示例
if __name__ == "__main__":
    # 创建 Database 类的实例，传入数据库名
    db = Database("dailyquote")
    # 调用 connect 方法建立数据库连接
    conn = db.connect()
    if conn:
        # 若连接成功，调用 close 方法关闭连接
        db.close(conn)
'''
