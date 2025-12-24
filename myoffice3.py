
#pip install pynput clipboard plyer pystray pyautogui pywebview pillow
import datetime,traceback, socket
# from win10toast import ToastNotifier
from plyer import notification
import plyer.platforms, plyer.platforms.win, plyer.platforms.win.notification # for plyer at windows of pyinstaller. 
import logging, logging.handlers
import sys
import pystray
from PIL import Image
import multiprocessing
import clipboard as cb
import os
import atexit
from pynput.keyboard import Key
import screenshot
import threading

# Ensure standard streams use UTF-8 so logging to console won't raise
# UnicodeEncodeError on Windows consoles using legacy code pages.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # If reconfigure isn't supported or fails, continue without crashing.
        pass

import ndict3 as mydict
import threekeycoodi

def _resource_path(relpath: str) -> str:
    """Return an absolute path to a resource, working when running frozen by PyInstaller.

    PyInstaller extracts bundled files to a temporary folder and sets ``sys._MEIPASS``.
    When not frozen, we resolve relative to the source file directory.
    """
    if getattr(sys, "frozen", False):
        # running in a PyInstaller bundle
        base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relpath)

sock = None

# log_fn = f'{os.path.dirname(__file__)+os.path.sep}myoffice.log'
# if os.path.isdir('c:/work/_log'): log_fn = 'c:/work/_log/myoffice.log'

#----------------------------------------------------------------------------------


def getLogger():
    from pathlib import Path
    path = Path("c:/work/_log")
    path.mkdir(parents=True, exist_ok=True)
    log_fn = str(path / "myoffice.log")
    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        sh = logging.StreamHandler()
        sh.setFormatter( logging.Formatter(fmt='[%(asctime)s,%(module)s,%(funcName)s,%(levelname)s ] %(message)s',datefmt='%Y-%m-%d %H:%M:%S ') )
        _logger.addHandler(sh)
        fh = logging.handlers.RotatingFileHandler(log_fn, maxBytes=9*1024*1024, backupCount=5, encoding='utf-8')
        fh.setFormatter( logging.Formatter(fmt='[%(asctime)s.%(msecs)03d,%(module)s,%(funcName)s,%(levelname)s] %(message)s',datefmt='%Y-%m-%d %H:%M:%S') )
        _logger.addHandler(fh)
        _logger.setLevel(level=logging.INFO)
    return _logger

logger = getLogger()

#----------------------------------------------------------------------------------
def from_clipboard()->str:
    data = cb.paste()
    return data


#----------------------------------------------------------------------------------
def dictcopyfindshow(): 
    threekeycoodi.action_ctrlc() # ctrl+c키를 눌려 클립보드로 복사하도록 함.
    cbtext = from_clipboard() # 클립보드에서 text 가져오기
    cbtext = cbtext.replace('\r\n',' ').replace('\n', ' ').strip()
    logger.info(f"searchwordlist({cbtext}) start")
    mydict.searchwordlist(cbtext)
    logger.info(f"searchwordlist({cbtext}) end")
#----------------------------------------------------------------------------------
def trancopyfindshow():    
    threekeycoodi.action_ctrlc() # ctrl+c키를 눌려 클립보드로 복사하도록 함.
    cbtext = from_clipboard() # 클립보드
    cbtext = cbtext.replace('\r\n',' ').replace('\n', ' ').strip()
    logger.info(f"translate START :: {cbtext}")
    mydict.translate(cbtext)
    logger.info("translate END :: %s", cbtext)

#----------------------------------------------------------------------------------
def show_notification(title: str, message: str, timeout: int, app_icon: str | None = None):
    """Show a desktop notification.

    If `app_icon` is not provided, try to use the bundled `translate.ico` via
    `_resource_path`. If the icon file isn't present, notify without an icon.
    """
    try:
        # default to bundled icon when available
        if app_icon is None:
            candidate = _resource_path("translate.ico")
            if os.path.exists(candidate):
                app_icon = candidate
            else:
                app_icon = None
    except Exception:
        app_icon = None

    logger.debug("notify: title=%s, icon=%s", title, app_icon)
    notification.notify(title=title, message=message, app_name="Office1", app_icon=app_icon, timeout=timeout)
    
