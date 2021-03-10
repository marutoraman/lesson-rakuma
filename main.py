from engine.amazon.amazon_scraping import Amazon
from engine.rakuma.rakuma import Rakuma
import eel 

import common.firebase as firebase 
import common.desktop as desktop
from engine.rakuma.rakuma import * 
from engine.amazon.amazon_scraping import * 


app_name = "view" # フォルダ名
end_point = "index.html" # htmlファイル名
size = (700,600)

@eel.expose
def sample():
    rakuma = Rakuma()
    amazon = Amazon()

# 画面起動
desktop.start(app_name,end_point,size)
