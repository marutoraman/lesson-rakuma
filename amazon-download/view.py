import eel
import desktop
import amazon_scraping
import rakuma_scraping

app_name="html"
end_point="index.html"
size=(800,500)

@ eel.expose
def main():
    eel.view_log_js(amazon_scraping.multi_thread())


@ eel.expose
def research_main():
    eel.view_log_js(rakuma_scraping.research())


desktop.start(app_name,end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)