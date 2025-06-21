from dolphin import event, gui, utils, memory
import configparser
import struct
from external import external_utils as ex
from Modules import agc_lib as lib
from Modules import settings_utils as setting
from Modules.mkw_classes import RaceManager, RaceState, VehiclePhysics, vec3
from Modules import mkw_utils as mkw_utils
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

def get_all_checkpoints():
    ''' The encode will be 4 bytes for left point_x, followed by 4 bytes for left point_z
                    then 4 bytes for right_point_x, followed by 4 bytes for right point_z,
                    repeat for all cp
        first bytes correspond to first cp, last bytes to last cp (i think)'''
    game_id = utils.get_game_id()
    address = {"RMCE01": 0x809B8F28, "RMCP01": 0x809BD6E8,
               "RMCJ01": 0x809BC748, "RMCK01": 0x809ABD28}
    kmp_ref = mkw_utils.chase_pointer(address[game_id], [0x4, 0x0], 'u32')
    ckpt_offset = memory.read_u32(kmp_ref+0x24)
    ckph_offset = memory.read_u32(kmp_ref+0x28)
    left_list = []
    right_list = []
    offset = ckpt_offset
    res = bytearray()
    id_list = bytearray()
    while offset < ckph_offset:
        res = res + bytearray(struct.pack("f", memory.read_f32(kmp_ref+0x4C+offset+0x8+0x0)))
        res = res + bytearray(struct.pack("f", memory.read_f32(kmp_ref+0x4C+offset+0x8+0x4)))
        res = res + bytearray(struct.pack("f", memory.read_f32(kmp_ref+0x4C+offset+0x8+0x8)))
        res = res + bytearray(struct.pack("f", memory.read_f32(kmp_ref+0x4C+offset+0x8+0xC)))
        id_list = id_list + bytearray(struct.pack("b", memory.read_s8(kmp_ref+0x4C+offset+0x8+0x11)))
        offset += 0x14
    return bytes(res[:256*16]), bytes(id_list[:256])


    
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

    global cp_writer
    cp_writer = ex.SharedMemoryWriter('mkds minimap checkpoints', 256*16)

    global cp_id_writer
    cp_id_writer = ex.SharedMemoryWriter('mkds minimap checkpoints_id', 256)

    global yaw_writer
    yaw_writer = ex.SharedMemoryWriter('mkds minimap yaw', 4)
    
    ex.start_external_script(os.path.join(utils.get_script_dir(), 'external', 'mkds_minimap_window.py'))

    
if __name__ == '__main__':
    main()
@event.on_savestateload
def clear_history(*_):
    position_history.clear()

@event.on_frameadvance
def on_frame_advance():
    global position_history
    global frame
    global pos_writer
    global end

    if (not end) and frame != mkw_utils.frame_of_input():
        position_history.update()
        cp, cp_id = get_all_checkpoints()
        try:
            pos_writer.write(history_to_bytes(position_history))
            cp_writer.write(cp)
            cp_id_writer.write(cp_id)
            yaw_writer.write(struct.pack('f', mkw_utils.get_facing_angle(0).yaw))
            
        except:
            end = True
            print('mkds minimap closed')
        
    frame = mkw_utils.frame_of_input()


    
    
