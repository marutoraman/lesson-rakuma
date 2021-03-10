import os
import sys
import requests
import csv
import urllib.request
import datetime
import time
import pyperclip
import imghdr
import eel
import urllib3
import re
import json
from subprocess import PIPE, Popen
import os

import common.desktop as desktop

DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'


def get_current_window_name():
    for i in Popen(['xprop', '-root'],  stdout=PIPE).stdout:
        if '_NET_ACTIVE_WINDOW(WINDOW):' in i:
            for j in Popen(['xprop', '-id', i.split()[4]], stdout=PIPE).stdout:
                if 'WM_ICON_NAME(STRING)' in j:
                    return j.split()[2][1:][:-1]

def toggle_foreground(app_name):
    app = get_current_window_name()
    if not app or not 0 is app.find(app_name):
        os.system('wmctrl -a ' + app_name)
    else:
        os.system('xwit -iconify -names ' + app_name)

def getAbsPath():  # 作業パス取得
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        running_mode = 'Frozen/executable'
    else:
        try:
            app_full_path = os.path.realpath(__file__)
            application_path = os.path.dirname(app_full_path)
            running_mode = "Non-interactive (e.g. 'python myapp.py')"
        except NameError:
            application_path = os.getcwd()
            running_mode = 'Interactive'
    return application_path + os.sep

def now_string():
  return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def log(txt):
    now = datetime.datetime.now()
    logStr = '[%s: %s] %s' % ('log', now.strftime(DATE_FORMAT), txt)
    # ログ出力
    with open(absPath + logFile, 'a', encoding='utf-8') as f:
        f.write(logStr + '\n')
    print(logStr)

def printDate(text):
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f') + " " + text) 

def log(txt):
    now = datetime.datetime.now()
    logStr = '[%s: %s] %s' % ('log', now.strftime(DATE_FORMAT), txt)
    # ログ出力
    with open(absPath + logFile, 'a', encoding='utf-8') as f:
        f.write(logStr + '\n')
    print(logStr)

def get_list(list,index=0):
  if len(list)>=1:
    return list[index]
  else:
    return ""

def readCSV(path,delimiter,skipHeader=True,encoding="utf-8"):
      # 入力ファイルの読み込み
  try:
    with open(path , "r", encoding=encoding) as f:
      if skipHeader==True:
        h = next(csv.reader(f)) # ヘッダ行を読み飛ばし
      
      reader= csv.reader(f,delimiter=delimiter)
      #temp = [row for row in reader ]
      inputData=[]
      for d in reader:
          inputData.append(d)
      return inputData
  except FileNotFoundError as e: # FileNotFoundErrorは例外クラス名
    print("ファイルが見つかりません", e)
    return None
  except Exception as e: # Exceptionは、それ以外の例外が発生した場合
    print(e)
    return None

def write_csv(filepath,data,delimiter=",",encoding="utf-8",date_mode=True):
  date=""
  if date_mode:
    date=now.strftime('%Y%m%d') 
  # 現状のファイルの行数を取得
  file_data=readCSV(os.getcwd() +  filepath + date + ".csv",delimiter,encoding=encoding)
  # 出力項目リストを作成
  fieldnames=[]
  for key in data.keys():
    fieldnames.append(key)
  # 結果をCSV出力
  try:
    with open(os.getcwd() + filepath + date + ".csv", "a",encoding=encoding,newline="",errors="ignore") as f:
      writer =  csv.DictWriter(f, fieldnames=fieldnames,delimiter=delimiter)
      if file_data==None: # ０行ならヘッダを付与
        writer.writeheader()
      writer.writerow(data)
  except Exception as e:
    log("CSV書き込みエラー")
    import traceback
    log(traceback.format_exc())
    pass

def write_text(filepath,data,mode,encoding="utf-8"):
  with open(os.getcwd() + filepath ,mode=mode,encoding=encoding) as f:
    f.write(data + "\n")

def read_text(filepath):
  with open(os.getcwd() + filepath,encoding="utf-8") as f:
    return f.read()  # ファイル終端まで全て読んだデータを返す
  
def write_csv_array(filepath,data,mode="w",delimiter=",",encoding="utf-8"):
  with open(os.getcwd() + "\\" + filepath , mode=mode) as file:
    writer = csv.writer(file, lineterminator='\n',delimiter=delimiter)
    writer.writerows(data)


def read_csv_dic(path,delimiter,encoding):
    # 入力ファイルの読み込み
    try:
        with open(os.getcwd() + "\\" + path, "r", encoding=encoding) as f:
            csv_header=next(csv.reader(f,delimiter=delimiter)) # ヘッダ行の設定
            reader = csv.DictReader(f, csv_header,delimiter=delimiter)
            data = [row for row in reader]
            return data
    except FileNotFoundError as e: # FileNotFoundErrorは例外クラス名
        log("エラー：ファイルが見つかりません")
        sys.exit
    except Exception as e: # Exceptionは、それ以外の例外が発生した場合
        print(e)
        sys.exit

def write_json(path,json_list):
  # JSON ファイルへの書き込み
  with open(path, 'w') as f:
      json.dump(json_list, f)

def randomSleep(begin,end):
  if begin=="":
    begin=0
  if end=="":
    end=0
  time.sleep(random.randint(int(begin),int(end)))  

def getDateDelta(delta):
  now=datetime.datetime.now()
  return now+datetime.timedelta(days=int(delta))

def img_download(img_src,img_save_path):
  # ダウンロード
  request_methods = urllib3.PoolManager()
  responce = request_methods.request('GET', img_src)
  # エラーの場合は終了
  if not responce.status==200:
    log("画像ファイルダウンロードエラー")
    log(img_src)
    return ""
  # 拡張子取得
  ext=imghdr.what(None,h=responce.data)
  # 取得できないタイプの場合、別の方法で取得
  if ext is None:
    ext = responce.headers['Content-Type'].split('/')[1]
  # 拡張子変換
  if ext=="jpeg":
      ext="jpg"
  elif ext=="svg+xml":
    ext="svg"
  # 画像保存
  result_path=img_save_path + "." + ext
  with open(os.getcwd() + result_path, "wb") as f: 
    f.write(responce.data)

  return result_path

def trim(text):
  return text.replace("\n","").replace(" ","").replace("　","")

def get_html(url,  headers="",referer='',apiFlg=False):  # GET処理
    #headers = getHeader(referer, apiFlg)
    html = requests.get(url, headers=headers)
    html.encoding = html.apparent_encoding  # 文字化け対応
    return html

def get_doller_yen_rate():
  json_data=get_json("https://api.exchangeratesapi.io/latest?base=USD")
  return float(json.dumps(json_data["rates"]["JPY"]))

def get_yen_krw_rate():
  json_data=get_json("https://api.exchangeratesapi.io/latest?base=JPY")
  return float(json.dumps(json_data["rates"]["KRW"]))
  
def get_json(url, referer=''):  # GET処理
  headers= {"content-type": "application/json"}
  respons = requests.get(url, headers=headers)
  return respons.json()

# 共通変数
now = datetime.datetime.now()
fileDate = now.strftime(DATE_FORMAT)
logFile = "\\log\\log_" + fileDate + '.txt'
absPath = getAbsPath()