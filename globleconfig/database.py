import psycopg2

"""
数据库连接参数
"""
class Database(object):

    def __init__(self,database):
        self.configs = {
            'db_type' : 'pg_sql',
            'db_host' : '172.16.34.116',
            'db_user' : 'postgres',
            'db_passwd' : '123456',
            'db_database' : database,
            'db_port' : 5432
        }
    def getcnn(self):
        config = self.configs
        return psycopg2.connect(host = config['db_host'], user = config['db_user'],
                                port = config['db_port'], password = config['db_passwd'], database = config['db_database'])