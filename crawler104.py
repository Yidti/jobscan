import pandas as pd
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
    
# def get_jobs_link(filter_jobs:list):
#         jobs_link = [f"https:{item['href']}" for item in filter_jobs]
#         return jobs_link
    
class Crawler104():
    today = datetime.now().date()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
    url = 'https://www.104.com.tw/jobs/search/?'
    
    def __init__(self, filter_params, key_word, page = 15):
        self.filter_params = filter_params
        self.key_word = key_word
        self.page = page

    def fetch_url(self):
        url = requests.get(self.url, self.filter_params, headers=self.headers).url
        print(f"url: {url}")
        return url

    def configure_driver(self):
        option = Options()
        option.add_argument(f"user-agent={self.headers['User-Agent']}")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # option.add_argument('--headless')
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

                self.load_pages(driver, total_page, scroll_times=15)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                raw_jobs = soup.find_all("a", class_="js-job-link")
                print(f'載入{len(raw_jobs)}筆資料', end=" | ")

                driver.quit()
                return raw_jobs
            except Exception as e:
                retry_count += 1
                print(f'執行錯誤, retry {retry_count}')

        print('達到重試上限，放棄爬取')
        return []

    def filter_job(self, raw_jobs:list):
        # 在title裡頭依照關鍵字來做篩選
        filter_jobs = [i for i in raw_jobs if re.search(self.key_word, i['title'].lower())]
        print(f'過濾後剩{len(filter_jobs)}筆資料', end=" | ")
        return filter_job

    