import os

from selenium.webdriver import Chrome, ChromeOptions, Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains

class Driver:
    
    @staticmethod
    def set_driver(driver_path, headless_flg):

        # Chromeドライバーの読み込み
        options = ChromeOptions()

        # ヘッドレスモード（画面非表示モード）をの設定
        if headless_flg == True:
            options.add_argument('--headless')

        # 起動オプションの設定
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
        # options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--user-data-dir=profile')
        # options.add_argument('--incognito')          # シークレットモードの設定を付与

        # ChromeのWebDriverオブジェクトを作成する。
        try:
            return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
        except Exception as e:
            print("driver起動エラー")
            print(e)
            return None
        
    @staticmethod
    def wait_for_element(driver,type,value,time=30):
        if type=="CLASS_NAME":type=By.CLASS_NAME
        elif type=="CSS_SELECTOR":type=By.CSS_SELECTOR
        else:type=By.CSS_SELECTOR
        wait = WebDriverWait(driver, time)
        wait.until(expected_conditions.visibility_of_element_located((type, value)))
        
    @staticmethod
    def accept_alert(driver):
        Alert(driver).accept()
        
    @staticmethod
    def move_to_element(driver,target):
        actions=ActionChains(driver)
        actions.move_to_element(target)
        actions.perform()
        