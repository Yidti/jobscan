# dags/data_pipeline_jobs104.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from config.search_params import get_filter_params
from crawler104 import Crawler104
from data_lake import DataLake
from data_warehouse import DataWarehouse
import pendulum

local_tz = pendulum.timezone("Asia/Taipei")

# 設定連線方式
remote=True
diff_container=True

# crawler filter
def get_crawler104():
    global remote, diff_container
    # 設定爬蟲完之前的篩選條件 (for website)
    # custom filter params for search - for yidti
    role = {'ro':'全職'}
    keyword = {'keyword':"後端工程師 python"}
    # area = {'area':['新北市', '台北市', '桃園市', '台中市']}
    isnew = {'isnew':'三日內'}
    jobexp = {'jobexp':['1年以下', '1-3年']}
    # 預設
    mode = {'mode':'列表'}  # 一次能呈現比較多筆資料
    order = {'order':'日期排序'}
    asc = {'asc':'遞減'}
    # filter_params = get_filter_params(role, keyword, area, isnew, jobexp, mode, order, asc)
    filter_params = get_filter_params(role, keyword, isnew, jobexp, mode, order, asc)
    # user & title
    user = "yidti"
    title = "data_Engineer"
    # 執行jupyter的時候在本機,遠端Remote連到 Docker的Chrome執行
    crawler = Crawler104(filter_params, user, title, remote=remote, diff_container=diff_container)

    # 設定爬蟲完之後的篩選條件(for data)
    # keywords for filter job again
    job_keywords = ('工程','資料','python','data','數據','後端')
    # Exclude keywords to filter out companies related to gambling or others that I don't want to consider.
    company_exclude = ('新加坡商冕創有限公司','新博軟體開發股份有限公司','現觀科技股份有限公司'
                       ,'全富數位有限公司','杰思數位有限公司','博凡星國際有限公司',
                      '尊博科技股份有限公司','新騎資訊有限公司','新加坡商鈦坦科技股份有限公司台灣分公司',
                       '豪穎科技股份有限公司','塶樂微創有限公司','磐弈有限公司',
                       '聯訊網路有限公司','冶金數位科技有限公司','肥貓科技有限公司',
                       '無名科技有限公司','博澭科技有限公司','緯雲股份有限公司',
                       '風采有限公司','英屬維京群島商嘉碼科技有限公司台灣分公司',
                       '冠宇數位科技股份有限公司','英仕國際有限公司','元遊科技有限公司',
                       '禾碩資訊股份有限公司','向上集團_向上國際科技股份有限公司',
                       '弈樂科技股份有限公司','馬來西亞商極限電腦科技有限公司台灣分公司',
                       '樂夠科技有限公司','威智國際有限公司','紅信科技有限公司',
                       '深思設計有限公司','揚帆科技有限公司','晶要資訊有限公司',
                       '九七科技股份有限公司','臣悅科技有限公司','尊承科技股份有限公司',
                       '遊戲河流有限公司','唐傳有限公司','捷訊資訊有限公司',
                       '逍遙遊科技有限公司','澄果資訊服務有限公司','果遊科技有限公司',
                       '昱泉國際股份有限公司','博星數位股份有限公司',
                      )
    print(f"設定排除{len(company_exclude)}家公司")
    crawler.set_filter(job_keywords, company_exclude)
    
    return crawler

# step 1 - 2024/05/20
def data_crawler_list():
    crawler = get_crawler104()
    crawler.run()

# step 2 - 2024/05/21
def data_crawler_detail():
    crawler = get_crawler104()
    crawler.detail()

# step 2.5 - 2024/05/21
def data_export_excel():
    crawler = get_crawler104()
    crawler.export_excel()

# step 3 - 2024/05/21
def data_lake():
    crawler = get_crawler104()
    data_lake = DataLake(crawler)
    data_lake.save_nosql()
    data_lake.filter()

# step 4 - 2024/05/22
def data_warehouse():
    crawler = get_crawler104()
    data_lake = DataLake(crawler)
    
    data_Warehouse = DataWarehouse(data_lake)
    data_Warehouse.save_sql()

with DAG(
    dag_id = 'data_pipeline_jobs104',
    schedule_interval="0 12,19 * * *",  # 每天晚上19點執行一次
    start_date=datetime(2024, 5, 19, tzinfo=local_tz),
    catchup=False,
    default_args={
        'depends_on_past': False,
        # 'email': ['bonjour.luc@gmail.com'], #如果Task執行失敗的話，要寄信給哪些人的email
        # 'email_on_failure': True, #如果Task執行失敗的話，是否寄信
        # 'email_on_retry': False, #如果Task重試的話，是否寄信
        'retries': 1, #最多重試的次數
        'retry_delay': timedelta(minutes=2), #每次重試中間的間隔
    },
    
) as dag:

    # step 1 OK!
    task_crawler_list = PythonOperator(
    task_id='data_crawler_list',
    python_callable=data_crawler_list
    )

    # step 2 OK!
    task_crawler_detail = PythonOperator(
    task_id='data_crawler_detail',
    python_callable=data_crawler_detail
    )

    # step 2.5 OK! 
    task_export_excel = PythonOperator(
    task_id='data_export_excel',
    python_callable=data_export_excel
    )

    # step 3 OK!
    task_lake = PythonOperator(
    task_id='data_lake',
    python_callable=data_lake
    )

    task_warehouse = PythonOperator(
    task_id='data_warehouse',
    python_callable=data_warehouse
    )

    # task_analysis = PythonOperator(
    # task_id='data_analysis',
    # python_callable=data_analysis
    # )
   
    task_crawler_list >> task_crawler_detail >> task_lake >> task_warehouse
    task_crawler_detail >> task_export_excel
