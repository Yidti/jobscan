import pandas as pd
import numpy as np
import time
import re, time, json, requests, random
from tqdm import tqdm
from datetime import datetime
# 爬蟲
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import threaded_async_job
from datetime import datetime
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
    
    def __init__(self, filter_params, page = 15):
        self.filter_params = filter_params
        self.page = page
        self.df_company = pd.DataFrame()
        self.df_industry = pd.DataFrame()
        self.df_jobs = pd.DataFrame()
        
    def fetch_url(self):
        url = requests.get(self.url, self.filter_params, headers=self.headers).url
        print(f"url: {url}")
        return url

    def configure_driver(self):
        option = Options()
        option.add_argument(f"user-agent={self.headers['User-Agent']}")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_argument('--headless')
        # option.add_argument("--disable-gpu")
        return webdriver.Chrome(options=option)

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
                driver = self.configure_driver()
                driver.get(url)

                element = driver.find_element(By.XPATH, '//*[@id="js-job-header"]/div[1]/label[1]/select/option[1]')
                total_page = int(re.sub(r'\D', '', element.text.split('/')[-1]))
                # 讀取所有頁面
                self.load_pages(driver, total_page, scroll_times=15)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # 讀取所有 job item
                raw_jobs = soup.find_all("article", class_="js-job-item")
                result_items = self.get_job_items(raw_jobs)
                company_items,industry_items,job_items = result_items
                print(f'載入{len(job_items)}筆資料', end=" | ")
                driver.quit()
                return result_items
            except Exception as e:
                retry_count += 1
                print(f'執行錯誤, retry {retry_count}, {e}')

        print('達到重試上限，放棄爬取')
        return None

    def get_job_items(self, raw_jobs):
        company_items = {}
        industry_items = {}
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
            # 收集 item
             # 檢查並加入 company_items
            if company_no not in company_items:
                company_items[company_no] = {
                    # "id": company_no,
                    "公司": company_name,
                    "link": company_link,
                }
            else:
                # print(f"{company_name}({company_no}) repeated ")
                pass
            
            # 檢查並加入 industry_items
            if industry_no not in industry_items:
                industry_items[industry_no] = {
                    # "id": industry_no,
                    "產業": industry_name
                }
            else:
                # print(f"{industry_name}({industry_no}) repeated ")
                pass
            
            # 檢查並加入 job_items
            if job_no not in job_items:
                job_items[job_no] = {
                    # "id": job_no,
                    "職缺": job_name,
                    "公司": company_no,
                    "link": job_link,
                    # "地區": job_area,
                    "縣市": job_city,
                    "區域": job_region,
                    "地址": job_address,
                    "產業": industry_no,
                    "經歷": job_exp,
                    "學歷": job_edu,
                }
            else:
                # print(f"{job_name}({job_no}) repeated ")
                pass

        return company_items,industry_items,job_items

    
    def filter_job(self, job_items:tuple, job_keywords:tuple=()):
        filtered_job = job_items.copy()
        keyword_pattern = '|'.join(map(re.escape, job_keywords))

        # 使用临时列表存储要删除的键
        job_keys_to_delete = []
        
        for key, content in filtered_job.items():
            # print(key, content['職缺'])
            if not re.search(keyword_pattern, content['職缺'].lower()):
                job_keys_to_delete.append(key)
        
        # 在循环之外删除不符合条件的键
        for key in job_keys_to_delete:
            del filtered_job[key]
        print(f'過濾剩{len(filtered_job)}筆資料', end=" | ")

        return filtered_job

    def run(self, job_keywords:tuple=()):
        start_time = time.time()
        result_items = self.search_job()
        # result 包含 company, industry, job (dictionary)
        company_items, industry_items, job_items = result_items
        filtered_jobs = self.filter_job(job_items, job_keywords)
        
        print(f"花費 {np.round((time.time() - start_time),2)} 秒")

        # transfer to df and save in object
        self.df_company = pd.DataFrame.from_dict(company_items, orient='index')
        self.df_industry = pd.DataFrame.from_dict(industry_items, orient='index')
        self.df_jobs = pd.DataFrame.from_dict(job_items, orient='index')

        return filtered_jobs
    
    def detail(self, filtered_jobs: dict):
        start_time = time.time()
        jobs_details = threaded_async_job.scraper(filtered_jobs)
        print(f"花費 {np.round((time.time() - start_time),2)} 秒")
        # 更新 df_jobs
        self.df_jobs = pd.DataFrame.from_dict(jobs_details, orient='index')
        # 重新排序column
        columns=["更新", "職缺","公司", "link",'縣市', "區域", "地址", "產業", "經歷", "學歷",
        "內容", "類別", "科系", "語文", "工具", "技能", "其他",
         "待遇", "性質", "管理", "出差", "時段", "休假", "可上", "人數", "福利" ]
        self.df_jobs = self.df_jobs[columns]
        return jobs_details

    def export(self, user:str):

        df_jobs_output = self.df_jobs.copy()
        # 匯入company link的資料 
        df_jobs_output = pd.merge(df_jobs_output, self.df_company[['link']], left_on='公司', right_index=True, how='left', suffixes=('_jobs', '_company'))


        # 將id取代成name
        df_jobs_output['公司'] = df_jobs_output['公司'].replace(self.df_company['公司'].to_dict())
        df_jobs_output['產業'] = df_jobs_output['產業'].replace(self.df_industry['產業'].to_dict())
        
        current_date = datetime.now().date()    
        user = user
        counter = 1
        
        output_filename = f'output/{user}_{current_date}.xlsx'
        base_filename = f"{user}_{current_date}"
        
        df_jobs_output.replace(r'=\w+', '', regex=True, inplace=True)
        
        while os.path.exists(output_filename):
            output_filename = f'output/{user}_{current_date}_{counter}.xlsx'
            base_filename = f"{user}_{current_date}_{counter}"
            counter += 1
        
        try:
            df_jobs_output.to_excel(output_filename, sheet_name=base_filename, index=False, engine='xlsxwriter')
            print(f"CSV文件保存成功: {output_filename}")
        except PermissionError as e:
            print(f"无法保存文件: {e}")
            