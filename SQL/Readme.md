# PostgreSQL 数据库操作工具类 🐘

## 🌟 简介  
基于 `psycopg2` 和 `pandas` 封装的 PostgreSQL 操作工具，提供 **表管理、数据插入、高性能查询** 等核心功能，支持与 DataFrame 无缝对接，特别适配含特殊字符的列名场景。


## 📦 安装与依赖  
```bash
pip install psycopg2-binary pandas  # 核心依赖
# 需确保存在自定义配置模块: from globleconfig.database import Database
```

## 使用方法
```bash
在globleconfig中配置好数据库信息
PG = pgsql("your_database_name")
```
