import asyncio
from tqdm import tqdm
import time
import numpy as np
import time
import json
import html
from bs4 import BeautifulSoup

# test jobs
# filter_jobs = [f'job-{i}' for i in range(0, 338)]


# async def get_job_info(item):
#     # This function should be implemented to get job info
#     # Replace this with your actual implementation
#     await asyncio.sleep(1)
#     # return f"Info for {item}"

# async def scrape(i, jobs_batch):
#     tasks = []
#     semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

#     for item in jobs_batch:
#         async with semaphore:
#             task = asyncio.ensure_future(get_job_info(item))
#             tasks.append(task)

#     return await asyncio.gather(*tasks)

# async def main():
#     # raw_Job_list[20]
#     print(len(filter_jobs))
#     # 每個 batch 的 size (非同步每個 batch 處理)
#     batch_size = 30
#     # 確認 batches 數量
#     num_batches = (len(filter_jobs) + batch_size - 1) // batch_size
#     results = []
    
#     for batch_idx in range(num_batches):
#         start_idx = batch_idx * batch_size
#         end_idx = min((batch_idx + 1) * batch_size, len(filter_jobs))
#         # 每個 batch 頭尾 (0->29; 30->59; ......)
#         jobs_batch = filter_jobs[start_idx:end_idx]
        
#         # 使用 asyncio.to_thread 将 tqdm 包装在一个线程中
#         with tqdm(total=len(jobs_batch), desc=f"Batch {batch_idx+1} - ({start_idx+1}-{end_idx})", unit="task") as pbar:
#             async def scrape_with_progress(i):
#                 result = await scrape(i, jobs_batch)
#                 pbar.update(1)
#                 return result

#             # results = await asyncio.gather(*(scrape_with_progress(i) for i in jobs_batch))
#             batch_results = await asyncio.gather(*(scrape_with_progress(i) for i in range(len(jobs_batch))))
#             results.extend(batch_results)
#         # 使用 asyncio.gather 同時處理多個非同步任務，並等待它們全部完成
#         # results = await asyncio.gather(*(scrape(i) for i in jobs_batch))
    
    
#     return results

# if __name__ == "__main__":
#     asyncio.run(main())


# -----------------------------------

import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
option = Options()
# option.page_load_strategy = 'none'
option.add_argument(f"user-agent={headers['User-Agent']}")
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_argument('--headless') # 瀏覽器不提供頁面觀看，linux下如果系統是純文字介面不加這條會啓動失敗

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



async def scrape_with_selenium(link, driver):
    start_time = time.time()

    try:
        driver.get(link)
        
        # 在這裡使用Selenium進行網頁操作，如點擊、填表單等

        # 這裡是一個等待範例，等待某個元素出現
        # element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, 'example'))
        # )
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
        
        # 在這裡可以繼續進行其他Selenium操作

        # 直接獲取當前頁面的HTML
        page_source = driver.page_source
        print(f"花費 {np.round((time.time() - start_time),2)} 秒")
        soup = BeautifulSoup(page_source, 'html.parser')            
        text_content = get_title(soup)
        # print(text_content)
        time.sleep(1)

        return link, page_source
    except Exception as e:
        print(f"Error processing link {link}: {e}")
        return link, None

async def main(jobs_list):

    # 在異步任務之外初始化 WebDriver 實例
    driver = webdriver.Chrome(options=option)

    try:
        tasks = [scrape_with_selenium(link, driver) for link in jobs_list]
        results = await asyncio.gather(*tasks)

        # 在這裡處理 results，比如解析網頁內容等
        # for link, page_source in results:
        #     if page_source is not None:
        #         print(f"Link: {link}, Response: {page_source[:100]}...")
    finally:
        # 確保最後退出 WebDriver
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
