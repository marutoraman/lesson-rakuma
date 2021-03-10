import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from base64 import a85encode
import os
from pandas.core.algorithms import mode
import time
import pandas as pd
import eel


IMG_FOLDER_PATH="img"
DELETE_DATE=-1

def login(inp):
    df = pd.read_csv("./setting.csv",encoding="utf-8_sig")
    cred = credentials.Certificate(f'./{list(df["firebase_json_name"])[0]}')
    try:
        app = firebase_admin.initialize_app(cred)
    except:
        pass
    db = firestore.client()
    users_ref = db.collection(u'users')
    docs = users_ref.stream()
    print("Firebaseを参照にパスワードとなるkeyを入力してください：")
    for doc in docs:
        # print(u'{} => {}'.format(doc.id, doc.to_dict()))
        # print(doc.to_dict().values())
        for mykey in doc.to_dict().values():
            # print(mykey)
            while (True):
                # inp = input()
                if inp != mykey:
                    print('パスワードが違います。再度入力してください。')
                    eel.undisplay()
                    eel.write("パスワードが違います。再度入力してください。")
                    break
                else:
                    print('ログイン成功')
                    eel.display()
                    eel.write("ログイン成功")
                    
                    time.sleep(1)
                    # 何かしらの関数
                    # print(myprint(inp))
                    
                    break


