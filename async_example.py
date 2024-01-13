import asyncio
from tqdm import tqdm

# test jobs
filter_jobs = [f'job-{i}' for i in range(0, 338)]


async def get_job_info(item):
    # This function should be implemented to get job info
    # Replace this with your actual implementation
    await asyncio.sleep(1)
    # return f"Info for {item}"

async def scrape(i, jobs_batch):
    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

    for item in jobs_batch:
        async with semaphore:
            task = asyncio.ensure_future(get_job_info(item))
            tasks.append(task)

    return await asyncio.gather(*tasks)

async def main():
    # raw_Job_list[20]
    print(len(filter_jobs))
    # 每個 batch 的 size (非同步每個 batch 處理)
    batch_size = 30
    # 確認 batches 數量
    num_batches = (len(filter_jobs) + batch_size - 1) // batch_size
    results = []
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(filter_jobs))
        # 每個 batch 頭尾 (0->29; 30->59; ......)
        jobs_batch = filter_jobs[start_idx:end_idx]
        
        # 使用 asyncio.to_thread 将 tqdm 包装在一个线程中
        with tqdm(total=len(jobs_batch), desc=f"Batch {batch_idx+1} - ({start_idx+1}-{end_idx})", unit="task") as pbar:
            async def scrape_with_progress(i):
                result = await scrape(i, jobs_batch)
                pbar.update(1)
                return result

            # results = await asyncio.gather(*(scrape_with_progress(i) for i in jobs_batch))
            batch_results = await asyncio.gather(*(scrape_with_progress(i) for i in range(len(jobs_batch))))
            results.extend(batch_results)
        # 使用 asyncio.gather 同時處理多個非同步任務，並等待它們全部完成
        # results = await asyncio.gather(*(scrape(i) for i in jobs_batch))
    
    
    return results

if __name__ == "__main__":
    asyncio.run(main())