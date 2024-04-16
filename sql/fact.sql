-- 放置job_info的 Facts Table
-- update = 更新
-- position = 職缺
-- position_link = 職缺_link
-- company_id = 公司_id
-- company = 公司
-- company_link = 公司_link
-- industry_id = 產業_id
-- industry = 產業
-- city = 縣市
-- region = 區域
-- address = 地址
-- experience = 經歷
-- education = 學歷
-- content = 內容
-- category = 類別
-- major = 科系
-- language = 語文
-- tool = 工具
-- skill = 技能
-- other = 其他
-- benefits = 待遇
-- type = 性質
-- management = 管理
-- business_trip = 出差
-- working_hours = 時段
-- vacation = 休假
-- available = 可上
-- quantity = 人數
-- welfare = 福利

CREATE TABLE IF NOT EXISTS job_info (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_job INT NOT NULL,
    position VARCHAR(255) NOT NULL,
    content TEXT,
    exp_id INT NOT NULL,
    UNIQUE (id_job, exp_id),
    FOREIGN KEY (exp_id) REFERENCES experience(id)
);