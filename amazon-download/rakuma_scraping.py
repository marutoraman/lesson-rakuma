### ラクマをリサーチしてCSVに出力する ###
import os
import eel
import time
import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from common.logger import set_logger


### 定数 ###
GOOGLE_URL = 'https://www.google.com/'
WAIT_TIME = 10 # 待機時間(秒)
CSV_FILE_NAME = 'amazon.csv'

logger = set_logger(__name__)


### Chromeドライバーの設定
def set_driver(driver_path, headless_flg):
    ## Chromeドライバーの読み込み
    if "chrome" in driver_path:
      options = ChromeOptions()
    else:
      options = Options()

    ## ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    ## 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    ## options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')    
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    ## ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(ChromeDriverManager().install(), options=options)
    else:
        return Firefox(options=options)


### ラクマ商品一覧CSVからURLを取得する
def get_rakuma_url():
    rakuma_file = pd.read_csv("./" + eel.rakuma_csv()())
    return rakuma_file["ラクマの商品一覧ページ"].tolist()


### 不要な文字を排除する
def sanitize(str):
    return str.replace('\n','').replace('\u3000' ,' ').replace('￥','').replace(',','').replace('商品説明','')


### ラクマ商品一覧URLから商品情報を取得する
def get_rakuma_item(driver,rakuma_list):
    classifying = eel.classifying()() # 対象商品分類
    max_page = eel.max_page()() # 1URLあたりの収集ページ数上限
    rakuma_item_urls = [] # ラクマ商品ページのURL

    for rakuma in rakuma_list:
    ## ラクマ商品一覧URL
        for page in range(1,int(max_page)+1):
        ## 収集ページ数上限まで
            is_soldout_query = "&transaction=soldout" if classifying == "inactive" else ""
            rakuma = f"{rakuma}&page={page}" if rakuma.find("?") >= 0 else f"{rakuma}?page={page}{is_soldout_query}"
            driver.get(rakuma)
            title_list = driver.find_elements_by_class_name('link_search_title')
            if len(title_list) == 0:
            ## 該当ページが無ければ抜ける
                title_list = driver.find_elements_by_class_name('link_category_title')
                if len(title_list) == 0:
                    break
            for title in title_list: ##
            ## 1ページ内の全商品
                rakuma_item_url = title.get_attribute('href')
                rakuma_item_urls.append(rakuma_item_url)

                logger.info(f'ラクマ読み込み : {title.text}')
    
    rakuma_items = []
    for rakuma_item_url in rakuma_item_urls:
    ## 全商品
        driver.get(rakuma_item_url)
        try:
            name = sanitize(driver.find_element_by_class_name('item__name').text)
            value = sanitize(driver.find_element_by_class_name('item__value').text)
            description = sanitize(driver.find_element_by_class_name('item__description').text)       
            
            try:
                driver.find_element_by_id('btn_sold')
                if classifying == 'inactive':
                ## 終了済み
                    rakuma_items.append((rakuma_item_url,name,value,description))
                    logger.info(f'終了済み ラクマの商品ページ : {rakuma_item_url}')                
            except NoSuchElementException:
                if classifying == 'active':
                ## 出品中
                    rakuma_items.append((rakuma_item_url,name,value,description))
                    logger.info(f'出品中 ラクマの商品ページ : {rakuma_item_url}')
        except:
            pass
    eel.view_log_js(f'ラクマ読み込み : {len(rakuma_items)}件')
    return rakuma_items


### URLからASINを取得する
def get_asin(url):
    asin = ''
    if '/dp/' in url:                    
        pos  = url.find('dp/')
        asin = url[pos + 3:pos + 13]
    return asin


### クエリーを指定してGoogle検索する
def google_search_by_query(driver,query,wait_time):
    driver.get(GOOGLE_URL)
    search = driver.find_element_by_name('q')
    search.send_keys(query)
    search.submit()
    time.sleep(wait_time)
    logger.info(f'検索クエリー : {query}')


### URLを指定してGoogle検索する
def google_search_by_url(driver,url,wait_time):
    driver.get(url)
    time.sleep(wait_time)


