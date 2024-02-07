import pandas as pd
import os
from datetime import datetime
import pymongo
from crawler104 import Crawler104
# from pandas import DataFrame

class DataLake():

    def __init__(self):
        self.noSQL_DB_name = "job_db"
        self.collection_name = "jobs_104"
        self.df_jobs = pd.DataFrame()

    def export_nosql(self, user, crawler:Crawler104):
        # df = self.load_excel(user)

        current_date = datetime.now().date()
        crawler.df_jobs['data stamp'] = current_date.strftime('%Y-%m-%d')

        df_jobs = crawler.df_jobs.copy()
        # df_jobs.merge(crawler.df_company[['link']], left_on='公司', right_index=True, how='left', suffixes=('_job', '_company'))
        # df_jobs.merge(crawler.df_company[['公司']], left_on='公司', right_index=True, how='left', suffixes=('_id', '_name'))
        # df_jobs.merge(crawler.df_industry[['產業']], left_on='產業', right_index=True, how='left', suffixes=('_id', '_name'))
        
        self.upload_collection(df_jobs)
    
    def upload_collection(self, df):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client[self.noSQL_DB_name]
        collection = db[self.collection_name]
        
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
                
        print(f'Update {update_count} records, Insert {new_count} records in {self.collection_name} collection')

    def load(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client[self.noSQL_DB_name]
        collection = db[self.collection_name]
        


    def filter(self, job_keywords=(), company_exclude=()):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client[self.noSQL_DB_name]
        collection = db[self.collection_name]
        
        def run_job_keywords(collection, job_keywords):
            # 構建正則表達式
            regex_pattern = '|'.join(job_keywords)
            # 刪除不符合關鍵字的文件
            delete_query = {'職缺': {'$not': {'$regex': regex_pattern, '$options': 'i'}}}
            delete_result = collection.delete_many(delete_query)
            print("job keywords - 已刪除不符合關鍵字的文件數量:", delete_result.deleted_count)

        def run_company_exclude(collection, company_exclude):
            # 構建要刪除的文件的查詢條件
            delete_query = {'公司': {'$in': company_exclude}}
            # 刪除符合條件的文件
            delete_result = collection.delete_many(delete_query)
            print("company exclude - 已刪除符合條件的文件數量:", delete_result.deleted_count)
        
        run_job_keywords(collection, job_keywords)
        run_company_exclude(collection, company_exclude)
    
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
        
        