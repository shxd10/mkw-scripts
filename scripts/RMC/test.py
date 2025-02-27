from dolphin import event, gui, utils, savestate, memory
import Modules.mkw_utils as mkw_utils
import sys
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, TimerManager, RaceConfig

def main():
    print("script started")

if __name__ == '__main__':
    main()




  
@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):

    print('state loaded')
@event.on_frameadvance
def on_frame_advance():
    pass
    #print('frame advance')


