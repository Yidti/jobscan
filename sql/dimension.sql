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

-- experience = 經歷 (eg: 1年, 2年)
CREATE TABLE IF NOT EXISTS experience(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    exp_year VARCHAR(10) NOT NULL,
    UNIQUE (exp_year)
);

