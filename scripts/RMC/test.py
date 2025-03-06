from dolphin import event, savestate, memory
import sys
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
event.on_frameadvance(on_frame_advance)


while True:
    await event.savestateload()
    time.sleep(5)
    print('state loaded')
