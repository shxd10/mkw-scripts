from dolphin import event, gui, utils
from external import external_utils as ex
from Modules import ttk_lib as lib
from Modules.framesequence import Frame
from Modules import mkw_utils as mkw_utils
import os

def run_input(_ = None):
    global position_history
    global pos_writer
    global end
    
    inp = input_reader.read_text().split(',')
    if len(inp) == 8 and inp[3] == '-1':
        #this logic is incorrect, most of the time
        inp[3] = int(inp[0])*int(inp[1])
    if len(inp) == 8:
        lib.write_player_inputs(Frame(inp))

def run_input_loop(_ = None):
    while True:
        run_input()
        time.sleep(1)
    
def main():
    global end
    end = False
    
    global input_writer
    input_writer = ex.SharedMemoryWriter('mkw tas input', 30)

    global input_reader
    input_reader = ex.SharedMemoryReader('mkw tas input')

    
    ex.start_external_script(os.path.join(utils.get_script_dir(), 'external', 'TAS_input_window.py'))

    
if __name__ == '__main__':
    main()



@event.on_framebegin
def on_frame_begin():
    run_input()
    
    
