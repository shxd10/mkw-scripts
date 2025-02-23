from dolphin import event, gui, utils, savestate, memory, controller
import Modules.mkw_utils as util
import sys
from Modules.mkw_classes import KartMove
from Modules import ttk_lib
from Modules import framesequence

def main():
    print("script started")

if __name__ == '__main__':
    main()

gc_a = {'Left': False,
    'Right': False,
    'Down': False,
    'Up': False,
    'Z': False,
    'R': False,
    'L': False,
    'A': True,
    'B': False,
    'X': False,
    'Y': False,
    'Start': False,
    'StickX': 128, # 0-255, 128 is neutral
    'StickY': 128, # 0-255, 128 is neutral
    'CStickX': 128,  # 0-255, 128 is neutral
    'CStickY': 128,  # 0-255, 128 is neutral
    'TriggerLeft': 0,  # 0-255
    'TriggerRight': 0,  # 0-255
    'AnalogA': 0,  # 0-255
    'AnalogB': 0,  # 0-255
    'Connected': True
        }

gc_b = {'Left': False,
    'Right': False,
    'Down': False,
    'Up': False,
    'Z': False,
    'R': False,
    'L': False,
    'A': True,
    'B': True,
    'X': False,
    'Y': False,
    'Start': False,
    'StickX': 128, # 0-255, 128 is neutral
    'StickY': 128, # 0-255, 128 is neutral
    'CStickX': 128,  # 0-255, 128 is neutral
    'CStickY': 128,  # 0-255, 128 is neutral
    'TriggerLeft': 0,  # 0-255
    'TriggerRight': 0,  # 0-255
    'AnalogA': 0,  # 0-255
    'AnalogB': 0,  # 0-255
    'Connected': True
        }

gc_no = {'Left': False,
    'Right': False,
    'Down': False,
    'Up': False,
    'Z': False,
    'R': False,
    'L': False,
    'A': False,
    'B': False,
    'X': False,
    'Y': False,
    'Start': False,
    'StickX': 128, # 0-255, 128 is neutral
    'StickY': 128, # 0-255, 128 is neutral
    'CStickX': 128,  # 0-255, 128 is neutral
    'CStickY': 128,  # 0-255, 128 is neutral
    'TriggerLeft': 0,  # 0-255
    'TriggerRight': 0,  # 0-255
    'AnalogA': 0,  # 0-255
    'AnalogB': 0,  # 0-255
    'Connected': True
        }
@event.on_frameadvance
def on_frame_advance():
    kart_move = KartMove()
    if util.frame_of_input() > 300 and kart_move.airtime() == 0:
        #controller.set_gc_buttons(0,gc_b)
        ttk_lib.write_player_inputs(framesequence.Frame([1,1,0,1,0,0,0,0]))
    if util.frame_of_input() > 300 and kart_move.airtime() != 0:
        #controller.set_gc_buttons(0,gc_a)
        ttk_lib.write_player_inputs(framesequence.Frame([1,0,0,0,0,0,0,0]))
    if 140 <= util.frame_of_input() <= 300 :
        #controller.set_gc_buttons(0,gc_a)
        ttk_lib.write_player_inputs(framesequence.Frame([1,0,0,0,0,0,0,0]))
    if util.frame_of_input() < 140 :
        #controller.set_gc_buttons(0,gc_no)
        ttk_lib.write_player_inputs(framesequence.Frame([0,0,0,0,0,0,0,0]))
