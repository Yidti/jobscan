-- 放置job_info的 Facts Table

-- 1. id_job = 職缺 id
-- 2. update_date = 更新
-- 3. position = 職缺
-- 4. position_link = 職缺_link

-- 5. company_id = 公司  (dimention table: company)  
    -- company_id = 公司_id
    -- company_name = 公司名稱
    -- company_link = 公司_link

-- 6. industry_id = 產業  (dimention table: industry)  
    -- industry_id = 產業_id
    -- industry_name = 產業

-- 7. location_id = 位置 (dimention table: location_city_region)  
    -- city_region_id = 區域
    -- address = 地址
    -- table: location_city_region
        -- city = 縣市
        -- region = 區域

-- 8. address = 地址

-- 9. experience_id = 經歷  (dimention table: experience)  
    -- exp_year = 經歷_年

-- 10. education_id = 教育 (dimension table: education)
    -- education = 學歷

-- 11. content = 內容

-- List: category = 類別 list (dimension table: category)
    -- job_id
    -- category_item = 類別

-- List: major = 科系 list (dimension table: major) 
    -- job_id
    -- major_item = 科系

-- List: language = 語文 (dimension table: language) 
    -- job_id
    -- language_item = 語文

-- 15. tool = 工具
-- 16. skill = 技能
-- 17. other = 其他
-- 18. benefits = 待遇
-- 19. type = 性質
-- 21. management = 管理
-- 22.business_trip = 出差
-- 23. working_hours = 時段
-- 24. vacation = 休假
-- 25. available = 可上
-- 26. quantity = 人數
-- 27. welfare = 福利


-- position_link = 職缺_link

CREATE TABLE IF NOT EXISTS job_info (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    update_date DATE NOT NULL,
    position VARCHAR(255) NOT NULL,
    position_link VARCHAR(255),
    company_id BIGINT NOT NULL,
    industry_id BIGINT NOT NULL,
    location_id INT NOT NULL,
    experience_id INT NOT NULL,
    education_id INT NOT NULL,
    content TEXT,
    tool VARCHAR(1000),
    UNIQUE (job_id, company_id, industry_id, location_id, experience_id, education_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (industry_id) REFERENCES industry(industry_id),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (experience_id) REFERENCES experience(id),
    FOREIGN KEY (education_id) REFERENCES education(id)
);

-- category list 需要去 category去抓資料
-- major list 需要去 major去抓資料
-- language list 需要去 language去抓資料

