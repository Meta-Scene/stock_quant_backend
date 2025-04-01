import pandas as pd
from globleconfig.database import Database
from typing import Optional, Union
import warnings
import psycopg2

"""
该类实现了sql语句
"""

class pgsql(object):

    def __init__(self,database):
        db = Database(database)
        warnings.filterwarnings('ignore')
        self.cnn = db.getcnn() #数据库连接
        with self.cnn:
            self.cur = self.cnn.cursor()  #数据库游标

    #检查表是否存在
    def table_exists(self, table_name):
        """
        检查表是否存在
        :param table_name: 表名
        :return: 如果表存在返回 True，否则返回 False
        """
        try:
            # 查询 information_schema.tables 系统表
            query = """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                );
            """
            self.cur.execute(query, (table_name,))
            exists = self.cur.fetchone()[0]
            return exists
        except psycopg2.Error as e:
            print(f"查询表是否存在时出错: {e}")
            return False

    def create_table(self, table_name, columns):
        column_definitions = []
        for col in columns:
            # 如果列名包含特殊字符，用双引号括起来
            if any(c in col for c in ' ()-+/=*&^%$#@!~`"\''):
                col = f'"{col}"'
            column_definitions.append(f"{col} VARCHAR(255)")
        create_table_query = f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                {', '.join(column_definitions)}
            );
        """

        try:
            self.cur.execute(create_table_query)
            self.cnn.commit()
            print(f"表 '{table_name}' 创建成功!")
        except psycopg2.errors.DuplicateTable:
            print(f"表 '{table_name}' 已经存在，无需再次创建。")
        except psycopg2.Error as e:
            print(f"创建表时出错: {e}")

    # 将数据通过df插入数据库的table表中
    def insert_data_bydf(self, df, table_name):
        if not self.table_exists(table_name):
            columns = df.columns.tolist()
            self.create_table(table_name, columns)

        columns = df.columns.tolist()
        # 处理包含特殊字符的列名
        processed_columns = []
        for col in columns:
            if any(c in col for c in ' ()-+/=*&^%$#@!~`"\''):
                col = f'"{col}"'
            processed_columns.append(col)

        insert_statement = f"INSERT INTO {table_name} ({', '.join(processed_columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        for index, row in df.iterrows():
            try:
                self.cur.execute(insert_statement, list(row))
                self.cnn.commit()
                #print(f"第 {index} 行数据插入成功。")
            except psycopg2.Error as e:
                print(f"插入第 {index} 行数据时出错: {e}，数据: {list(row)}")
                self.cnn.rollback()

    # 查看数据库中指定表的数据,指定查询方式
    def view_table_data(self, select_query, table_name):
        if not self.table_exists(table_name):
            print(f"表 '{table_name}' 不存在。")
            return

        try:
            self.cur.execute(select_query)
            rows = self.cur.fetchall()
            column_names = [desc[0] for desc in self.cur.description]
            df = pd.DataFrame(rows, columns=column_names)
            return df
            # print(f"表 '{table_name}' 中的数据：")
            # print(df.to_csv(sep='\t', na_rep='nan'))
        except psycopg2.Error as e:
            print(f"查询表数据时出错: {e}")

    def get_all_data(self, table_name: str) -> pd.DataFrame:
        """
        读取整张表所有数据（高性能方式）

        参数:
            table_name: 目标表名称

        返回:
            包含全部数据的DataFrame，如果表不存在或出错返回空DataFrame
        """
        if not self.table_exists(table_name):
            print(f"表 {table_name} 不存在")
            return pd.DataFrame()

        try:
            # 直接使用pandas的read_sql提高读取性能
            return pd.read_sql(f"SELECT * FROM {table_name}", self.cnn)
        except psycopg2.Error as e:
            print(f"读取数据失败: {e}")
            return pd.DataFrame()

    def get_top_data(self, table_name: str, limit: int,
                     where_clause: Optional[str] = None) -> pd.DataFrame:
        """
        读取指定表前N行数据（支持条件过滤）

        参数:
            table_name: 目标表名
            limit: 要获取的行数（正整数）
            where_clause: 可选过滤条件（不要包含WHERE关键字）

        返回:
            包含查询结果的DataFrame（失败返回空DataFrame）

        示例:
            get_top_data('users', 10, "age > 18 AND status = 'active'")
        """
        # 参数校验
        if not isinstance(limit, int) or limit <= 0:
            print("limit参数必须为正整数")
            return pd.DataFrame()

        if not self.table_exists(table_name):
            print(f"表 {table_name} 不存在")
            return pd.DataFrame()

        try:
            # 构建基础查询
            query = f"SELECT * FROM {table_name}"

            # 添加过滤条件
            if where_clause:
                query += f" WHERE {where_clause}"

            # 添加行数限制
            query += f" LIMIT {limit}"

            # 执行查询
            return pd.read_sql(query, self.cnn)
        except psycopg2.Error as e:
            print(f"查询执行失败: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"发生未知错误: {e}")
            return pd.DataFrame()

    def close_connection(self):
        self.cur.close()


# 使用示例
if __name__ == "__main__":
    PG = pgsql()

    # 示例 DataFrame
    '''data = {
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    }
    df = pd.DataFrame(data)'''

    # 插入数据
    table_name = "Drangon_tigger_data"
    PG.view_table_data(table_name)

    # 关闭数据库连接
    PG.close_connection()