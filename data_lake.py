import pandas as pd
import os
from datetime import datetime
import pymongo
# from pandas import DataFrame

class DataLake():

    def __init__(self):
        self.noSQL_DB_name = "job_db"
        self.collection_name = "jobs_104"

    def upload_to_nosql(self, user):
        df = self.load_excel(user)
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client[self.noSQL_DB_name]
        collection = db[self.collection_name]
        current_date = datetime.now().date()
        df['data stamp'] = current_date.strftime('%Y-%m-%d')
        data = df.reset_index().to_dict(orient="records")

        new_count, update_count = 0, 0
        for idx, record in enumerate(data):
            try:
                filter_query = {"id": record["id"]}
                existing_record = collection.find_one(filter_query)
                # 已存在就更新, 不存在就插入
                if existing_record is None:
                    new_count += 1
                    collection.insert_one(record)
                else:
                    update_count += 1
                    collection.replace_one(filter_query, record)
            except Exception as e:
                print(f"{idx},{e}")
                
        print(f'更新{update_count}筆, 新增{new_count}筆')

    
    def load_excel(self, user):
        # Load excel
        current_date = datetime.now().date()
        # user = "yidti"
        file_name = f'output/{user}_{current_date}.xlsx'
        df = pd.DataFrame()
        if os.path.isfile(file_name):
            df = pd.read_excel(file_name, index_col="id")
            print(f"df length: {len(df)}")
        else:
            print("File not found. Please run the crawler function.")
        
        if df is not None:
            # 每columns裏頭包含null的row數目相加 再全部加總
            print(f"Cell num including null: {df.isnull().sum().sum()}")
            # 任何包含null的row數目加總
            df_include_null = df[df.isnull().any(axis=1)]
            print(f"Row num including null: {len(df_include_null)}")
        
        return df
        
        