#----------------------------------------------------------------------------------
def screencapture():
    logger.info(f"screenshot start")
    fn = screenshot.shot()
    show_notification(title = '스크린샷!', message = f"'{fn}'에 저장됨." ,  timeout = 1.2, )
    logger.info(f"screenshot {fn}에 저장.")
    logger.info(f"screenshot end")
#----------------------------------------------------------------------------------    
def exit_handler():
    global sock
    show_notification(title = '종료!', message = f"MYOFFICE종료됨" ,  timeout = 2, )
    logger.info(f"closing browser_window.")
    try : logger.info(f"close browser_window")
    except : logger.info('browser_window error')
    logger.info(f"closing sock.close().")
    try : sock.close()
    except : logger.info('sock.close() error')
    logger.info(f"{datetime.datetime.now().strftime('%H:%M:%S')},exit!. bye.")
    
#----------------------------------------------------------------------------------


def on_show(icon, item):
    logger.info("Show clicked")
    
def on_quit(icon, item):
    logger.info("on_quit started")
    threekeycoodi.exit_key_listen()
    icon.stop()
    mydict.destroy_and_close()
    # sys.exit(0)
    logger.info("on_quit finished")

def background_job(stop_event):
    
    logger.info(f"Start office app.")
    print("triple ESC press : EXIT APP.")
    print("triple SHIFT press : ENGLISH Translation for The Selected WORD.")
    print("triple CTRL press : ENGLISH DICTIONARY for The Selected WORD.")
    
    show_notification(title = 'MyOffice시작', message = f"SHIFT*3=번역,\nCTRL*3=사전,\nCTRL.SHIFT.CTRL=캡쳐" , timeout = 2.5, )
    
    atexit.register(exit_handler)

    tki = threekeycoodi.TripleKeyInput()
    tki.add_keyservice(threekeycoodi.KeyService('tran',[Key.shift_l,Key.shift_l,Key.shift_l],trancopyfindshow)) # 구우우글 번여꾸.
    tki.add_keyservice(threekeycoodi.KeyService('dict',[Key.ctrl_l,Key.ctrl_l,Key.ctrl_l],dictcopyfindshow)) # 네이버 사전
    tki.add_keyservice(threekeycoodi.KeyService('capture',[Key.ctrl_l,Key.shift_l,Key.ctrl_l],screencapture)) # 화면 캡
    tki.start()
    logger.info("background_job finished")


def main():
    logger.info(f"start myoffice1.")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.bind(("127.0.0.1", 30044))
    except Exception as ee:
        logger.error(f"oops. it already started(30044port is in use). exit.")
        traceback.print_exc()
        # ToastNotifier().show_toast("MyOffice시작실패", f"이미 실행중인것 같음.", duration=2.5, threaded=True)
        show_notification(title = 'MyOffice시작실패', message = f"이미 실행중인것 같음." ,timeout = 2, )
        sys.exit(1)

    menu = pystray.Menu(
        pystray.MenuItem("WhatIsIt", on_show),
        pystray.MenuItem("Quit", on_quit),
    )
    icon_path = _resource_path("translate.ico")
    try:
        icon_image = Image.open(icon_path)
    except FileNotFoundError:
        logger.error(f"translate.ico not found at {icon_path}. When building with PyInstaller include the file with --add-data.")
        raise
    icon = pystray.Icon( "MyOffice", icon_image,  "[MyOffice] Select any text, press Shift(or Ctrl) 3 times",   menu  )
    stop_event = threading.Event()
    worker = threading.Thread(target=background_job, args=(stop_event,), daemon=True)
    worker.start()

    try:
        logger.info("icon.run() starting")
        icon.run()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("KeyboardInterrupt caught, shutting down...")
        on_quit(icon, None)
    finally:
        stop_event.set()


if __name__ == '__main__':
    # Required when using multiprocessing with a frozen executable (PyInstaller) on Windows
    multiprocessing.freeze_support()
    main()





