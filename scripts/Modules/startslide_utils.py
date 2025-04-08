from enum import Enum
from dolphin import event, gui, utils # type: ignore
from Modules import ttk_lib
from Modules.mkw_utils import frame_of_input
from Modules import mkw_translations as translate
from Modules.mkw_classes import RaceManager, RaceState
from Modules.framesequence import FrameSequence
import os

flame_slide_bikes = ("Flame Runner"),
mach_slide_bikes = ("Mach Bike", "Sugarscoot", "Zip Zip")
spear_slide_bikes = ("Jet Bubble", "Phantom", "Spear", "Sneakster")
wario_slide_bikes = ("Wario Bike")
wiggle_slide_bikes = ("Bit Bike", "Bullet Bike", "Dolphin Dasher", "Magikruiser",
                     "Quacker", "Shooting Star", "Standard Bike L", "Standard Bike M",
                     "Standard Bike S")

class Direction(Enum):
    RIGHT = "right"
    LEFT = "left"
    
def check_vehicle(vehicle: str):
    global direction
    path = utils.get_script_dir()

    if vehicle in flame_slide_bikes:
        return os.path.join(path, "Startslides", f"flame_{direction.value}.csv")

    elif vehicle in spear_slide_bikes:
        return os.path.join(path, "Startslides", f"spear_{direction.value}.csv")

    elif vehicle in mach_slide_bikes:
        return os.path.join(path, "Startslides", f"mach_{direction.value}.csv")

    elif vehicle in wario_slide_bikes:
        return os.path.join(path, "Startslides", f"wario_{direction.value}.csv")
    
    elif vehicle in wiggle_slide_bikes:
        return os.path.join(path, "Startslides", f"wiggle_{direction.value}.csv")

    else:  # Karts fall here. We take any slides, just for the startboost
        return os.path.join(path, "Startslides", f"spear_{direction.value}.csv")


def on_state_load(is_slot, slot):
    global player_inputs
    player_inputs = FrameSequence(check_vehicle(translate.vehicle_id()))
    player_inputs.read_from_file()

def on_frame_advance():
    frame = frame_of_input()
    stage = RaceManager.state()
    
    player_input = player_inputs[frame]
    if (player_input and stage.value == RaceState.COUNTDOWN.value):
        ttk_lib.write_player_inputs(player_input)


def execute_startslide(direction_: Direction):
    global direction
    direction = direction_

    global player_inputs
    player_inputs = FrameSequence(check_vehicle(translate.vehicle_id()))

    event.on_savestateload(on_state_load)
    event.on_frameadvance(on_frame_advance)
    
    gui.add_osd_message(f"Startslide: {len(player_inputs) > 0}")
