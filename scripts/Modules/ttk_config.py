from . import mkw_translations
from Modules import settings_utils as setting

# when running undo_state_backup.py, creates up to backup_amount
# backup files for your race inputs while you are TASing
backup_amount = 10

# csvs that player and ghost inputs will be written to must be tucked
# inside a function because we want to support the course changing
def text_file_path(path_name: str) -> str:
    ttk_settings = setting.get_ttk_config()

    if ttk_settings.track_suffix:    
        course = '_' + mkw_translations.course_slot_abbreviation()
    else:
        course = mkw_translations.course_slot_abbreviation()
    
    text_file_paths = {
        "Player": f"MKW_Inputs/{course}/{ttk_settings.player_filename}.csv",
        "Ghost": f"MKW_Inputs/{course}/{ttk_settings.ghost_filename}.csv",
        "Backup": f"MKW_Inputs/{course}/Backups/backup##.csv"
        #"Player": "MKW_Inputs/" + ttk_settings.player_filename + course + ".csv",
        #"Ghost": "MKW_Inputs/" + ttk_settings.ghost_filename + course + ".csv",
        #"Backup": "MKW_Inputs/Backups/" "ttk_backup##" + course +".csv"
    }
    
    return text_file_paths[path_name]

# rkgs that player and ghost inputs will be written to
course = mkw_translations.course_slot_abbreviation()
ttk_settings = setting.get_ttk_config()
rkg_file_path = {
    "Player": f"MKW_Inputs/{course}/{ttk_settings.player_filename}.rkg",
    "Ghost": f"MKW_Inputs/{course}/{ttk_settings.ghost_filename}.rkg",
    #"Player": "MKW_Inputs/MKW_Player_Inputs_" + course + ".rkg",
    #"Ghost": "MKW_Inputs/MKW_Ghost_Inputs_" + course + ".rkg"
}