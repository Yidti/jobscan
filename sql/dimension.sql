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

-- location table
    -- city = 縣市
    -- region = 區域
CREATE TABLE IF NOT EXISTS location(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(255) NOT NULL,
    region VARCHAR(255),
    UNIQUE (city, region),
    CHECK ((city IS NOT NULL AND region IS NOT NULL) OR (city IS NOT NULL))
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

-- category = 分類 (eg: 軟體工程師.....)
CREATE TABLE IF NOT EXISTS category(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(255) NOT NULL,
    UNIQUE (category)
);

-- major = 分類 (eg: 資訊工程相關.....)
CREATE TABLE IF NOT EXISTS major(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    major VARCHAR(255) NOT NULL,
    UNIQUE (major)
);

-- major = 分類 (eg: 資訊工程相關.....)
CREATE TABLE IF NOT EXISTS language(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    language VARCHAR(100) NOT NULL,
    UNIQUE (language)
);
