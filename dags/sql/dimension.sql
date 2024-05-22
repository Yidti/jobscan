-- 把重複性高的column切割出來儲存成 Dimension Table

-- company_id = 公司_id
-- company = 公司
-- company_link = 公司_link
CREATE TABLE IF NOT EXISTS company(  
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    company_id BIGINT NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_link VARCHAR(255) NOT NULL, 
    UNIQUE (company_id, company_name, company_link)
);

-- industry table
    -- industry_id = 產業_id
    -- industry = 產業
CREATE TABLE IF NOT EXISTS industry(  
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    industry_id BIGINT NOT NULL,
    industry_name VARCHAR(255) NOT NULL,
    UNIQUE (industry_id, industry_name)
);

-- location_city_region table
    -- city = 縣市
    -- region = 區域
CREATE TABLE IF NOT EXISTS location_city_region(
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(255) NOT NULL,
    region VARCHAR(255),
    UNIQUE (city, region),
    CHECK ((city IS NOT NULL AND region IS NOT NULL) OR (city IS NOT NULL))
);

-- location table
    -- city_region_id = 城市與區域
    -- address = 地址
CREATE TABLE IF NOT EXISTS location(
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    city_region_id BIGINT NOT NULL,
    address VARCHAR(255) NOT NULL,
    FOREIGN KEY (city_region_id) REFERENCES location_city_region(id)
);

-- experience = 經歷 (eg: 1年, 2年)
CREATE TABLE IF NOT EXISTS experience(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    experience VARCHAR(10) NOT NULL,
    UNIQUE (experience)
);

-- education = 教育 (eg: 學士, 碩士)
CREATE TABLE IF NOT EXISTS education(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    education VARCHAR(10) NOT NULL,
    UNIQUE (education)
);


-- category_item = 分類(item, eg: 軟體工程師)
CREATE TABLE IF NOT EXISTS category_item(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    category_item VARCHAR(255) NOT NULL,
    UNIQUE (category_item)
);


-- category = 分類 (list, eg: 軟體工程師,AI工程師,...)
CREATE TABLE IF NOT EXISTS category(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    category_item VARCHAR(255) NOT NULL,
    FOREIGN KEY (category_item) REFERENCES category_item(category_item)
);

-- major_item = 主修 (item, eg: 光電...)
CREATE TABLE IF NOT EXISTS major_item(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    major_item VARCHAR(255) NOT NULL,
    UNIQUE (major_item)
);

-- major = 主修 (list, eg: 光電...,數學...)
CREATE TABLE IF NOT EXISTS major(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    major_item VARCHAR(255) NOT NULL,
    FOREIGN KEY (major_item) REFERENCES major_item(major_item)
);

-- language_item = 主修 (item, eg: 中文...)
CREATE TABLE IF NOT EXISTS language_item(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    language_item VARCHAR(255) NOT NULL,
    UNIQUE (language_item)
);

-- language = 語言 (list, eg: 中文, 英文.....)
CREATE TABLE IF NOT EXISTS language(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    language_item VARCHAR(255) NOT NULL,
    FOREIGN KEY (language_item) REFERENCES language_item(language_item)
);

-- tool_item = 工具 (item, eg: C#....)
CREATE TABLE IF NOT EXISTS tool_item(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    tool_item VARCHAR(255) NOT NULL,
    UNIQUE (tool_item)
);

-- tool = 工具 (list, eg: C#, Python.....)
CREATE TABLE IF NOT EXISTS tool(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    tool_item VARCHAR(255) NOT NULL,
    FOREIGN KEY (tool_item) REFERENCES tool_item(tool_item)
);

-- skill_item = 技能 (item, eg: 系統架構規劃....)
CREATE TABLE IF NOT EXISTS skill_item(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    skill_item VARCHAR(255) NOT NULL,
    UNIQUE (skill_item)
);

-- skill = 技能 (list, eg: 系統架構規劃, 軟體程式設計.....)
CREATE TABLE IF NOT EXISTS skill(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    skill_item VARCHAR(255) NOT NULL,
    FOREIGN KEY (skill_item) REFERENCES skill_item(skill_item)
);

-- benefits = 待遇 (eg: 待遇面議)
CREATE TABLE IF NOT EXISTS benefits(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    benefits VARCHAR(255) NOT NULL,
    UNIQUE (benefits)
);

-- type = 性質 (eg: 全職)
CREATE TABLE IF NOT EXISTS type(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(255) NOT NULL,
    UNIQUE (type)
);

-- management = 性質 (eg: 全職)
CREATE TABLE IF NOT EXISTS management(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    management VARCHAR(255) NOT NULL,
    UNIQUE (management)
);

-- business_trip = 出差 (eg: 無需出差外派)
CREATE TABLE IF NOT EXISTS business_trip(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    business_trip VARCHAR(255) NOT NULL,
    UNIQUE (business_trip)
);

-- working_hours = 時段 (eg: 日班) - 由於中文要判斷重複的部分 在此會出現錯誤 
CREATE TABLE IF NOT EXISTS working_hours(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    working_hours VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    UNIQUE (working_hours)
);

-- vacation = 休假 (eg: 周休二日) 
CREATE TABLE IF NOT EXISTS vacation(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    vacation VARCHAR(255) NOT NULL,
    UNIQUE (vacation)
);

-- available = 可上班時間 (eg: 一個月內) 
CREATE TABLE IF NOT EXISTS available(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    available VARCHAR(255) NOT NULL,
    UNIQUE (available)
);

-- quantity = 人數 (eg: 1~2人) 
CREATE TABLE IF NOT EXISTS quantity(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    quantity VARCHAR(255) NOT NULL,
    UNIQUE (quantity)
);

