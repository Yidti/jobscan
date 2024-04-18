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

-- industry_id = 產業_id
-- industry = 產業
CREATE TABLE IF NOT EXISTS industry(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    industry_id BIGINT NOT NULL,
    industry_name VARCHAR(255) NOT NULL,
    UNIQUE (industry_id)
);


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
    exp_year VARCHAR(10) NOT NULL,
    UNIQUE (exp_year)
);

