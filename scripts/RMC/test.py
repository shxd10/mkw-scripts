from dolphin import event, savestate, memory
import sys

path = r'C:\Users\Bloun\AppData\Local\Programs\Python\Python38\Lib\site-packages'
sys.path.append(path)
tk_path = r'C:\Users\Bloun\AppData\Local\Programs\Python\Python38\Lib'
sys.path.append(tk_path)
import tkinter


import time

def main():
    #savestate.load_from_slot(2)
    pass

if __name__ == '__main__':
    main()
    




def on_state_load(fromSlot: bool, slot: int):
    print('state loaded')
    time.sleep(5)
#event.on_savestateload(on_state_load)

def on_frame_advance():
    #print('frame advanced')
    pass
#event.on_frameadvance(on_frame_advance)


