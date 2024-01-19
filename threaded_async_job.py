from tqdm import tqdm
import asyncio
import jobs104
import pandas as pd
from datetime import datetime
import os
import threading


async def scrape_batch(jobs_batch, progress_bar):
    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

    async with semaphore:
        task = asyncio.create_task(jobs104.get_info(jobs_batch))
        progress_bar.update(1)
        tasks.append(task)

    return await asyncio.gather(*tasks)

def process_batch(jobs, start_idx, end_idx, all_results,progress_bar):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    current_batch = jobs[start_idx:end_idx]
    results = loop.run_until_complete(scrape_batch(current_batch, progress_bar))
    all_results.extend(results)


def scraper(jobs):
    all_df = pd.DataFrame()
    current_date = datetime.now().date()    
    print(f"jobs:{len(jobs)}")
    
    # 每個 batch 的 size (非同步每個 batch 處理)
    batch_size = 50
    # 確認 batches 數量
    num_batches = (len(jobs) + batch_size - 1) // batch_size
    all_results = []

    with tqdm(total=num_batches, desc="Processing batches", unit="batch") as progress_bar:
        threads = []
    
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(jobs))
    
            # 启动一个新线程来处理当前 batch
            thread = threading.Thread(target=process_batch, args=(jobs, start_idx, end_idx, all_results, progress_bar))
            thread.start()
            threads.append(thread)
    
        # 等待所有线程完成
        for thread in threads:
            thread.join()

    for batch in all_results:
        for link, df in batch:
            if isinstance(df, pd.DataFrame):
                all_df = pd.concat([all_df, df], ignore_index=True)

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
    
    return all_df


