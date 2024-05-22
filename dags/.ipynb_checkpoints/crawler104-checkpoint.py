import pandas as pd
import numpy as np
import time
import re, time, json, requests, random
from tqdm import tqdm
from datetime import datetime, timedelta
# 爬蟲
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from crawler import Crawler

import threaded_async_job
import os
import xlsxwriter
# import grequests # 看起要在.py才能用

# 非同步HTTP請求
from aiohttp import ClientSession, TCPConnector
# Python標準庫中提供的用於支援異步編程的模組, 可使用async和await關鍵字來定義異步協程
import asyncio
# 處理嵌套事件迴圈（nested event loop）的庫, 在Python中，通常只能有一個事件迴圈運行，
# 但某些情況下，比如在Jupyter Notebook中執行異步代碼時，可能會遇到嵌套事件迴圈的問題。
# nest_asyncio的作用就是解決這個問題，允許在已有事件迴圈的情況下再創建一個新的事件迴圈。

# import nest_asyncio
# 它會修改當前執行環境，允許在已有事件迴圈的情況下再次建立一個新的事件迴圈，
# 通常用於處理一些特定的情況，例如在Jupyter Notebook中執行異步代碼。
# nest_asyncio.apply()

def get_values(selected, mapping):
    codes = [mapping[item] for item in selected]
    values = ','.join(map(str, codes))
    return values
    


