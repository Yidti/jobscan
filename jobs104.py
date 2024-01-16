import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import time
import numpy as np
import json
import html

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
option = Options()
# option.page_load_strategy = 'none'
option.add_argument(f"user-agent={headers['User-Agent']}")
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_argument('--headless') # 瀏覽器不提供頁面觀看，linux下如果系統是純文字介面不加這條會啓動失敗
# option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
# option.add_argument('--disable-gpu') # 規避部分chrome gpu bug
# option.add_experimental_option("prefs", prefs)
option.add_argument('blink-settings=imagesEnabled=false') #不加載圖片提高效率





def extract_script_content(soup):
    """
    Extracts the content of the 'application/ld+json' script tag from a BeautifulSoup object.

    Parameters:
        - soup: BeautifulSoup object representing the HTML content.

    Returns:
        - The content of the script tag or None if not found.
    """
    if soup is None:
        print("No data available.")
        return None

    # 找到包含 JavaScript 代码的 script 标签
    script_tag = soup.find('script', type='application/ld+json')

    if script_tag is None:
        print("No script tag found.")
        return None

    # 返回 script 标签的内容
    return script_tag.text


def get_title(soup):
    # if soup is None:
    #     print("No data available.")
    #     return None

    # # 找到包含JavaScript代码的script标签
    # script_tag = soup.find('script', type='application/ld+json')

    # if script_tag is None:
    #     print("No script tag found.")
    #     return None

    json_string = extract_script_content(soup)

    # 将JSON字符串转换为Python的list
    data_list = json.loads(json_string)

    # 打印转换后的list
    company = data_list[0]['itemListElement'][1]['name']
    print(company, end=" | ")

    position = data_list[0]['itemListElement'][2]['name']
    print(position, end=" | ")

    update = data_list[2]['datePosted']
    print(update)

    description = data_list[2]['description']
    description = html.unescape(description)

    # 使用 BeautifulSoup 解析 HTML
    soup_descript = BeautifulSoup(description, 'html.parser')

    # 将 <br> 转换成换行符号
    for br_tag in soup_descript.find_all('br'):
        br_tag.replace_with('\n')

    # 提取纯文本内容
    text_content = soup_descript.get_text(separator='\n', strip=True)
    # print(text_content)
    
    return text_content


# async def scrape_with_selenium(link, driver):
#     start_time = time.time()
#     try:
#         driver.get(link)
#         # 在這裡使用Selenium進行網頁操作
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
#         # 直接獲取當前頁面的HTML
#         page_source = driver.page_source
#         print(f"花費 {np.round((time.time() - start_time),2)} 秒")
#         soup = BeautifulSoup(page_source, 'html.parser')            
#         text_content = get_title(soup)
#         # await asyncio.sleep(delay_seconds)
#         time.sleep(1)

#         return link, text_content
#     except Exception as e:
#         print(f"Error processing link {link}: {e}")
#         return link, None
        

async def get_info(jobs_list):
    jobs_list = [f"https:{item['href']}" for item in jobs_list]
    jobs_list = [url.split('?')[0] for url in jobs_list]

    tasks = []
    # 在異步任務之外初始化 WebDriver 實例
    driver = webdriver.Chrome(options=option)

    # 使用信号量控制并发
    semaphore = asyncio.Semaphore(10) 
    
    for link in jobs_list:
        async with semaphore:
            task = asyncio.create_task(fetch(link, driver))
            tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # 退出浏览器
    driver.quit()
    return results

 

async def fetch(link, driver):
  time.sleep(1.5)
  try:
    # 最多重试3次
    for retry in range(3):
      try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text_content = get_title(soup)

        return link, text_content

        # return parse_page(soup)
      except:
        print(f"Error loading {link}, retrying...")

    # return None
    return link, None


  except Exception as e:
    print(f"Error: {e}")
    # return None
    return link, None




    # try:
    #     tasks = [scrape_with_selenium(link, driver) for link in jobs_list]
    #     results = await asyncio.gather(*tasks)

    #     # 在這裡處理 results，比如解析網頁內容等
    #     # for link, text_content in results:
    #     #     if text_content is not None:
    #     #         print(f"Link: {link}, Response: {text_content[:100]}...")
    #     return results
    # finally:
    #     # 確保最後退出 WebDriver
    #     driver.quit()
    

# try:
    #     tasks = []
    #     for link in jobs_list:
    #         # 嘗試最多兩次
    #         for _ in range(2):
    #             result = await scrape_with_selenium(link, driver)
    #             if result[1] is not None:
    #                 tasks.append(result)
    #                 break  # 如果成功取得內容，則中斷嘗試
    #             else:
    #                 print(f"Retrying link {link}...")
    #         else:
    #             # 如果兩次都沒有成功，加入 None 作為結果
    #             tasks.append((link, None))

    #     results = await asyncio.gather(*tasks)

    #     return results
    # finally:
    #     driver.quit()




# async def get_info(item):
#     try:
#         title = item['title']
#         job_link = f"https:{item['href']}"
        
#         print(1, title)
#         print(2, job_link)
        
#         driver = webdriver.Chrome(options=option)
        
#         # 直接使用 await，因為 browser.get 和 browser.wait 本身就是異步的
#         driver.get(job_link)
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
        
#         # 获取加载后的页面内容
#         html_content = driver.page_source
#         # 关闭浏览器
#         driver.quit()
        
#         # print(html_content)
#         return html_content
#         # df = pd.DataFrame()
#         # # Data = {
#         # #     '更新日期': [self.update_date(soup)],
#         # #     '職缺名稱': [title],
#         # #     '公司名稱': [self.company(soup)],
#         # #     '連結': [Job_link]
#         # # }
#         # # Data.update(self.jd_info(soup))
#         # # Data.update(self.jr_info(soup))
#         # # df = pd.DataFrame(Data, columns=['更新日期', '職缺名稱', '公司名稱', '工作內容', '職務類別', '工作待遇',
#         # #                                 '工作性質', '上班地點', '管理責任', '出差外派', '上班時段', '休假制度',
#         # #                                 '可上班日', '需求人數', '工作經歷', '學歷要求', '科系要求', '語文條件',
#         # #                                 '擅長工具', '工作技能', '其他要求', '連結'])
#         # return df
#     except Exception as e:
#         print("發生錯誤", e)
#         return None
