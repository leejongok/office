import pyautogui,datetime,os

def shot() :
    dir = f"c:/users/{os.getlogin()}/downloads/"    
    if os.name == 'posix'  : dir = f'/home/{os.getlogin()}/다운로드/'
    fn = f"{dir}autocap{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-4]}.png"
    print(f'screenshot {fn}')
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(fn)
    return fn
    
if __name__ == '__main__':
    shot() 
