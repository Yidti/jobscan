# JOBSCAN

## Docker Compose Installation and Execution

To set up the project using Docker Compose, follow these steps:

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Yidti/jobscan.git
   cd jobscan
2. **Create a .env file with necessary environment variables.**
    
    > **Note:** This project is a sample and requires you to modify the environment settings in the `.env` file and `docker-compose.yml`. Apologies, the environment variables are not yet fully organized.
3. **Build and start the containers**:

    ```sh
    docker-compose up --build
4. **Access the services**:
   - **Airflow Webserver**: http://localhost:8080
   - **MongoDB**: http://localhost:27018
   - **MySQL**: http://localhost:3308
   - **Selenium Chrome**: http://localhost:4444
   - **FastAPI**: http://localhost:8888/docs

## Features
### Filter conditions need to be set in advance
* #### Set filters before website searching
  ```python
  # custom filter params for search - for yidti
  role = {'ro':'全職'}
  keyword = {'keyword':"後端工程師 python"}
  isnew = {'isnew':'三日內'}
  jobexp = {'jobexp':['1年以下', '1-3年']}
  mode = {'mode':'列表'}  # 一次能呈現比較多筆資料
  order = {'order':'日期排序'}
  asc = {'asc':'遞減'}
  filter_params = get_filter_params(role, keyword, isnew, jobexp, mode, order, asc)
  user = "yidti"
  title = "data_Engineer"
    ```
* #### Set filters for the data saved after web crawling."
  ```python
  # keywords for filter job again
  job_keywords = ('工程','資料','python','data','數據','後端')
  # Exclude keywords to filter out companies related to gambling or others that I don't want to consider.
  company_exclude = ('新加坡商冕創有限公司','新博軟體開發股份有限公司','現觀科技股份有限公司'
                        ,'全富數位有限公司','杰思數位有限公司','博凡星國際有限公司',
                        '尊博科技股份有限公司','新騎資訊有限公司','新加坡商鈦坦科技股份有限公司台灣分公司',
                        '豪穎科技股份有限公司','塶樂微創有限公司','磐弈有限公司',
                        '聯訊網路有限公司','冶金數位科技有限公司','肥貓科技有限公司',
                        '無名科技有限公司','博澭科技有限公司','緯雲股份有限公司',
                        '風采有限公司','英屬維京群島商嘉碼科技有限公司台灣分公司',
                        '冠宇數位科技股份有限公司','英仕國際有限公司','元遊科技有限公司',
                        '禾碩資訊股份有限公司','向上集團_向上國際科技股份有限公司',
                        '弈樂科技股份有限公司','馬來西亞商極限電腦科技有限公司台灣分公司',
                        '樂夠科技有限公司','威智國際有限公司','紅信科技有限公司',
                        '深思設計有限公司','揚帆科技有限公司','晶要資訊有限公司',
                        '九七科技股份有限公司','臣悅科技有限公司','尊承科技股份有限公司',
                        '遊戲河流有限公司','唐傳有限公司','捷訊資訊有限公司',
                        '逍遙遊科技有限公司','澄果資訊服務有限公司','果遊科技有限公司',
                        '昱泉國際股份有限公司','博星數位股份有限公司',
                        )
  print(f"設定排除{len(company_exclude)}家公司")
  ```

## ETL Structure
![image](https://github.com/Yidti/jobscan/assets/71652287/b79dfc64-3236-4828-991a-182b1353736e)
### Airflow Workflow
![image](https://github.com/Yidti/jobscan/assets/71652287/822a10ca-3720-448c-a539-ff9eff25831f)
- **Web Crawler**: Search results list and details from 104.
- **Export File**: Save data into an Excel file.
- **Data Lake**: Store data into NoSQL (MongoDB).
- **Data Warehouse**: Store data into SQL (MySQL).
- **FastAPI**: Develop RESTful API for accessing job listing data.
  
  ![image](https://github.com/Yidti/jobscan/assets/71652287/bb8c6de1-972b-4c5f-bd0a-aab3dc2381a0)

- **EDA (Exploratory Data Analysis)**:
  - **Vertical Bar Chart**: Education
    ![Education Vertical Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/727a4c91-f361-4732-a95e-b3f9464df0af)
  - **Horizontal Bar Chart**: Education
    ![Education Horizontal Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/2c8ed6e6-7885-4bca-98c3-7ddb17978eb0)
  - **Horizontal Bar Chart**: Major
    ![Major Horizontal Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/86ce4375-5f2a-4315-9290-9a4128c21411)
  - **Horizontal Bar Chart**: Skills
    ![Skills Horizontal Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/ceacd91e-88e5-4107-aee6-ba0e9e9b0303)
  - **Horizontal Bar Chart**: Tools
    ![Tools Horizontal Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/f08bad08-365f-4472-b343-c7512f05b1f0)
  - **Pie Chart**: Education
    ![Education Pie Chart](https://github.com/Yidti/jobscan/assets/71652287/5fa173ff-52e6-4438-9ac6-f8ee9a4d0968)
  - **Pie Chart**: Location
    ![Location Pie Chart](https://github.com/Yidti/jobscan/assets/71652287/6daad501-12ba-4783-94ca-128f8bb806b9)
  - **Pie Chart**: Major
    ![Major Pie Chart](https://github.com/Yidti/jobscan/assets/71652287/dacc8102-cb66-4d05-892d-c1c742c54c31)
  - **Pie Chart**: Skills
    ![Skills Pie Chart](https://github.com/Yidti/jobscan/assets/71652287/c71e28da-14b6-4aeb-8591-1e7b479f3c97)
  - **Pie Chart**: Tools
    ![Tools Pie Chart](https://github.com/Yidti/jobscan/assets/71652287/2c6273b7-0711-4252-8da5-0637e36e2ab4)
- **Data Cleaning and Merging**:
  - **Horizontal Bar Chart + Word Cloud**: Tools
    ![Tools Bar Chart + Word Cloud](https://github.com/Yidti/jobscan/assets/71652287/0db5848a-7236-4a7c-9af8-c0612d73648b)
  - **Vertical Bar Chart**: Tools
    ![Tools Vertical Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/61916ff1-2df0-4f62-9d77-7b1100c38e44)
  - **Horizontal Bar Chart**: Tools
    ![Tools Horizontal Bar Chart](https://github.com/Yidti/jobscan/assets/71652287/b44a8bfc-e60a-4505-aa8f-3b41d5ca17f8)

## References
- [JobSearcher](https://github.com/DrDAN6770/JobSearcher/tree/main)
- [Airflow Scraping ETL Tutorial](https://github.com/ChickenBenny/Airflow-scraping-ETL-tutorial)