### 利益値でフィルターをかける
def gain_filter(driver,csv_item):
    url = f'https://www.amazon.co.jp/dp/{csv_item[0]}?language=ja_JP' # AmazonからASINコードで商品を検索する
    google_search_by_url(driver,url,WAIT_TIME)
    try:
        price = sanitize(driver.find_element_by_id('priceblock_ourprice').text)
        price = price[price.find("-")+1:] if price.find("-") >= 0 else price    
        gain = int(csv_item[3]) - int(price)
        eel_gain = int(eel.gain()())
        logger.info(f'ラクマ {csv_item[1]} {csv_item[3]}   Amazon {url} {sanitize(driver.find_element_by_id("priceblock_ourprice").text)}   利益 {str(gain)}')
    
        if gain >= eel_gain:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f'エラー:{e}')
        return False


### CSV出力対象リストを作成する
def get_csv_item(driver,rakuma_items):
    wrk_csv_items = []
    for rakuma_item in rakuma_items:
    ## 全商品
        #query = f'{rakuma_item[1]} site:amazon.co.jp'
        query = f'{rakuma_item[1]} site:amazon.co.jp'
        #url=f'https://www.google.com/search?q={rakuma_item[1]}+site%3Aamazon.co.jp&rlz=1C1QABZ_jaJP923JP923&aqs=chrome..69i57.11123j0j9&sourceid=chrome&ie=UTF-8'
        google_search_by_query(driver,query,WAIT_TIME)
        #google_search_by_url(driver,url,WAIT_TIME)
        flg = False
        while True:
        ## 全検索結果
            result_rows = driver.find_elements_by_class_name('yuRUbf')
            for result_row in result_rows:
                result_url = result_row.find_element_by_tag_name('a').get_attribute('href')
                asin = get_asin(result_url)
                if len(asin) > 0:                    
                ## CSV出力対象リストに追加する
                    wrk_csv_items.append((asin,rakuma_item[0],rakuma_item[1],rakuma_item[2],rakuma_item[3]))
                    logger.info(f'asinあり Amazonの商品ページ : {result_url}')
                    flg = True
                    break
            if flg:
                break
            else:
                try:
                    next_page = driver.find_element_by_id('pnnext').get_attribute('href')            
                    driver.get(next_page)
                    time.sleep(WAIT_TIME)
                except NoSuchElementException as e:
                    logger.warning(f'asin検索エラー: {e}')
                    break

    csv_items = []
    print(wrk_csv_items)
    ## 利益値でフィルターをかける
    for wrk_csv_item in wrk_csv_items:    
        try:
            if gain_filter(driver,wrk_csv_item):          
                csv_items.append((wrk_csv_item[0],wrk_csv_item[1],wrk_csv_item[2],wrk_csv_item[4]))
                logger.info(f'出力 : {(wrk_csv_item[0],wrk_csv_item[1],wrk_csv_item[2],wrk_csv_item[4])}')
        except  NoSuchElementException as e:
        ## Amazonに価格がなければ対象外
            logger.warning(f'Amazon価格取得エラー: {e}')
            pass

    eel.view_log_js(f'CSV出力 : {len(csv_items)}件')
    return csv_items


### CSVファイルを作成する
def toCsv(list,fileName):
    df = pd.DataFrame(list,columns=['ASIN', 'ラクマ商品URL', 'ラクマ商品名','ラクマ商品説明'])
    df.to_csv(fileName, index=False,encoding = 'utf-8_sig')


### ラクマをリサーチしてCSVに出力する
def research():
    ## driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    ## ラクマ商品一覧CSVからURLを取得する
    rakuma_urls = get_rakuma_url()
    print(rakuma_urls)

    ## ラクマ商品一覧URLから商品情報を取得する
    rakuma_items = get_rakuma_item(driver,rakuma_urls)
    
    ## CSV出力対象リストを作成する
    csv_items = get_csv_item(driver,rakuma_items)
    
    ## CSVファイルに出力する
    toCsv(csv_items,CSV_FILE_NAME)

    ## driverを終了
    driver.quit()

    return "終了しました"
