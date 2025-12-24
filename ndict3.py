'''
cmd window가 없어지지 않을때, 아래와 같이 creationflags=0x08000000로 수정.
c:\\Python3A-64\\Lib\\site-packages\\selenium\\webdriver\\common\\service.py
self.process = subprocess.Popen(cmd, env=self.env, close_fds=platform.system() != 'Windows', stdout=self.log_file, stderr=self.log_file, stdin=PIPE, creationflags=0x08000000)
'''

import time
import urllib.parse, datetime
import webview
import multiprocessing


_width = 750
_height = 800
_p:multiprocessing.Process = None
_cmd_q :multiprocessing.Queue = None

def on_closed():
    print("window closed")
    global _p, _cmd_q
    if _p is not None and _p.is_alive():
        _p.join(2)
        if _p.is_alive():
            _p.terminate()
        _p = None
        _cmd_q = None

def run_webview(cmd_q, url="https://example.com"):
    window = webview.create_window( "myofc3", url, width=_width, height=_height, x=5,y=5 )
    window.events.closed += on_closed

    def controller():
        while True:
            cmd:str = cmd_q.get()
            if cmd == "close":
                window.destroy() # on_closed이 호출되면서 프로세스도 끝냄.
                break
            elif cmd.startswith("url:"):
                window.minimize()
                window.load_url(cmd[4:])                
                window.restore()
                window.show()

    import threading
    threading.Thread(target=controller, daemon=True).start()
    webview.start()
#-----------------------------------------------------------------------------------------------------------------
def destroy_and_close():
    _cmd_q.put("close")

#-----------------------------------------------------------------------------------------------------------------
def searchwordlist(word:str): 
    global _p, _cmd_q
    url = f"https://en.dict.naver.com/#/search?query={word}"
    if _p is None or not _p.is_alive():
        _cmd_q = multiprocessing.Queue()
        _p = multiprocessing.Process(target=run_webview, args=(_cmd_q,url))
        _p.start()
    else :
        _cmd_q.put(f"url:{url}")
    
#-----------------------------------------------------------------------------------------------------------------
def translate(text):    
    papagotranslate(text)

def papagotranslate(text):
    global _p, _cmd_q
    url = f'''https://papago.naver.com/?sk=auto&tk=ko&st={ urllib.parse.quote(text)}'''
    if _p is None or not _p.is_alive():
        _cmd_q = multiprocessing.Queue()
        _p = multiprocessing.Process(target=run_webview, args=(_cmd_q,url))
        _p.start()
    else :
        _cmd_q.put(f"url:{url}")

#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #driver = get_driver()
    
    import datetime
    print(datetime.datetime.now())
    driver = None
    # driver = searchwordlist(driver,'present')
    # driver = translate(driver,'''Gravity''')
    # ta = WebDriverWait(driver, 5).until( EC.presence_of_element_located( (By.CSS_SELECTOR, '''d-textarea[name="source"] > div[role="textbox"] > p''') ))
    # time.sleep(10)
    # # ta.clear() # 실패. clear후에는 send_keys함수 호출할때 에러남.
    # driver.execute_script("arguments[0].textContent = ' ';", ta) # blank를 넣어주면 에러남. 한글자라도 있어야함.
    # time.sleep(2)
    # ta.send_keys("help me.")
    # print(ta.get_attribute("outerHTML"))
    # time.sleep(30)
    driver = translate(driver,'Fraudsters promising to help after scams')
    time.sleep(60)

    
