from dolphin import event, gui, utils
import configparser
import struct
from external import external_utils as ex
import Modules.agc_lib as lib
import Modules.settings_utils as setting
from Modules.mkw_classes import RaceManager, RaceState, VehiclePhysics, vec3
import Modules.mkw_utils as mkw_utils
import os


def history_to_bytes(p):
    ''' The encode will be 4 bytes for player pos_x, followed by 4 bytes for player pos_z
                    then 4 bytes for ghost pos_x, followed by 4 bytes for ghost pos_z,
                    repeat for all frames
        first bytes correspond to recent frame, last bytes to old frames'''
    res = bytearray()
    for frame_data in p:
        res = res + bytearray(struct.pack("f", frame_data['player'].x))
        res = res + bytearray(struct.pack("f", frame_data['player'].z))
        res = res + bytearray(struct.pack("f", frame_data['ghost'].x))
        res = res + bytearray(struct.pack("f", frame_data['ghost'].z))
    return bytes(res)
    
def main():
    global end
    end = False
    
    HISTORY_SIZE = 240
    
    def player_pos():
        try:
            return VehiclePhysics.position(0)
        except:
            return vec3(0,0,0)
        
    def ghost_pos():
        try:
            return VehiclePhysics.position(1)
        except:
            return vec3(0,0,0)
    
    global position_history
    position_history = mkw_utils.History({'player':player_pos, 'ghost':ghost_pos},
                                            HISTORY_SIZE)

    global frame
    frame = mkw_utils.frame_of_input()

    global pos_writer
    pos_writer = ex.SharedMemoryWriter('mkds minimap', HISTORY_SIZE*16)

    ex.start_external_script(os.path.join(utils.get_script_dir(), 'external', 'mkds_minimap_window.py'))

    
if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global position_history
    global frame
    global pos_writer
    global end

    if (not end) and frame != mkw_utils.frame_of_input():
        position_history.update()
        pos_writer.write(history_to_bytes(position_history))
        
    frame = mkw_utils.frame_of_input()

    try:
        a = ex.SharedMemoryReader('mkds minimap is running')
        a.close()
    except:
        pos_writer.close()
        end = True
        print('finished')

    
    
