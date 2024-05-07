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
import platform
import numpy as np

def set_font():
    """
    設定matplotlib的字體,根據作業系統自動選擇合適的字體
    """
    os_name = platform.system()
    
    if os_name == 'Windows':
        # 對於Windows系統
        mpl.rcParams['font.family'] = 'Microsoft JhengHei'
    elif os_name == 'Darwin':
        # 對於Mac OS系統
        mpl.rcParams['font.family'] = 'Arial Unicode MS'
    else:
        # 對於Linux或其他系統
        mpl.rcParams['font.family'] = 'DejaVu Sans'
        
# 使用該函數設定字體
set_font()


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

    def plot_count(self, df, column_name, ax=None, figsize=(10, 6), vertical=True, rotation=0):

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


        if vertical == True:
            ax = sns.countplot(data=df, x=column_name, order=order, palette=colors, ax=ax, hue=column_name, legend=False)
            for p in ax.patches:
                count = int(p.get_height())
                ax.annotate(f'{count}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
            ax.set_xlabel(column_name)
            ax.set_ylabel('Counts')
            ax.set_ylim(top=ax.get_ylim()[1] * 1.02)
            
            for tick in ax.get_xticklabels():
                tick.set_rotation(rotation)

        else:
            ax = sns.countplot(data=df, y=column_name, order=order, ax=ax, palette=colors, hue=column_name, legend=False)
            for p in ax.patches:
                w = int(p.get_width())
                ax.annotate(f'{w}', (w, p.get_y() + p.get_height() / 2.),
                            ha='left', va='center',fontsize=10, color='black', xytext=(5, 0),
                            textcoords='offset points')
            ax.set_xlabel('Counts')
            ax.set_ylabel(column_name)
            ax.set_xlim(right=ax.get_xlim()[1] * 1.02)
            
            for tick in ax.get_yticklabels():
                tick.set_rotation(rotation)
        
        x_limit_1 = ax.get_xlim()[0]
        x_limit_2 = ax.get_xlim()[1]
        diff = x_limit_2*0.02
        ax.set_xlim(left= x_limit_1 - diff)
        ax.set_xlim(right= x_limit_2 + diff)

        y_limit_1 = ax.get_ylim()[0]
        y_limit_2 = ax.get_ylim()[1]
        diff = y_limit_2*0.02
        ax.set_ylim(top= y_limit_2 + diff)
        ax.set_ylim(bottom= y_limit_1 - diff)

        plt.tight_layout()

    
    def plot_pie(self, df, column_name, ax=None, figsize=(10, 6), startangle=45, x_move=1.4, y_move=1.2, y_add=0.2):
        if df.empty:
            print("DataFrame 為空,無法繪製圖形。")
            return
    
        if column_name not in df.columns:
            print(f"列名 '{column_name}' 不存在於 DataFrame 中。")
            return
    
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
    
        value_counts = df[column_name].value_counts()
        labels = value_counts.index
        sizes = value_counts.values
        colors = sns.color_palette("husl", len(labels))
        total = sum(sizes)  # 計算總數
        results = []
        for label, size in zip(labels, sizes):
            percentage = (size / total) * 100  # 計算百分比
            result = f"{label} ({percentage:.2f}%)"
            results.append(result)

        wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.5), startangle=startangle)
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

        prev_ang = 0
        min_ang = 8  # 調整這個值以控制最小距離
        for i, p in enumerate(wedges):
            ang_origin = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang_origin))
            x = np.cos(np.deg2rad(ang_origin))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang_origin)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            
            # 檢查新的 annotate 位置是否太靠近之前的 annotate 位置
            too_close = False
            diff_ang = np.abs(prev_ang-ang_origin)
            # print("diff_ang",diff_ang)
            if diff_ang < min_ang:
                too_close = True
                
            if too_close:
            # 如果太靠近,調整新的 annotate 位置
                # print("Change")
                ang = prev_ang + 8
                yy = np.sin(np.deg2rad(ang))
                xx = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(xx))]
                connectionstyle = "angle,angleA=0,angleB={}".format(-ang)
                # 位移
                y_move += y_add
                xytext = (x_move*np.sign(x), y_move*y)
            else:
                xytext = (x_move*np.sign(x), y_move*y)
            
            prev_ang = ang_origin

            ax.annotate(results[i], xy=(x, y), xytext=xytext,
                        horizontalalignment=horizontalalignment, **kw)


        # for i, p in enumerate(wedges):
        #     ang_origin = (p.theta2 - p.theta1)/2. + p.theta1
        #     y = np.sin(np.deg2rad(ang_origin))
        #     x = np.cos(np.deg2rad(ang_origin))
        #     print("ang",ang_origin, x, y)
        #     horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        
        #     connectionstyle = f"angle,angleA=0,angleB={ang_origin}"
        #     kw["arrowprops"].update({"connectionstyle": connectionstyle})
        
        #     # 檢查新的 annotate 位置是否太靠近之前的 annotate 位置
        #     too_close = False
            
        #     # distance = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
        #     diff_ang = np.abs(prev_ang-ang_origin)
        #     print("diff_ang",diff_ang)
        #     if diff_ang < min_ang:
        #         too_close = True

            
        #     if too_close:
        #         # 如果太靠近,調整新的 annotate 位置
        #         print("Change")
        #         ang = prev_ang + 8
        #         prev_ang = ang

        #         # y = np.sin(np.deg2rad(ang))
        #         # x = np.cos(np.deg2rad(ang))
        #         horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        #         connectionstyle = f"angle,angleA=0,angleB={ang}"
        #         kw["arrowprops"].update({"connectionstyle": connectionstyle})
                
        #         text_x = 1.3*np.sign(x)
        #         text_y = 1.4*y
        #         # text_x, text_y = x * 1.3, y * 1.2

        #         print('Change',f'{results[i]}',ang)

        #     else:
        #         prev_ang = ang_origin
        #         # text_x, text_y = x * 1.3, y * 1.2

        #         text_x = 1.3*np.sign(x)
        #         text_y =1.2*y

            
            
        #     if i in range(0,8):
        #         # print(results[i], x, y, text_x, text_y)
        #         ann = ax.annotate(results[i], xy=(x, y), xytext=(text_x, text_y),
        #                           horizontalalignment=horizontalalignment, **kw)
        #         # 記錄新的 annotate 位置
        #         prev_x= ann.xy[0]
        #         prev_y= ann.xy[1]

            


        
        
        ax.axis('equal')  # 確保圓環圖是圓形的
        ax.set_title(f"{column_name}")
    
        # 移除邊框
        ax.set_frame_on(False)
        plt.tight_layout()

        

    