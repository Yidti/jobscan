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

-- 7. location_id = 位置 (dimention table: location)  
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

-- List: tool = 工具 (dimension table: tool)
    -- job_id
    -- tool_item = 工具

-- List. skill = 技能 (dimension table: tool)
    -- job_id
    -- skill_item = 技能

-- 12. other = 其他

-- 13. benefits_id = 待遇 (dimension table: benefits)
    -- benefits = 待遇

-- 14. type_id = 性質 (dimension table: type)
    -- type = 性質

-- 15. management_id = 管理 (dimension table: management)
    -- management = 管理

-- 16.business_trip = 出差 (dimension table: business_trip)
    -- business_trip = 出差

-- 17. working_hours = 時段 (dimension table: working_hours)
    -- working_hours = 時段

-- 18. vacation = 休假 (dimension table: vacation)
    -- vacation = 休假

-- 19. available = 可上工時間 (dimension table: available)
    -- available = 休假

-- 20. quantity = 人數 (dimension table: quantity)
    -- quantity = 人數

-- 21. welfare = 福利

CREATE TABLE IF NOT EXISTS job_info (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    update_date DATE NOT NULL,
    position VARCHAR(255) NOT NULL,
    position_link VARCHAR(255),
    company_id BIGINT NOT NULL,
    industry_id BIGINT NOT NULL,
    location_id BIGINT NOT NULL,
    experience_id INT NOT NULL,
    education_id INT NOT NULL,
    content TEXT NOT NULL,
    other TEXT NOT NULL,
    benefits_id INT NOT NULL,
    type_id INT NOT NULL,
    management_id INT NOT NULL,
    business_trip_id INT NOT NULL,
    working_hours_id INT NOT NULL,
    vacation_id INT NOT NULL,
    available_id INT NOT NULL,
    quantity_id INT NOT NULL,
    welfare TEXT NOT NULL,
    UNIQUE (job_id),
    -- CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES company(id),
    -- CONSTRAINT fk_industry FOREIGN KEY (industry_id) REFERENCES industry(id),
    CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES location(id),
    CONSTRAINT fk_experience FOREIGN KEY (experience_id) REFERENCES experience(id),
    CONSTRAINT fk_education FOREIGN KEY (education_id) REFERENCES education(id),
    CONSTRAINT fk_benefits FOREIGN KEY (benefits_id) REFERENCES benefits(id),
    CONSTRAINT fk_type FOREIGN KEY (type_id) REFERENCES type(id),
    CONSTRAINT fk_management FOREIGN KEY (management_id) REFERENCES management(id),
    CONSTRAINT fk_business_trip FOREIGN KEY (business_trip_id) REFERENCES business_trip(id),
    CONSTRAINT fk_working_hours FOREIGN KEY (working_hours_id) REFERENCES working_hours(id),
    CONSTRAINT fk_vacation FOREIGN KEY (vacation_id) REFERENCES vacation(id),
    CONSTRAINT fk_available FOREIGN KEY (available_id) REFERENCES available(id),
    CONSTRAINT fk_quantity FOREIGN KEY (quantity_id) REFERENCES quantity(id)
);

-- category list 需要去 category去抓資料
-- major list 需要去 major去抓資料
-- language list 需要去 language去抓資料
-- tool list 需要去 tool去抓資料
-- skill list 需要去 skill去抓資料