class Crawler104():
    today = datetime.now().date()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
    url = 'https://www.104.com.tw/jobs/search/?'
    
    def __init__(self, filter_params, user="",title="" , page = 15, remote=True, diff_container=True):
        self.filter_params = filter_params
        self.user = user
        self.title = title
        self.page = page
        
        self.df_jobs = pd.DataFrame()
        self.df_jobs_temp = pd.DataFrame()
        self.df_jobs_today = pd.DataFrame()
        self.df_jobs_details = pd.DataFrame()

        # 請依照連線狀況設定, 遠端chrome時, 有不同容器或相同容器狀況
        self.remote = remote
        # 執行Airflow的時候要更改成Ture
        self.diff_container = diff_container
        # 初步爬蟲使用
        self.crawler = Crawler(remote=self.remote, diff_container=self.diff_container)
        # 目前遠端有一個大問題, detail爬蟲的時候會當機 (修復完畢)
        if self.diff_container:
            self.temp_path = "/opt/airflow/dags/temp/"
            self.output_path = "/opt/airflow/dags/output/"
        else:
            self.temp_path = "temp/"
            self.output_path = "output/"
        
        # 爬完蟲之後的篩選條件
        self.job_keywords = None
        self.company_exclude = None

    def set_filter(self, job_keywords, company_exclude):
        self.job_keywords = job_keywords
        self.company_exclude = company_exclude

    def fetch_url(self):
        url = requests.get(self.url, self.filter_params, headers=self.headers).url
        print(f"url: {url}")
        return url
    
    def check_driver(self):
        try:
            # 嘗試初始化 driver
            with self.crawler.configure_driver() as driver:
                # driver = 
                # driver = self.configure_driver(use_remote= self.remote)
                # driver.quit()
                print("Chrome driver is available.")
            return True
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            # 重新拋出異常，以便 Airflow 檢測到任務失敗
            raise
            # return False
    
    def load_pages(self, driver, total_page, scroll_times):
        current_page = 0

        with tqdm(total=scroll_times + total_page - scroll_times, position=0, desc="Loading", unit="page") as pbar:
            # 滾動前15頁
            for _ in range(scroll_times):
                driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                current_page += 1
                time.sleep(2)
                pbar.update(1)  # 更新進度條
            
            # 自動加載結束後要自行點選載入(15以後)  
            while current_page < total_page:
                try:
                    button_element = WebDriverWait(driver, 4).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#js-job-content > div:last-child > button'))
                    )
                    page_number = int(re.search(r'\d+', button_element.text).group()) if re.search(r'\d+', button_element.text) else None
                    button_element.click()
                    current_page += 1
                    pbar.update(1)  # 更新進度條

                    if (total_page == page_number) or (page_number is None):
                        print(f"載入{current_page}頁", end=" | ")
                        break
                except Exception as e:
                    print("發生未知錯誤：", e)
                    break
    
    def search_job(self):   
        retry_count = 0
        while retry_count < 3:
            try:
                # 嘗試執行原本的搜尋邏輯
                url = self.fetch_url()

                # driver = 

                with self.crawler.configure_driver() as driver: 
                    # driver = self.configure_driver(use_remote= self.remote)
                    driver.get(url)
    
                    element = driver.find_element(By.XPATH, '//*[@id="js-job-header"]/div[1]/label[1]/select/option[1]')
                    total_page = int(re.sub(r'\D', '', element.text.split('/')[-1]))
                    # 讀取所有頁面
                    # test mode
                    # total_page=15
                    self.load_pages(driver, total_page, scroll_times=15)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # 讀取所有 job item
                    raw_jobs = soup.find_all("article", class_="js-job-item")
                    job_items = self.get_job_items(raw_jobs)
                    # company_items,industry_items,job_items = result_items
                    print(f'載入{len(job_items)}筆資料', end=" | ")
                    # driver.quit()
    
                    # result 包含 company, industry, job (dictionary)
                    # company_items, industry_items, job_items = result_items 
                    # transfer to df and save in object
                    # self.df_company = pd.DataFrame.from_dict(company_items, orient='index')
                    # self.df_industry = pd.DataFrame.from_dict(industry_items, orient='index')
                    self.df_jobs = pd.DataFrame.from_dict(job_items, orient='index')
            
                    # self.df_company.index.name = 'id'
                    # self.df_industry.index.name = 'id'
                    self.df_jobs.index.name = 'id'
                    return True
                    
            except Exception as e:
                retry_count += 1
                print(f'執行錯誤, retry {retry_count}, {e}')

        print('達到重試上限，放棄爬取')
        return False

    def get_job_items(self, raw_jobs):
        # company_items = {}
        # industry_items = {}
        job_items = {}
        
        for article in raw_jobs:
        
            # article
            # 公司 company
            company_no = int(article.get("data-cust-no"))
            company_name = article.get("data-cust-name")
            company_link = article.find('li', class_='job-mode__company').find('a')['href']
            company_link= f"https:{company_link.split('?')[0]}"
            company_title_element = article.find('li', class_='job-mode__company').find('a')
            company_title = company_title_element.get('title')
            # 移除空白字符和換行
            company_title = company_title.replace('\n', '').strip()
            pattern = r'.*公司(?:住址|地址)：(.+)'
            # 使用正則表達式搜尋"公司地址："之後的所有內容
            match = re.search(pattern, company_title)

            if match:
                job_address = match.group(1).strip()
            else:
                job_address = None

            # 產業 industry
            industry_no = int(article.get("data-indcat"))
            industry_name = article.get("data-indcat-desc")
            # 工作 job
            job_no = int(article.get("data-job-no"))
            job_name = article.get("data-job-name")
            job_link_element = article.find("a", class_="js-job-link")
            job_link = job_link_element.get("href")
            job_link= f"https:{job_link.split('?')[0]}"
            job_exp = article.find('li', class_='job-mode__exp').text
            job_edu = article.find('li', class_='job-mode__edu').text
            # 地區area = 縣市county/city + 區域region 
            job_area = article.find('li', class_='job-mode__area').text
            pattern = r'(.+?[市縣])(.+?[區鎮])?'
            area_match = re.match(pattern ,job_area)
            if area_match: 
                job_city = area_match.group(1)
                job_region = area_match.group(2)
            else: 
                job_city = job_area
                job_region = None
            
            
            # 檢查並加入 job_items
            if job_no not in job_items:
                job_items[job_no] = {
                    "職缺": job_name,
                    "職缺_link": job_link,
                    "公司_id":company_no,
                    "公司": company_name,
                    "公司_link": company_link,
                    "產業_id": industry_no,
                    "產業": industry_name,
                    # "地區": job_area,
                    "縣市": job_city,
                    "區域": job_region,
                    "地址": job_address,
                    "經歷": job_exp,
                    "學歷": job_edu,
                }
            else:
                # print(f"{job_name}({job_no}) repeated ")
                pass
                
        return job_items
        # return company_items,industry_items,job_items

    
    def filter_job(self, job_items:pd.DataFrame, job_keywords=(), company_exclude=()):
        filtered_job = job_items.copy()
        job_keys_to_delete = []

        # keyword_pattern = '|'.join(map(re.escape, job_keywords))
        # 職缺篩選條件
        if job_keywords:
            for key, row in filtered_job.iterrows():
                if not any(keyword in row['職缺'] for keyword in job_keywords):
                    job_keys_to_delete.append(key)
                    
        # 公司排除條件
        if company_exclude:
            for key, row in filtered_job.iterrows():
                if any(company in row['公司'] for company in company_exclude):
                    job_keys_to_delete.append(key)
        # 去除重複的索引
        job_keys_to_delete = list(set(job_keys_to_delete))
        # 刪除符合條件的行
        filtered_job.drop(job_keys_to_delete, inplace=True)
        
        print(f'過濾剩{len(filtered_job)}筆資料', end=" | ")

        return filtered_job



    def get_path(self, detail=False, exclude=False):
        # 先讀取 parquet 暫存檔
        file_name = f"{self.user}_{self.title}"
        if detail:
            file_name = file_name + "_details"
        if exclude:
            file_name = file_name + "_exclude"   
        parquet_file = f"{file_name}.parquet" 
        parquet_path = f"{self.temp_path}/{parquet_file}"
        return parquet_path

        
    def load_parquet(self, detail=False, exclude=False):
        # 先讀取 parquet 暫存檔
        # file_name = f"{self.user}_{self.title}"
        # if detail:
        #     file_name = file_name + "_details"
        # parquet_file = f"{file_name}.parquet" 
        # parquet_path = f"temp/{parquet_file}"
        parquet_path = self.get_path(detail = detail, exclude = exclude)
        # print(parquet_path)
        if os.path.exists(parquet_path):
            existing_df = pd.read_parquet(parquet_path)
            return existing_df
        else:
            print("Crawler temp file not found.")
            return None

    
    def save_parquet(self, df_jobs, detail=False, exclude=False):
        file_name = f"{self.user}_{self.title}"
        if detail:
            file_name = file_name + "_details"
        if exclude:
            file_name = file_name + "_exclude"

        parquet_file = f"{file_name}.parquet" 
        # self.temp_path = "/opt/airflow/temp/" or "temp/"
        parquet_path = f"{self.temp_path}{parquet_file}"
        
        if os.path.exists(parquet_path):
            existing_df = pd.read_parquet(parquet_path)
            combined_df = pd.concat([existing_df, df_jobs], join='inner')
            # 將data_stamp轉換為datetime類型，以便進行排序
            combined_df['data_stamp'] = pd.to_datetime(combined_df['data_stamp'])
            # 按照id和data_stamp排序，保留最新的data_stamp
            combined_df = combined_df.sort_values(by=['id', 'data_stamp'], ascending=[True, False])
            # 刪除重複的id，只保留最新的那一條
            combined_df = combined_df.reset_index(drop=False)
            combined_df = combined_df.drop_duplicates(subset='id', keep='first')
            combined_df = combined_df.set_index('id')
        else:
            combined_df = df_jobs
    
        combined_df.to_parquet(parquet_path, index=True)

    # def run(self, job_keywords=(), company_exclude=()):
    def run(self):

        if not self.check_driver():
            print("Driver check failed. Exiting.")
            raise ValueError("Driver check failed.")

        if (self.job_keywords is not None) and (self.company_exclude is not None):
            print("Start Crawling")    
            start_time = time.time()
            self.search_job()
            self.df_jobs = self.filter_job(self.df_jobs, self.job_keywords, self.company_exclude)
            print(f"花費 {np.round((time.time() - start_time),2)} 秒")
            # 儲存在暫存檔案裡頭 (加入日期標記）
            current_date = datetime.now().date()
            self.df_jobs['data_stamp'] = current_date.strftime('%Y-%m-%d')
            self.save_parquet(self.df_jobs)
        else: 
            print("Setting Filtter")

    
    def detail(self):
        # 先讀取 parquet list暫存檔 (沒有暫存檔就會回傳none)
        df_temp = self.load_parquet(detail=False)
        # print('test',df_temp)
        if df_temp is not None:
            self.df_jobs_temp = df_temp
        else:
            print("Please execute run method before detail method!")

        # 假如爬蟲暫存檔list有存在的話
        if all([self.df_jobs_temp is not None, self.company_exclude is not None, self.job_keywords is not None]):

            start_time = time.time()

            # 定義計數器
            count = 0
            # 持續十次爬蟲
            while count <10:
                # 更新計數器
                count += 1

                # 讀取 parquet detail暫存檔 避免重複抓取 (讀取今日資料 排除已經爬過 & 關閉的職缺)
                current_date = datetime.now().date()
                today_date = datetime.now().strftime('%Y-%m-%d')
                self.df_jobs_today = self.df_jobs_temp[self.df_jobs_temp['data_stamp'] == today_date]
    
                # 讀取已存在的detail檔案
                df_exist = self.load_parquet(detail=True)
                df_close = self.load_parquet(exclude=True)
                
                # 抓取detail目標
                df_scrape = self.df_jobs_today.copy()            
                # df_scrape = df_scrape.head(10)
                if df_exist is not None:
                    # 計算一周前的日期
                    today = datetime.now()
                    one_week_ago = today - timedelta(days=7)
                    # 確保 data_stamp 是 datetime 格式
                    df_exist['data_stamp'] = pd.to_datetime(df_exist['data_stamp'])
                    # 過濾出 data_stamp 在一周內的記錄
                    recent_ids = df_exist[df_exist['data_stamp'] >= one_week_ago].index
                    # filter in df_exist based on id
                    df_scrape = df_scrape[~df_scrape.index.isin(df_exist.index)]
                    print(f'目標{len(self.df_jobs_today)}筆 | 排除一週內更新，過濾剩{len(df_scrape)}筆資料', end = " | ")
                    
                    
                if df_close is not None:
                    # 过滤掉存在于 df_close 中的 id
                    df_scrape = df_scrape[~df_scrape.index.isin(df_close.index)]
                print(f"排除無效連結或關閉職缺，過濾剩{len(df_scrape)}筆資料")    
    
                # remove crawler
                jobs_details = threaded_async_job.scraper(self, df_scrape)
                
                print(f"Scraping Details for {len(jobs_details)} Jobs", end = " | ")
                df_jobs_details = pd.DataFrame.from_dict(jobs_details, orient='index')
                df_jobs_details.index.name = 'id'
    
                if not df_jobs_details.empty:
                    self.df_jobs_details = df_jobs_details
                    # 儲存在暫存檔案裡頭 (加入日期標記）
                    current_date = datetime.now().date()
                    self.df_jobs_details['data_stamp'] = current_date.strftime('%Y-%m-%d')
                    # 重新排序column
                    columns=["更新", "職缺",'職缺_link',"公司_id", "公司", "公司_link","產業_id", "產業",
                             "縣市", "區域", "地址", "經歷", "學歷", "內容", "類別", "科系",
                             "語文", "工具", "技能", "其他", "待遇", 
                             "性質", "管理", "出差", "時段", "休假", "可上", "人數", "福利", "data_stamp" ]
                    self.df_jobs_details = self.df_jobs_details[columns]
                    # 儲存到 detail 暫存檔
                    self.save_parquet(self.df_jobs_details, detail=True)
                else:
                    print("無需更新")
                    break
                    
            print(f"花費 {np.round((time.time() - start_time),2)} 秒")
    
    def export_excel(self):

        # 先讀取 parquet detail暫存檔 (沒有暫存檔就會回傳none)
        df_temp = self.load_parquet(detail=True)
        if df_temp is not None:
            self.df_jobs_details = df_temp
        else:
            print("Please execute detail method before export_excel method!")

        if self.df_jobs_details is not None:
            df_jobs_output = self.df_jobs_details
    
            column_list = ["公司_id", "產業_id"]
            for column_to_drop in column_list:
                if column_to_drop in df_jobs_output.columns:
                    df_jobs_output = df_jobs_output.drop(column_to_drop,axis= 1)
            df_jobs_output.replace(r'=\w+', '', regex=True, inplace=True)

            # 修改日期格式
            df_jobs_output['data_stamp'] = pd.to_datetime(df_jobs_output['data_stamp'])
            df_jobs_output['data_stamp'] = df_jobs_output['data_stamp'].dt.date

            # 儲存 excel (每個月換一個檔案)
            current_date = datetime.now().date()
            year_month = current_date.strftime('%Y_%m')

            file_name = f"{self.user}_{self.title}_{year_month}"   
            xlsx_file = f"{file_name}" 
            xlsx_path = f'{self.output_path}/{xlsx_file}.xlsx'
            # 先删除现有文件（如果存在）
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
            # 然后保存新文件        
            try:
                df_jobs_output.to_excel(xlsx_path, sheet_name=xlsx_file, index=True, index_label='id', engine='xlsxwriter')
                print(f"Excel文件儲存成功: {xlsx_path}")
            except PermissionError as e:
                print(f"無法保存文件: {e}")


        # output_filename = f'output_{current_date}.csv'
        # counter = 1
        
        # while os.path.exists(output_filename):
        #     output_filename = f'output_{current_date}_{counter}.csv'
        #     counter += 1
        
        # try:
        #     all_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        #     print(f"CSV文件保存成功: {output_filename}")
        # except PermissionError as e:
        #     print(f"无法保存文件: {e}")
            