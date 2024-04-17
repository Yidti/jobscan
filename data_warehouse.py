import mysql.connector
import os
from translation import translation_dict
from sqlalchemy import create_engine
import urllib.parse
import pandas as pd
from data_lake import DataLake

class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DataWarehouse(metaclass=SingletonMeta):
    def __init__(self):
        # 'dimension.sql' & 'facts.sql'
        self.sql_script={}
        self.df_no_sql = pd.DataFrame()
        self.df_sql = pd.DataFrame()
        self.db_name = "job_db"
        self.engine = self.connect()

    def initial_db(self):
        self.createDB(self.db_name)
        self.read_sql_file()
        db_name = self.db_name
        sql_dimension = self.sql_script['dimension.sql']
        sql_fact = self.sql_script['fact.sql']
        self.execute_sql(db_name,sql_dimension)
        self.execute_sql(db_name,sql_fact)

    def connect(self):
        # 对密码进行 URL 编码
        password = urllib.parse.quote_plus('Sql@1031')
        # 创建 SQLAlchemy 引擎
        db_name = "job_db"
        # 创建 SQLAlchemy 引擎
        engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost:3306/{db_name}')
        return engine

    # 先從NoSQL抓資料dataframe
    def save_sql(self, data_lake:DataLake):
        self.df_no_sql = data_lake.load_latest()
        
        # 將最新資料列名重命名為與目標表相匹配的名稱
        df_new = self.df_no_sql.rename(columns=translation_dict)
        # 將資料更新至 dimension table (data, selected_columns, column_old, column_new)
        table_name = "experience"
        selected_columns = ["experience"]
        rename = {"experience":"exp_year"}
        id_name = "exp_year"
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)

        table_name = "company"
        selected_columns = ['company_id', 'company', 'company_link']
        rename = {"company":"company_name"}
        id_name = "company_id"
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)
         # 讀取目標表的資料,寫入dimention table
        # df_dimension = df_new[[column_old]].drop_duplicates().reset_index(drop=True)
        # df_dimension = df_dimension.rename(columns = {table_name:column_new})
        
    
    
        # 將資料更新至 fact table
        # self.update_fact_sql(df_new, "job_info")

    def update_fact_sql(self, df_new, table_name):
        # 選擇要存入的 columns
        selected = ['update_date','position','position_link','content', 'experience']

        selected_columns = df_new.loc[:, selected]
        selected_columns.reset_index(inplace=True)
        selected_columns.rename(columns={'id': 'id_job'}, inplace=True)
        # 將 data 部分欄位取代成 dimension 的外鍵 foreign key
        existing_experience = self.read_sql("experience")
        selected_columns = selected_columns.merge(existing_experience, left_on='experience', right_on='exp_year', how='left')
        selected_columns['experience'] = selected_columns['id']
        # 刪除 'id','year_exp' 列，因為它不再需要
        selected_columns.drop(columns=['id', 'exp_year'], inplace=True)
        selected_columns = selected_columns.rename(columns={'experience': 'exp_id'})
        # 儲存至sql (排除重複的id)
        self.insert_sql(selected_columns, "job_info", "id_job")

    
    
    def update_dimension_sql(self, df_new, table_name, selected_columns, rename, id_name):
         # 讀取目標表的資料,寫入dimention table
        df_dimension = df_new[selected_columns].drop_duplicates().reset_index(drop=True)
        # 欄位重新命名
        df_dimension = df_dimension.rename(columns = rename)
        # 儲存至sql (排除重複的id)
        self.insert_sql(df_dimension, table_name, id_name)    

    def insert_sql(self, selected_columns, table_name, id_name):
         # 讀取目標表的資料
        existing_data = self.read_sql(table_name)
        # 檢查要寫入的資料是否已存在於目標表中
        duplicate_rows = selected_columns[selected_columns[id_name].isin(existing_data[id_name])]
        # 找出要寫入的資料中不重複的值
        insert_data = selected_columns[~selected_columns[id_name].isin(existing_data[id_name])]
        # 如果有不重複的值，將其寫入目標表
        if not insert_data.empty:
            insert_data.to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
            print(f"不重複的值已成功寫入{table_name}目標表, 寫入{len(insert_data)}筆")
        else:
            print(f"所有要寫入的值都已存在於{table_name}目標表中，無需進行寫入")
            
    def read_sql(self, table_name):
        existing_data = pd.read_sql(f'SELECT * FROM {table_name}', con=self.engine)
        return existing_data
        
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

