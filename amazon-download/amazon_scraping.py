from logging import error
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import threading
import math
import eel
import os
import urllib3,urllib.request
import imghdr
import re

from common.logger import set_logger

logger = set_logger(__name__)

IMG_FOLDER_NAME="./img"

#ドライバーの設定
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
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

#高速化
def multi_thread():
    #指定したASINの情報を取得
    def get_detail(bot,ASINS,indices):
        # driverを起動
        if os.name == 'nt': #Windows
            driver = set_driver("chromedriver.exe", False)
        elif os.name == 'posix': #Mac
            driver = set_driver("chromedriver", False)

        no_stock_count=0
        no_asin_count=0
        error_count=0
        success_count=0
        count=0
        for ASIN,index in zip(ASINS,indices):               
            try: 
                error_flg=False
                url=""
                title=""
                price=""
                temp_img_list=[""]*4
                _detail=""
                _categorys=[]
                send=""
                
                #指定したASINのサイトに移動
                url = f"https://www.amazon.co.jp/dp/{ASIN}?language=ja_JP"
                driver.get(url)
                time.sleep(3)

                #商品のURLを取得し、商品ページに移動
                #try:
                    #item_url = driver.find_elements_by_css_selector(".a-size-base.a-link-normal.a-text-normal")[-1]
                    #url = item_url.get_attribute("href")
                    #driver.get(url)
                    #time.sleep(3)
                #except Exception:
                #    continue

                #タイトルの取得
                try:
                    title = driver.find_element_by_id("productTitle").text
                    #不要ワードの削除
                    for word in delete_list:
                        if word in title:
                            title = title.replace(word, "")
                    #40文字以上は削除
                    if len(title) > 40:
                        title = title[:40]
                except Exception as e:
                    logger.info(f"[スレッド{bot}] {count+1}件目 ASINエラー:{ASIN} / {e}")
                    eel.view_log_js(f"[スレッド{bot}] {count+1}件目 ASINエラー:{ASIN}")
                    no_asin_count+=1
                    error_flg=True
                    #continue


                #値段の取得
                try:
                    price = driver.find_element_by_id("price_inside_buybox").text[1:].replace(",", "")
                except Exception as e:
                    logger.info(f"[スレッド{bot}] {count+1}件目 在庫なしエラー:{ASIN} / {e}")
                    eel.view_log_js(f"[スレッド{bot}] {count+1}件目 在庫なしエラー:{ASIN}")
                    no_stock_count+=1
                    error_flg=True
                    #continue


                #画像の取得
                #try:
                #    img = driver.find_element_by_id("imgTagWrapperId").find_element_by_tag_name("img").get_attribute("src")
                #    
                #except Exception:
                #    continue
                #img_list.append(img)
                temp_img_list=amazon_img_download(driver,IMG_FOLDER_NAME,ASIN)
                        
                #説明文の取得
                try:
                    item_detail_table =  driver.find_element_by_id("feature-bullets")
                    ul = item_detail_table.find_element_by_tag_name("ul")
                    details = ul.find_elements_by_tag_name("li")
                    _detail = ""
                    for detail in details:
                        detail = detail.find_element_by_class_name("a-list-item").text
                        #不要ワードの削除
                        for word in delete_list:
                            if word in detail:
                                detail = detail.replace(word, "")
                        _detail += "・" + detail
                    #1000文字以上は削除
                    if len(_detail) >= 1000:
                        _detail = _detail[:1000]
                except Exception as e:
                    logger.info(f"[スレッド{bot}] {count+1}件目エラー:{ASIN} / {e}")
                    eel.view_log_js(f"[スレッド{bot}] {count+1}件目エラー:{ASIN}")
                    error_count+=1
                    error_flg=True
                    #continue


                #カテゴリーの取得
                try:
                    categorys = []
                    category_table = driver.find_element_by_css_selector(".a-unordered-list.a-horizontal.a-size-small")
                    category_li = category_table.find_elements_by_tag_name("li")
                    for li in category_li:
                        span = li.find_element_by_tag_name("span")
                        try:
                            a = span.find_element_by_tag_name("a")
                            category = a.text
                        except Exception:
                            category = ""
                        categorys.append(category)
                except Exception as e:
                    logger.info(f"[スレッド{bot}] {count+1}件目エラー:{ASIN} / {e}")
                    eel.view_log_js(f"[スレッド{bot}] {count+1}件目エラー:{ASIN}")
                    error_count+=1
                    error_flg=True
                    #continue
                _categorys = [category for category in categorys if category != '']


                #発送元の取得
                bool = True
                try:
                    send_from = driver.find_elements_by_class_name("tabular-buybox-text")[1]
                    if send_from.text[:6] != "Amazon":
                        bool = False
                    if bool:
                        send = "Amazon発送"
                    else:
                        send = "Amazon以外"
                except Exception as e:
                    logger.info(f"[スレッド{bot}] {count+1}件目エラー:{ASIN} / {e}")
                    eel.view_log_js(f"[スレッド{bot}] {count+1}件目エラー:{ASIN}")
                    error_count+=1
                    error_flg=True
                    #continue
            
                # CSV出力
                url_list.append(url)
                title_list.append(title)
                price_list.append(price)
                for i in range(4):
                    if len(temp_img_list)>i:
                        img_list[i].append(temp_img_list[i])
                    else:
                        img_list[i].append("")
                detail_list.append(_detail)
                categorys_list.append('›'.join(_categorys))
                send_list.append(send)
                error_flg_list.append(error_flg)
                exp_index_list.append(index)
                
                logger.info(f"[スレッド{bot}] {count+1}/{len(ASINS)}件目取得完了:{ASIN} / {title[:20]}")
                eel.view_log_js(f"[スレッド{bot}] {count+1}/{len(ASINS)}件目取得完了:{ASIN} / {title[:20]}")
                success_count+=1
                count += 1
                
            except Exception as e:
                logger.info(f"[スレッド{bot}] {count+1}件目エラー:{ASIN} / {e}")
                eel.view_log_js(f"[スレッド{bot}] {count+1}件目エラー:{ASIN}")
                error_count+=1
                count += 1
        
        eel.view_log_js(f"[スレッド{bot}][完了] 総数:{len(ASINS)} / 成功:{success_count} / ASINエラー:{no_asin_count} / 在庫なし:{no_stock_count} / その他エラー:{error_count}")
        driver.quit()


    #格納するリストの作成
    title_list = []
    price_list = []
    img_list = [""]*4
    img_list[0] = []
    img_list[1] = []
    img_list[2] = []
    img_list[3] = []
    url_list = []
    detail_list = []
    categorys_list = []
    send_list = []
    error_flg_list = []
    exp_index_list = []

    #不要ワードの読み込み
    delete_word_file = pd.read_csv("./" + eel.delete_word_file()())
    delete_list= delete_word_file["不要ワード"].tolist()

    #ASINリストの読み込み
    df = pd.read_csv("./" + eel.ASIN_file()())
    ASINS_list = df["ASIN"].tolist()
    index_list = df.index.values
    
    #listの分割
    thread_num = int(eel.thread_num()())
    n = math.ceil(len(ASINS_list) / thread_num)
    n=1 if n==0 else n # スレッド数＞ASIN数の場合はn=1とする
    split_list = [ASINS_list[i: i + n] for i in range(0,len(ASINS_list), n)]
    split_index_list = [index_list[i: i + n] for i in range(0,len(index_list), n)]
    
    threads = []
    bot = 1
    for ASINS,index in zip(split_list,split_index_list):
        t = threading.Thread(target=get_detail, args=([bot,ASINS,index]))
        t.start()
        threads.append(t)
        bot += 1
    for thread in threads:
        thread.join()

    #csvファイルの出力
    result = pd.DataFrame({"index":exp_index_list,"商品名": title_list, "金額": price_list,
                           "画像1": img_list[0], "画像2": img_list[1], "画像3": img_list[2], "画像4": img_list[3],
                           "URL": url_list, "商品説明": detail_list, "Amazonカテゴリー": categorys_list, "発送元": send_list,
                           "エラー":error_flg_list}) 
    result = result.sort_values("index")
    result.to_csv(eel.result_file()(), encoding="utf-8_sig",index=False)

    return "終了しました"

def amazon_img_download(driver,img_folder,asin):
    ''' 画像ダウンロード '''
    img_list = []
    imgs=[]
    html=driver.page_source #画面からだと遅延がひどいためHTMLのJSから直接取得
    imgs=re.findall(r',"large":"([\s\S]*?)",',html,flags=re.I)
    for i,img in enumerate(imgs):
        img_name = f"{asin}-{i+1}.jpg"
        file_path = f"./{img_folder}/{img_name}"
        img_list.append(img_name)
        urllib.request.urlretrieve(img, file_path)
        #画像は最大４枚まで
        if i>=3:
            break
        
    return img_list