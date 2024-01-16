from tqdm import tqdm
import asyncio
import jobs104

async def scrape_batch(jobs_batch):
    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

    async with semaphore:
        task = asyncio.create_task(jobs104.get_info(jobs_batch))
        tasks.append(task)
        print("Batch Start")

    return await asyncio.gather(*tasks)

async def scraper(jobs):

    # jobs = filter_jobs
    
    print(f"jobs:{len(jobs)}")
    # 每個 batch 的 size (非同步每個 batch 處理)
    batch_size = 10
    # 確認 batches 數量
    num_batches = (len(jobs) + batch_size - 1) // batch_size
    all_results = []
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(jobs))
        # 每個 batch 頭尾 (0->29; 30->59; ......)
        jobs_batch = jobs[start_idx:end_idx]
        results = await scrape_batch(jobs_batch)
        all_results.extend(results)

    return all_results