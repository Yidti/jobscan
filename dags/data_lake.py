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
        self.df_jobs_details = pd.DataFrame()
        self.crawler = None

    def inital(self, crawler:Crawler104):
        # 先讀取 parquet detail暫存檔 (沒有暫存檔就會回傳none)
        df_temp = crawler.load_parquet(detail=True)
        if df_temp is not None:
            self.df_jobs_details = df_temp
        else:
            print("Please execute crawler's detail method before datalake's run method!")

        # 假如在在docker內部的話,有特別的host name
        if crawler.diff_container:
            self.mongo_url = "mongodb://root:example@host.docker.internal:27018/"
        else:
            self.mongo_url = "mongodb://root:example@localhost:27018/"
            
    def save_nosql(self):
        
        if self.df_jobs_details is not None:
            # current_date = datetime.now().date()
            # crawler.df_jobs_details['data_stamp'] = current_date.strftime('%Y-%m-%d')
            df_jobs = self.df_jobs_details.copy()
            self.upload_collection(df_jobs)
    
    def upload_collection(self, df):
        try: 
            client = pymongo.MongoClient(self.mongo_url)
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
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
    

    def load_all(self):
        try: 
            client = pymongo.MongoClient(self.mongo_url)
            db = client[self.noSQL_DB_name]
            collection = db[self.collection_name]
            
            data_list = list(collection.find({}, {"_id": 0}))  # 返回整個集合的所有文檔，排除 _id 欄位
            
            if data_list:
                df_jobs = pd.DataFrame(data_list)
                df_jobs.set_index("id", inplace=True)  # 在這裡使用 set_index 方法將 id 設置為索引
            else:
                print("No data found in the collection.")
                df_jobs = pd.DataFrame()  # 返回一個空的 DataFrame
        
            return df_jobs
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")


    def load_latest(self):
        try: 
            client = pymongo.MongoClient(self.mongo_url)
            db = client[self.noSQL_DB_name]
            collection = db[self.collection_name]
            
            stamp = collection.find_one(
                filter= {}, # 返回集合中的所有文檔
                sort=[("data stamp", -1)], # 按照字段進行降序排序。 -1 表示降序排列，1 表示升序排列
                projection={"_id": 0, "data stamp": 1}) # 指定了返回的文檔中的欄位, 0 表示排除, 1代表返回
            latest_stamp = stamp['data stamp']
            data_list = list(collection.find({"data stamp": {"$eq": latest_stamp}})) #  $eq（equal to）操作符
            if data_list:
                df_jobs = pd.DataFrame(data_list)
                df_jobs.set_index("id", inplace=True)  # 在這裡使用 set_index 方法將 id 設置為索引
                df_jobs = df_jobs.drop(["_id", "data stamp"], axis = 1)
            
            return df_jobs
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")


    def filter(self, job_keywords=(), company_exclude=()):

        try:
            client = pymongo.MongoClient(self.mongo_url)
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
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
    
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
        
        