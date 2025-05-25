from dolphin import event, savestate, memory, debug
from Modules.mkw_utils import frame_of_input
import sys
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState


def main():
    pass

if __name__ == '__main__':
    main()
    

        
def on_state_load(fromSlot: bool, slot: int):
    if not memory.is_memory_accessible():
        print('MEMORY NOT READABLE ON STATE LOAD')
event.on_savestateload(on_state_load)

def on_before_state_load(fromSlot: bool, slot: int):
    if not memory.is_memory_accessible():
        print('MEMORY NOT READABLE ON  BEFORE STATE LOAD')
event.on_beforesavestateload(on_before_state_load)


def on_state_save(fromSlot: bool, slot: int):
    if not memory.is_memory_accessible():
        print('MEMORY NOT READABLE ON STATE SAVE')  
event.on_savestatesave(on_state_save)

def on_frame_advance():
    frame = frame_of_input()
    print('FRAME_ADVANCE', frame)
#event.on_frameadvance(on_frame_advance)

def on_frame_begin():
    frame = frame_of_input()
    #time.sleep(1)
    print('FRAME_BEGIN', frame)
    
#event.on_framebegin(on_frame_begin)

def on_unpause():
    frame = frame_of_input()
    #time.sleep(1)
    print('UNPAUSE', frame)
    
#event.on_unpause(on_unpause)

def on_focuschange(focus):
    #time.sleep(1)
    print('FOCUS CHANGE', focus)
    
#event.on_focuschange(on_focuschange)

def on_rgc(x,y,h,w):
    #time.sleep(1)
    print('RGC', x,y,h,w)
    
#event.on_rendergeometrychange(on_rgc)


