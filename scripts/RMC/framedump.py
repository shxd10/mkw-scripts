from dolphin import event, savestate, utils
from Modules import mkw_utils as mkw_utils
from Modules.agc_lib import AGCMetaData
from Modules.framesequence import Frame
from external import external_utils as ex
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, KartObjectManager, VehiclePhysics, vec3

from pathlib import Path
import os
import datetime
import time

def main():

    #TODO : Save XFB setting

    global folder_path
    folder_path = os.path.join(utils.get_script_dir(), 'FrameDumps')
    #Create folders if needed
    Path(os.path.join(folder_path, 'RAM_data', 'nul.nul')).parent.mkdir(exist_ok=True, parents=True)
    for filename in os.listdir(os.path.join(folder_path, 'RAM_data')):
        os.remove(os.path.join(folder_path, 'RAM_data', filename))
    
    if not (utils.is_framedumping() or utils.is_audiodumping()):
        utils.start_framedump()
        utils.start_audiodump()
    else:
        print("Don't start this script when already dumping")
        utils.cancel_script(utils.get_script_name())

    global frame_counter
    frame_counter = 0 #Count the frame of dumps, different from frame of input

    global framedump_prefix
    framedump_prefix = None

    global state_counter, state
    state_counter = 0
    state = 0

@event.on_scriptend
def scriptend(id_):

    #TODO : Resotre XFB setting

    print(framedump_prefix)
    if utils.get_script_id() == id_:
        if (utils.is_framedumping() and utils.is_audiodumping()):
            utils.stop_framedump()
            utils.stop_audiodump()
            if utils.is_paused():
                utils.toggle_play()
            ex_script_path = os.path.join(folder_path, 'encoder.py')
            ex_info_path = os.path.join(folder_path, 'dump_info.txt')
            with open(ex_info_path, 'w') as f:
                f.write(f'{framedump_prefix}\n')
            ex.start_external_script(ex_script_path, False, False)

def frame_text():
    text = ''
    text += f'frame_of_input:{mkw_utils.frame_of_input()}\n'
    text += f'yaw:{mkw_utils.get_facing_angle(0).yaw}\n'
    text += f'spd_x:{mkw_utils.delta_position(0).x}\n'
    text += f'spd_y:{mkw_utils.delta_position(0).y}\n'
    text += f'spd_z:{mkw_utils.delta_position(0).z}\n'
    text += f'iv_x:{VehiclePhysics.internal_velocity(0).x}\n'
    text += f'iv_y:{VehiclePhysics.internal_velocity(0).y}\n'
    text += f'iv_z:{VehiclePhysics.internal_velocity(0).z}\n'
    text += f'ev_x:{VehiclePhysics.external_velocity(0).x}\n'
    text += f'ev_y:{VehiclePhysics.external_velocity(0).y}\n'
    text += f'ev_z:{VehiclePhysics.external_velocity(0).z}\n'
    text += f'mvr_x:{VehiclePhysics.moving_road_velocity(0).x}\n'
    text += f'mvr_y:{VehiclePhysics.moving_road_velocity(0).y}\n'
    text += f'mvr_z:{VehiclePhysics.moving_road_velocity(0).z}\n'
    text += f'mvw_x:{VehiclePhysics.moving_water_velocity(0).x}\n'
    text += f'mvw_y:{VehiclePhysics.moving_water_velocity(0).y}\n'
    text += f'mvw_z:{VehiclePhysics.moving_water_velocity(0).z}\n'
    text += f'cp:{RaceManagerPlayer(0).checkpoint_id()}\n'
    text += f'kcp:{RaceManagerPlayer(0).max_kcp()}\n'
    text += f'rp:{RaceManagerPlayer(0).respawn()}\n'
    text += f'racecomp:{RaceManagerPlayer(0).race_completion()}\n'
    text += f'lapcomp:{RaceManagerPlayer(0).lap_completion()}\n'
    text += f'input:{Frame.from_current_frame(0)}\n'
    text += f'state:{state}\n'
    text += f'state_counter:{state_counter}\n'
    return text
    
@event.on_frameadvance
def on_frame_advance():
    global frame_counter

    global framedump_prefix

    global state_counter, state

    if state == mkw_utils.extended_race_state():
        state_counter += 1
    else:
        state = mkw_utils.extended_race_state()
        state_counter = 0
    
    if frame_counter == 0:
        c = datetime.datetime.now()
        framedump_prefix = f"{utils.get_game_id()}_{c.year}-{c.month:02d}-{c.day:02d}_{c.hour:02d}-{c.minute:02d}-{c.second:02d}"
    if mkw_utils.extended_race_state() in [1,2,3,4]:
        with open(os.path.join(folder_path, 'RAM_data', f'{frame_counter}.txt'), 'w') as f:
            f.write(frame_text())
    else:
        with open(os.path.join(folder_path, 'RAM_data', f'{frame_counter}.txt'), 'w') as f:
            f.write('')

    frame_counter += 1

if __name__ == '__main__':
    main()
