import mysql.connector
import os
from translation import translation_dict
from sqlalchemy import create_engine, text
import urllib.parse
import pandas as pd
from data_lake import DataLake
import time
        
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
        self.engine = self.connect()
        self.db_name = "job_db"
        self.host="localhost"
        self.user = "root"
        self.password = "Sql@1031"
        self.port = 3306

    def initial_db(self):
        # self.deleteDB(self.db_name)
        self.createDB(self.db_name)
        self.read_sql_file()
        db_name = self.db_name
        sql_dimension = self.sql_script['dimension.sql']
        sql_fact = self.sql_script['fact.sql']
        self.execute_sql(db_name,sql_dimension)
        time.sleep(1)  # 等待 1 秒，確保 dimension 表建立完成
        self.execute_sql(db_name, sql_fact)
    
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
        # 將資料更新至 dimension table
        self.update_all_dimension(df_new)
        # 將資料更新至 fact table
        self.update_fact_sql(df_new, "job_info")

    def update_all_dimension(self, df_new):
        # 將資料更新至 dimension table (data, selected_columns, column_old, column_new)

        table_name = "company"
        selected_columns = ['company_id', 'company', 'company_link']
        rename = {"company":"company_name"}
        id_name = ["company_id","company_name","company_link"]
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)

        table_name = "industry"
        selected_columns = ['industry_id', 'industry']
        rename = {"industry":"industry_name"}
        id_name = ["industry_id","industry_name"]
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)

        table_name = "location_city_region"
        selected_columns = ['city', 'region']
        rename = {}
        id_name = ['city', 'region']
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)

        # location table (refer: location_city_region)
        table_name = "location"
        dimension_table_name = "location_city_region"
        merge = [['city','region'],['city','region']]
        drop = ['city','region']
        selected_columns = ['city', 'region', 'address']
        rename = {'id': 'city_region_id'}
        id_name = ['city_region_id', 'address']
        df = df_new[selected_columns].drop_duplicates().reset_index(drop=True)
        df_existing = self.read_sql(dimension_table_name)
        df = self.replace_foreign_key(df, df_existing, merge, drop, rename)
        self.insert_sql(df, table_name, id_name)

        
        self.one_column_sql(df_new, "experience")
        self.one_column_sql(df_new, "education")
        
        self.item_list_sql(df_new, "category_item","category")
        self.item_list_sql(df_new, "major_item","major")
        self.item_list_sql(df_new, "language_item","language")
        self.item_list_sql(df_new, "tool_item","tool")
        self.item_list_sql(df_new, "skill_item","skill")

        self.one_column_sql(df_new, "benefits")
        self.one_column_sql(df_new, "type")
        self.one_column_sql(df_new, "management")
        self.one_column_sql(df_new, "business_trip")
        self.one_column_sql(df_new, "working_hours")
        self.one_column_sql(df_new, "vacation")
        self.one_column_sql(df_new, "available")
        self.one_column_sql(df_new, "quantity")

    def update_fact_sql(self, df_new, table_name):
        df_new.reset_index(inplace=True)
        df_new.rename(columns={'id': 'job_id'}, inplace=True)
        df_new = self.replace_all_foreign_key(df_new)
        # 選擇要存入的 columns
        selected =['job_id','update_date','position','position_link',
                   'company_id','industry_id','location_id','experience_id',
                   'education_id', 'content','other', 'benefits_id',
                  'type_id', 'management_id','business_trip_id','working_hours_id',
                   'vacation_id', 'available_id', 'quantity_id', 'welfare']
        df_new = df_new.loc[:, selected]
        # print(f"columns:{len(df_new.columns)}")
        # 儲存至sql (排除重複的id)
        self.insert_sql(df_new, "job_info", "job_id")

    def replace_existing_table(self, table_name, table_name_reference, merge, drop):
        df_existing = self.read_sql(table_name)
        df_existing.set_index('id', inplace=True)
        df_existing_ref = self.read_sql(table_name_reference)
        df_existing = df_existing.merge(df_existing_ref, left_on=merge[0], right_on=merge[1], how='left')
        df_existing.drop(columns = drop, inplace=True)
        return df_existing
        
    def replace_all_foreign_key(self, df_new):
        # 將 data 部分欄位取代成 dimension 的外鍵 foreign key
        table_name = "location"
        table_name_reference = "location_city_region"
        merge = [['city_region_id'],['id']]
        drop = ['city_region_id']
        df_existing = self.replace_existing_table(table_name, table_name_reference, merge, drop)
        
        merge = [['city','region','address'],['city','region','address']]
        drop = ['city','region','address']
        rename = {'id': 'location_id'}
        df_new = self.replace_foreign_key(df_new, df_existing, merge, drop, rename)

        df_new = self.one_foreign_key(df_new, "experience")
        df_new = self.one_foreign_key(df_new, "education")
        df_new = self.one_foreign_key(df_new, "benefits")
        df_new = self.one_foreign_key(df_new, "type")
        df_new = self.one_foreign_key(df_new, "management")
        df_new = self.one_foreign_key(df_new, "business_trip")
        df_new = self.one_foreign_key(df_new, "working_hours")
        df_new = self.one_foreign_key(df_new, "vacation")
        df_new = self.one_foreign_key(df_new, "available")
        df_new = self.one_foreign_key(df_new, "quantity")

        
        return df_new
    def one_foreign_key(self, df_new, column_name):
        df_existing = self.read_sql(column_name)
        merge = [[column_name],[column_name]]
        drop = [column_name]
        rename = {'id': f'{column_name}_id'}
        df_new = self.replace_foreign_key(df_new, df_existing, merge, drop, rename)
        return df_new
        
    def replace_foreign_key(self, df_new, existing, merge, drop, rename):
        df_new = df_new.merge(existing, left_on=merge[0], right_on=merge[1], how='left')
        df_new.drop(columns = drop, inplace=True)
        df_new = df_new.rename(columns=rename)
        return df_new

    def explode_list_sql(self, df_new, table_name, selected_column, rename, id_name):
        df_item = df_new[selected_column].str.split(',')
        df_item = df_item.explode(selected_column).reset_index(drop=True)
        df_item = pd.DataFrame({selected_column: df_item})
        df_item = df_item.drop_duplicates().reset_index(drop=True)
        df_item = df_item.rename(columns = rename)
        self.insert_sql(df_item, table_name, id_name)  

    def split_list_sql(self, df_new, table_name, selected_column, column_name , id_name):
        df_selected = df_new[selected_column]
        df_list = []
        for index, row in df_selected.items():
            row_list = row.split(',')
            for item in row_list:
                # print(index, position)
                df_list.append({'job_id': index, column_name: item})
        df = pd.DataFrame(df_list)
        self.insert_sql(df, table_name, id_name)

        
    def one_column_sql(self, df_new, column_name):
        table_name = column_name
        selected_columns = [column_name]
        rename = {}
        id_name = [column_name]
        self.update_dimension_sql(df_new, table_name, selected_columns, rename, id_name)
    
    def item_list_sql(self, df_new, item_name, list_name):
        table_name = item_name
        selected_column = list_name
        rename = {list_name: item_name}
        id_name = [item_name]
        self.explode_list_sql(df_new, table_name, selected_column, rename, id_name) 

        table_name = list_name
        selected_column = list_name
        column_name = item_name
        id_name = ["job_id", item_name]
        self.split_list_sql(df_new, table_name, selected_column, column_name , id_name)
                      
    def update_dimension_sql(self, df_new, table_name, selected_columns, rename, id_name):
         # 讀取目標表的資料,寫入dimention table
        # df_new[selected_columns] = df_new[selected_columns].str.strip()

        df_new = df_new[selected_columns].drop_duplicates().reset_index(drop=True)
        # 欄位重新命名
        df_new = df_new.rename(columns = rename)
        # 儲存至sql (排除重複的id)
        self.insert_sql(df_new, table_name, id_name)    

    # 需要修正 2025.05.04
    def insert_sql(self, selected_columns, table_name, id_name):
        # engine = self.connect()
        # existing_data = self.read_sql(table_name)
        # existing_data = existing_data[id_name]
        # # 檢查要寫入的資料是否已存在於目標表中 (依照id_name list來篩選)
        # df_merge = pd.merge(selected_columns, existing_data, on=id_name, how='left', indicator=True)
        # df_insert = df_merge[df_merge['_merge'] == 'left_only']
        # df_insert = df_insert.drop('_merge', axis=1)
    
        # df_insert_update = pd.merge(existing_data[id_name[0]], df_insert, on=id_name[0], how='inner')
        # if not df_insert_update.empty:
        #     with engine.connect() as connection:
        #         for index, row in df_insert_update.iterrows():
        #             for index, id in enumerate(id_name):
        #                 if index != 0:
        #                     # 更新除了id之外的內容
        #                     sql_query = text(f"UPDATE {table_name} SET {id} = :{id} WHERE {id_name[0]} = :{id_name[0]}")
        #                     connection.execute(sql_query, {id: row[id], id_name[0]: row[id_name[0]]})
        #         connection.commit()
        #         print(f"更新表格:{table_name},寫入{len(df_insert_update)}筆")
    
        # # 剩下的剩下id沒有重複的內容就 append
        # df_insert_append = pd.concat([df_insert, df_insert_update]).drop_duplicates(keep=False)
        # if not df_insert_append.empty:
        #     df_insert_append.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        #     print(f"新增表格:{table_name},寫入{len(df_insert_append)}筆")
        # else:
        #     print(f"無須新增表格:{table_name}")
        
        
         # 讀取目標表的資料
        existing_data = self.read_sql(table_name)
        existing_data = existing_data[id_name]

        # 檢查要寫入的資料是否已存在於目標表中
        df_merge = pd.merge(selected_columns, existing_data, on=id_name, how="left", indicator=True)
        df_insert = df_merge[df_merge['_merge'] == 'left_only']
        df_insert = df_insert.drop('_merge', axis=1)

        # 如果有不重複的值，將其寫入目標表
        if not df_insert.empty:
            df_insert.to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
            print(f"更新表格:{table_name},寫入{len(df_insert)}筆")
        else:
            print(f"無須更新:{table_name}")
            
    def read_sql(self, table_name):
        existing_data = pd.read_sql(f'SELECT * FROM {table_name}', con=self.engine)
        return existing_data
        
    # create db
    def createDB(self, db_name):
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
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

    # Delete database
    def deleteDB(self, db_name):
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
        )
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print(f"DB ({db_name}) has been deleted")
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

