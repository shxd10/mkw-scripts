from dolphin import event, gui, utils
import configparser
import math
import os
from binascii import hexlify

from Modules.mkw_classes.common import SurfaceProperties, eulerAngle
from Modules.mkw_utils import History 

import Modules.settings_utils as setting
import Modules.mkw_utils as mkw_utils
from Modules.rkg_lib import get_RKG_data_memory, decode_RKG
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, TimerManager
from Modules.mkw_classes import RaceConfig, RaceConfigScenario, RaceConfigSettings
from Modules.mkw_classes import KartObject, KartMove, KartSettings, KartBody
from Modules.mkw_classes import VehicleDynamics, VehiclePhysics, KartBoost, KartJump
from Modules.mkw_classes import KartState, KartCollide, KartInput, RaceInputState




def main():
    global state
    state = RaceManager.state().value

if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global state

    if RaceManager.state().value == 4:
        if state != 5 :
            is_saved, rkg_data = get_RKG_data_memory()

            if is_saved:
                state = 5
                course_id = RaceConfigSettings(RaceConfigScenario(RaceConfig.race_scenario()).settings()).course_id()
                metadata, inputList, mii_data = decode_RKG(rkg_data)
                crc_string = str(hexlify(rkg_data[-4:]))[2:-2]
                ft_string = f'_{metadata.finish_time:.3f}s_'
                filename = os.path.join(utils.get_script_dir(), 'Ghost', 'AutoSave', course_id.name+ft_string+crc_string+'.rkg')
                with open(filename, 'wb') as f:
                    f.write(rkg_data)
                gui.add_osd_message("Ghost saved to "+filename)
            else:
                state = 4
    else:
        state = RaceManager.state().value
            

