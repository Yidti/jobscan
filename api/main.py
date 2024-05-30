from fastapi import FastAPI, Query
from sqlalchemy import create_engine, engine
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import date

remote = True
diff_container = True

db_name = "job_db"
user = 'root'
password = 'test'

if not remote:
    host = 'localhost'
    port = 3306  # 預設值
else:
    if not diff_container:
        host = 'localhost'
        port = 3308
    else:
        host = 'mysqldb'
        port = 3306 # container 內部連線

mysql_url = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}'

def get_mysql_conn() -> engine.base.Connection:
    # 晚點再設置環境變數
    # load_dotenv()
    print(mysql_url)

    engine = create_engine(mysql_url)
    connect = engine.connect()
    return connect


app = FastAPI()

@app.get("/")
def read_root():
    return {"jobscan": "Find job!!! (╯°□°）╯︵ ┻━┻"}


@app.get("/tables/{table_name}", summary="Get table data", description="Retrieve data from a specified table, with an optional limit on the number of rows.")
def get_one_table_from_sql(table_name: str,  limit:int = Query(None)):
    query = f"SELECT * FROM {table_name}" if limit is None else f"SELECt * FROM {table_name} LIMIT {limit}"
    connection = get_mysql_conn()
    df = pd.read_sql(query, con=connection)
    data_dict = df.to_dict("records")
    return {f"{table_name}":data_dict}

# 只顯示 position, position_link, company, company_link
@app.get("/job-list-by-date")
def get_job_list_by_date(date: date = Query(..., description="日期，格式為 YYYY-MM-DD")):
    mysql_conn = get_mysql_conn()
    query = f'''
        SELECT 
            job.update_date, 
            job.position, 
            job.position_link, 
            co.company_name 
        FROM 
            job_info job 
        JOIN 
            company co
        ON 
            job.company_id = co.company_id 
        WHERE 
            job.update_date >= '{date}' 
        AND 
            job.company_id IN (
                SELECT 
                    MAX(company_id) 
                FROM 
                    company
                GROUP BY 
                    company_name
            )
        ORDER BY 
            job.update_date DESC
    '''
    connection = get_mysql_conn()
    df = pd.read_sql(query, con=connection)
    data_dict = df.to_dict("records")

    return {f"job_list >= ({date})": data_dict}