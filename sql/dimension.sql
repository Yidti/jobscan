-- 把重複性高的column切割出來儲存成 Dimension Table








-- 經歷
CREATE TABLE IF NOT EXISTS working_exp(  
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    year_exp VARCHAR(10) NOT NULL,
    UNIQUE (year_exp)
);