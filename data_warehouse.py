import mysql.connector
import os
from translation import translation_dict
from sqlalchemy import create_engine
import urllib.parse
import pandas as pd
from data_lake import DataLake



class DataWarehouse():
    def __init__(self):
        # 'dimension.sql' & 'facts.sql'
        self.sql_script={}
        self.df = pd.DataFrame()
        
    # 先從NoSQL抓資料dataframe
    def save_sql(self, data_lake:DataLake):
        self.df = data_lake.load_latest()
    
    # 將data lake資料放到dimension 的 table裏頭
    # def run

    
        
    # create db
    def createDB(self, db_name):
        connection = mysql.connector.connect(
            host="localhost",
            user = "root",
            password = "Sql@1031",
            port = 3306
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        for db in databases:
            if db[0] == db_name:
                print(f"DB is created ({db_name})")
        connection.commit()
        connection.close()

    # 讀取資料夾中的sql檔案
    def read_sql_file(self):
        try:
            # SQL 文件所在的目录路径
            sql_directory = 'sql'
            sql_script = {}
            # 讀取 SQL 檔案
            # 获取目录中所有的 SQL 文件
            sql_files = [f for f in os.listdir(sql_directory) if f.endswith('.sql')]
            for file_name in sql_files:
                sql_file_path = os.path.join(sql_directory, file_name)
                with open(sql_file_path, 'r') as f:
                    sql_content = f.read()
                    sql_script[file_name] = sql_content
            self.sql_script = sql_script
    
        except Exception as e:
            print(f"Error reading SQL script from {sql_directory}: {e}")
            return None

    # 執行sql內容
    def execute_sql(selfk, db_name, sql_script):
        connection = mysql.connector.connect(
            host="localhost",
            user = "root",
            password = "Sql@1031",
            port = 3306,
            database = db_name
        )
    
        try:
            cursor = connection.cursor()
            # 執行 SQL 內容
            cursor.execute(sql_script)
            print("Successfully executed SQL script")
        except Exception as e:
            print(f"Error executing SQL script: {e}")
        finally:
            # 關閉資料庫連接
            connection.close()

