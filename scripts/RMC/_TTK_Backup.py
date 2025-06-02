from dolphin import event, gui, utils, memory

from Modules import settings_utils as setting
from Modules import ttk_lib as ttk_lib
from Modules import mkw_translations as mkw_translations
from Modules.mkw_classes import RaceManager, RaceState

def main():
    global backup_count
    backup_count = 0
    
if __name__ == '__main__':
    main()


@event.on_beforesavestateload
def do_backup(_, __):
    global backup_count
    
    
    if memory.is_memory_accessible() and RaceManager.state().value in [1,2]:      
        config = setting.get_ttk_config()
        backup_count += 1
        backup_count %= config.ttk_backup
        
        inputs = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER) 
        ttk_lib.write_to_backup_csv(inputs, backup_count)

