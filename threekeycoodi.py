from pynput.keyboard import Key,Controller, Listener
from pynput import mouse
import datetime, time

def action_ctrlc():
    keyboard = Controller()
    keyboard.press(Key.ctrl_l)
    keyboard.press('c')
    keyboard.release('c')
    keyboard.release(Key.ctrl_l)
    time.sleep(0.05)

class TKey:
    def __init__(self, tkey):
        self.tkey = tkey
        self.dt = datetime.datetime.now()
    def __repr__(self):
        return f"<<tkey:{self.tkey},dt:{self.dt}>>"
    
class TMouse:
    def __init__(self, pressed:bool):
        self.pressed = pressed
        self.dt = datetime.datetime.now()
    def __repr__(self):
        return f"<<pressed:{self.pressed},dt:{self.dt}>>"
    
class KeyService :
    def __init__(self, id, keyseq,  fn):
        self.id:str = id
        self.keyseq:list = keyseq
        self.fn:function = fn

klistener:Listener = None
mlistener:mouse.Listener = None

def exit_key_listen():
    print('exit listening')
    mlistener.stop()
    klistener.stop()
    return False


class TripleKeyInput:
    def __init__(self):
        print("the TripleKeyInput v.2")
        self.key_queue = []
        self.key_service_list:list[TKey] = []
        self.mouse_queue:list[TMouse] = []

    def find_keyservice_by_id(self, id:str)->KeyService :
        for ks in self.key_service_list:
            if ks.id == id:
                return ks

    def find_keyservice_by_keyseq(self,keyseq:list)->KeyService :
        for ks in self.key_service_list:
            if ks.keyseq == keyseq:
                return ks

    def add_keyservice(self, ks:KeyService):
        # check id duplication
        if self.find_keyservice_by_id(ks.id):
            print('id exists', ks.id)
            return False
        # check keyseq
        if self.find_keyservice_by_keyseq(ks.keyseq):
            print('keyseq exists', ks.keyseq)
            return False
        self.key_service_list.append(ks)

    def find_keyservice(self):
        first, second, third = self.key_queue
        
        for ks in self.key_service_list:
            if ks.keyseq == [first.tkey, second.tkey, third.tkey]:
                return ks
    

    def triple_combination(self):
        #print(self.key_queue)
        # 3개인지 확인
        if len(self.key_queue) != 3: 
            return # 입력키가 3개미만이므로 아무것도 안함. 
        # 1초 이내인지 확인
        first, second, third = self.key_queue
        ts = (third.dt - first.dt).total_seconds()
        #print('third.dt - first.dt',ts,'sec')
        if ts>=1: 
            return # 1초 이내가 아니므로 아무것도 안함.
        # 3개중 하나라도 esc, shift_l, ctrl_l 중에 하나가 아니라면, 아무것도 안함.
        if first.tkey not in [Key.esc, Key.shift_l, Key.ctrl_l] : 
            return
        if second.tkey not in [Key.esc, Key.shift_l, Key.ctrl_l] : 
            return
        if third.tkey not in [Key.esc, Key.shift_l, Key.ctrl_l] : 
            return
        #print('서비스에서 명령찾기')
        ks:KeyService = self.find_keyservice()
        #print(datetime.datetime.now(), 'ks is ',ks)
        if ks and ks.fn:
            self.key_queue = []
            return ks.fn()
        
        # if first.tkey == Key.esc and first.tkey == Key.esc and first.tkey == Key.esc :
        #     return False

    def key_on_release(self,key):
        if key not in [Key.esc, Key.shift_l, Key.ctrl_l] :
            if self.key_queue: self.key_queue = [] # esc또는 shift또는 ctrl키가 아니라면, key_queue를 초기화함(단,key_queue에 데이터가 있을때)
            return
        #print( key )
        if len(self.key_queue) >= 3 : self.key_queue = self.key_queue[1:]
        self.key_queue.append( TKey(key) )
        
        return self.triple_combination()
    
    def do_mouse_action(self):
        # press,0.3s이하,release + 0.6s이하 + press,0.3s~0.6s,release => action1
        # press,0.3s~0.6s,release + 0.6s이하 + press,0.3s이하,release => action2
        # press,0.3s~0.6s,release + 0.6s이하 + press,0.3s~0.6s,release => action3
        
        # print(self.mouse_queue)
        diff0 = (self.mouse_queue[1].dt  - self.mouse_queue[0].dt).total_seconds()
        diff1 = (self.mouse_queue[2].dt  - self.mouse_queue[1].dt).total_seconds()
        diff2 = (self.mouse_queue[3].dt  - self.mouse_queue[2].dt).total_seconds()
        
        print( diff0,diff1, diff2 )
        key_id:str = None
        if diff0 <= 0.3 and diff1 <= 0.6 and 0.3< diff2 <= 0.6:
            print("action1")
            key_id = "tran"
        elif 0.3 < diff0 <= 0.6 and diff1 <= 0.6 and diff2 < 0.3:
            print("action2")
            key_id = "dict"
        elif 0.3 < diff0 <= 0.6 and diff1 <= 0.6 and 0.3< diff2 <= 0.6:
            print("action3")
            key_id = "capture"
        else : return
        
        ks:KeyService = self.find_keyservice_by_id(key_id)
        return ks.fn()
    
    def on_click(self,x, y, button, pressed):
        if button != mouse.Button.right: 
            self.mouse_queue.clear()
            return
        
        if len(self.mouse_queue) == 2: #  기존의 오래된 rightclick이 있다면 지운다.
            diff = (datetime.datetime.now() - self.mouse_queue[1].dt).total_seconds()
            if diff > 0.6 : 
                self.mouse_queue.clear()            
        
        self.mouse_queue.append(TMouse(pressed))
            
        if len(self.mouse_queue) == 4:
            self.do_mouse_action()
            self.mouse_queue.clear()

    def start(self):
        global klistener, mlistener
        with Listener(  on_release=self.key_on_release ) as klistener, mouse.Listener(on_click=self.on_click) as mlistener :
            print("key listener : ", klistener)
            print("mouse listener : ", mlistener)
            klistener.join()
            mlistener.join()
            


if __name__ == '__main__':
    tk = TripleKeyInput()
    tk.add_keyservice( KeyService('exit', [Key.esc,Key.esc,Key.esc], exit_key_listen) )
    tk.start()

# press_time = None

# def key_on_release(key):
#     #print( datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3], 'key_on_release', key, type(key))
#     diff = datetime.datetime.now() - press_time
#     print('diff:',diff.total_seconds(), key )
#     if key==Key.esc:
#         return False

# def key_on_press(key):
#     #print(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3],'key_on_press', key, type(key))
#     global press_time
#     press_time = datetime.datetime.now()

# with Listener(  on_release=key_on_release, on_press=key_on_press ) as listener:
#     listener.join()