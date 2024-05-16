from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Crawler():
    
    def __init__(self, remote=True, diff_container=False):
        self.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36' }
        self.remote = remote
        # 假如remote模式才考慮是不相容器下還是相同容器下
        self.diff_container = diff_container
        
        # 提示使用者
        if self.remote:
            print("use remote chrome setting")
        else:
            print("use local chrome setting")
            
        if self.diff_container:
            # 不同container 互相連線則改成容器名稱: chrome
            self.remote_url = 'http://chrome:4444/wd/hub'
        else:
            # 相同容器下的連線, 則使用localhost
            self.remote_url = 'http://localhost:4444/wd/hub'
        
    def configure_driver(self):
        option = Options()
        option.add_argument(f"user-agent={self.headers['User-Agent']}")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_argument('--headless')
        # option.add_argument("--disable-gpu")
        # option.page_load_strategy = 'none'
        option.add_argument(f"user-agent={self.headers['User-Agent']}")
        # option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
        # option.add_argument('--disable-gpu') # 規避部分chrome gpu bug
        # option.add_experimental_option("prefs", prefs)
        option.add_argument('blink-settings=imagesEnabled=false') #不加載圖片提高效率

        if self.remote:
            # Use webdriver.Remote to connect to the Selenium Grid
            driver = webdriver.Remote(
                command_executor=self.remote_url,
                options=option
            )
        else:
            # Use local webdriver.Chrome (in the same container)
            driver = webdriver.Chrome(options=option)
        
        driver.set_page_load_timeout(60)  # 設置頁面加載超時時間
        return driver
