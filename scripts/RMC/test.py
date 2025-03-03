from dolphin import event, gui, utils, savestate, memory
import Modules.mkw_utils as mkw_utils
import sys
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, VehiclePhysics, RaceConfig
import time

def main():
    pass


if __name__ == '__main__':
    main()




  
@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    time.sleep(2)
    print('state loaded')
@event.on_frameadvance
def on_frame_advance():
    #time.sleep(2)
    #print('frame advance')
    pass

