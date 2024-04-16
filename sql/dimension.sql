-- 把重複性高的column切割出來儲存成 Dimension Table








-- experience = 經歷 (eg: 1年, 2年)
CREATE TABLE IF NOT EXISTS experience(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    exp_year VARCHAR(10) NOT NULL,
    UNIQUE (exp_year)
);


