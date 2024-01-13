from aiohttp import ClientSession, TCPConnector
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
option = Options()
# option.page_load_strategy = 'none'
option.add_argument(f"user-agent={headers['User-Agent']}")



# 非同步函式，用於發送 HTTP GET 請求
# async def fetch(session, url):    
#         # 使用 GoogleBot 作為 User-Agent 進行請求
#         async with session.get(url, headers = {'User-Agent':'GoogleBot'}) as response:
#             return await response.text()


async def get_info(item):
    try:
        title = item['title']
        job_link = f"https:{item['href']}"
        
        print(1, title)
        print(2, job_link)
        
        driver = webdriver.Chrome(options=option)
        
        # 直接使用 await，因為 browser.get 和 browser.wait 本身就是異步的
        driver.get(job_link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
        
        # 获取加载后的页面内容
        html_content = driver.page_source
        # 关闭浏览器
        driver.quit()
        
        # print(html_content)
        return html_content
        # df = pd.DataFrame()
        # # Data = {
        # #     '更新日期': [self.update_date(soup)],
        # #     '職缺名稱': [title],
        # #     '公司名稱': [self.company(soup)],
        # #     '連結': [Job_link]
        # # }
        # # Data.update(self.jd_info(soup))
        # # Data.update(self.jr_info(soup))
        # # df = pd.DataFrame(Data, columns=['更新日期', '職缺名稱', '公司名稱', '工作內容', '職務類別', '工作待遇',
        # #                                 '工作性質', '上班地點', '管理責任', '出差外派', '上班時段', '休假制度',
        # #                                 '可上班日', '需求人數', '工作經歷', '學歷要求', '科系要求', '語文條件',
        # #                                 '擅長工具', '工作技能', '其他要求', '連結'])
        # return df
    except Exception as e:
        print("發生錯誤", e)
        return None
