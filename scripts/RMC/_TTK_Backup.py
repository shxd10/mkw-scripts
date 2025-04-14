from dolphin import event, gui, utils, memory

import Modules.settings_utils as setting
import Modules.ttk_lib as ttk_lib
import Modules.mkw_translations as mkw_translations
from Modules.mkw_classes import RaceManager, RaceState

def main():
    global backup_count
    backup_count = 0
    
if __name__ == '__main__':
    main()


@event.on_beforesavestateload
def do_backup(_, __):
    global backup_count

    #test for https://blounard.s-ul.eu/1E62ITQK.png
    memory.read_u32(0x809B4242)
    #If you get the same error with the address above, it's
    #because of this script
    
    if RaceManager.state().value in [1,2]:      
        config = setting.get_ttk_config()
        backup_count += 1
        backup_count %= config.ttk_backup
        
        inputs = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER) 
        ttk_lib.write_to_backup_csv(inputs, backup_count)

