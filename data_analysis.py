# 測試!!!
from sqlalchemy import create_engine
import urllib.parse
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import sqlite3
import pymongo
from wordcloud import WordCloud
# 設定中文字型為微軟正黑體
mpl.rcParams['font.family'] = 'Microsoft JhengHei'



class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataAnalysis(metaclass=SingletonMeta):
    def __init__(self):
        self.engine = self.connect()   
        
    def connect(self):
            # 对密码进行 URL 编码
            password = urllib.parse.quote_plus('Sql@1031')
            # 创建 SQLAlchemy 引擎
            db_name = "job_db"
            # 创建 SQLAlchemy 引擎
            engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost:3306/{db_name}')
            return engine

    def load_sql_table(self, table_name):
        existing_data = pd.read_sql(f'SELECT * FROM {table_name}', con=self.engine)
        return existing_data
    
    
    def merge_data(self, t1_table, t2_table, t1_id, t2_id, t1_columns=[], t2_columns=[]):
        try:
            # 構建 SQL 查詢字串
            select_t1_columns = ', '.join([f't1.{col}' for col in t1_columns])
            select_t2_columns = ', '.join([f't2.{col}' for col in t2_columns])
            select_list = [select_t1_columns, select_t2_columns]
            select_list = [item.strip(', ') for item in select_list if item]  # 去除頭尾逗號並過濾空字串
            select_columns = ', '.join(select_list) if select_list else '*'
        
            # print(select_columns)
            query = f'''
            SELECT
                {select_columns}
            FROM
                {t1_table} AS t1
            JOIN
                {t2_table} AS t2
            ON t1.{t1_id} = t2.{t2_id}
            WHERE t1.{t1_id} IS NOT NULL AND t2.{t2_id} IS NOT NULL
            '''
    
            # 從資料庫讀取資料到 DataFrame
            df = pd.read_sql_query(query, self.engine)
        except Exception as e:
            print("Error", e)
            df = pd.DataFrame()  # 雖然不是必需,但保留這行也沒有問題
        return df

    def horizontal_countplot(self, df : pd.DataFrame, column_name : str, ax = None):
        # if df.empty:
        #     print("DataFrame 為空，無法繪製計數柱狀圖。")
        # return  # 如果 DataFrame 為空，直接返回，不繼續執行後續的程式碼
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        if ax is None:
            ax = plt.gca()
        
        order = df[column_name].value_counts().index
        # 新增：從 Seaborn 的 "husl" 調色板獲取顏色列表
        colors = sns.color_palette("husl", len(order)) 
        # 修改：將顏色列表傳遞給 palette 參數
        ax = sns.countplot(data=df, y=column_name, order=order, ax=ax, palette=colors, hue=column_name, legend=False)
        # ax = sns.countplot(data=df, y=column_name, order=order, ax=ax)
        for p in ax.patches:
            w = int(p.get_width())
            ax.annotate(f'{w}', (w, p.get_y() + p.get_height() / 2.),
                        ha='left', va='center',fontsize=10, color='black', xytext=(2, 0),
                        textcoords='offset points')
    
        max_count = df[column_name].value_counts().max()
        max_x = ((max_count + 100) // 100 + 1) * 100
        ax.set_xlim(0, max_x) 
        plt.xlabel('Counts')
        plt.ylabel('')
        plt.tight_layout()
        plt.show()

    def vertical_countplot(self, df, column_name, ax=None):
        if df.empty:
            print("DataFrame 為空，無法繪製計數柱狀圖。")
        return  # 如果 DataFrame 為空，直接返回，不繼續執行後續的程式碼
        

        # if ax is None:
        #     ax = plt.gca()  # 如果未提供 ax，則使用當前的 Axes
        # 新增：從 Seaborn 的 "husl" 調色板獲取顏色列表
        colors = sns.color_palette("husl", len(df[column_name].value_counts()))  
        # 修改：將顏色列表傳遞給 palette 參數
        sns.countplot(data=df, x=column_name, ax=ax, palette=colors, hue=column_name, legend=False)
    
        # sns.countplot(data=df, x=column_name, ax=ax)
        for p in ax.patches:
            h = int(p.get_height())
            ax.annotate(f'{h}', (p.get_x() + p.get_width() / 2., h),
                        ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                        textcoords='offset points')
        ax.set_ylabel('Counts')
        plt.tight_layout()
        plt.show()


    def plot_countplot(self, df, column_name, ax=None, figsize=(10, 6)):

        if df.empty:
            print("DataFrame 为空,无法绘制计数柱状图。")
            return
    
        if column_name not in df.columns:
            print(f"列名 '{column_name}' 不存在于 DataFrame 中。")
            return
    
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)  # 创建一个新的图形和坐标轴对象
    
        total_count = df[column_name].count()
        value_counts = df[column_name].value_counts()
        order = value_counts.index
        colors = sns.color_palette("husl", len(order))
    
        ax = sns.countplot(data=df, x=column_name, order=order, palette=colors, ax=ax, hue=column_name, legend=False)
    
        for p in ax.patches:
            count = int(p.get_height())
            ax.annotate(f'{count}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')
    
        ax.set_xlabel(column_name)
        ax.set_ylabel('Counts')
        # 调整坐标轴限制以确保数字不超出外框
        ax.set_ylim(top=ax.get_ylim()[1] * 1.05)

        x_limit_1 = ax.get_xlim()[0]
        x_limit_2 = ax.get_xlim()[1]
        diff = x_limit_2*0.04
        ax.set_xlim(left= x_limit_1 - diff)
        ax.set_xlim(right= x_limit_2 + diff)
        plt.xticks(rotation=45)
        plt.tight_layout()



