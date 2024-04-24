-- 把重複性高的column切割出來儲存成 Dimension Table

-- company_id = 公司_id
-- company = 公司
-- company_link = 公司_link
CREATE TABLE IF NOT EXISTS company(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    company_id BIGINT NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_link VARCHAR(255),
    UNIQUE (company_id)
);

-- industry table
    -- industry_id = 產業_id
    -- industry = 產業
CREATE TABLE IF NOT EXISTS industry(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    industry_id BIGINT NOT NULL,
    industry_name VARCHAR(255) NOT NULL,
    UNIQUE (industry_id)
);

-- location_city_region table
    -- city = 縣市
    -- region = 區域
CREATE TABLE IF NOT EXISTS location_city_region(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(255) NOT NULL,
    region VARCHAR(255),
    UNIQUE (city, region),
    CHECK ((city IS NOT NULL AND region IS NOT NULL) OR (city IS NOT NULL))
);

-- location table
    -- city_region_id = 城市與區域
    -- address = 地址
CREATE TABLE IF NOT EXISTS location(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    city_region_id INT NOT NULL,
    address VARCHAR(255) NOT NULL,
    FOREIGN KEY (city_region_id) REFERENCES location_city_region(id)
);

-- experience = 經歷 (eg: 1年, 2年)
CREATE TABLE IF NOT EXISTS experience(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    experience_year VARCHAR(10) NOT NULL,
    UNIQUE (experience_year)
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
