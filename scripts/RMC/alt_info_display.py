"""
EPIK95
An alternative infodisplay that I made for personal use. The text that gets displayed is created in one large
formatted string, which makes it very easy to modify or add to the display directly instead of using a config file.
Setting EXTERNAL_MODE to True will render the display in a separate window (requires Python to be installed).
Setting GHOST_DISPLAY to True will render a second copy of the display with values for the ghost.
If "Remove UI Delay" is enabled in Dolphin's graphics settings, set NO_DELAY to True to prevent flickering.
"""
from dolphin import event, gui, utils, memory # type: ignore
import os
from Modules import mkw_classes as mkw, mkw_utils
from external import external_utils as ex

EXTERNAL_MODE = False
NO_DELAY = True
GHOST_DISPLAY = False

ROUND_DIGITS = 6
TEXT_COLOR = 0xFFFFFFFF

def round_(x, digits=ROUND_DIGITS):
    return round(x or 0, digits)

def round_str(x, digits=ROUND_DIGITS):
    rounded = round_(x, digits)
    return f"{rounded:.{digits}f}"

def delta(current, previous):
    if previous is None:
        return "+?"
    res = round_(current - previous, ROUND_DIGITS)
    return ("+" if res > 0 else "") + round_str(res)


def create_infodisplay(player_idx: int = 0):
    # Instantiate classes
    race_mgr_player = mkw.RaceManagerPlayer(player_idx)
    race_scenario = mkw.RaceConfigScenario(addr=mkw.RaceConfig.race_scenario())

    if player_idx >= race_scenario.player_count():
        return "[invalid player index]"
    
    race_settings = mkw.RaceConfigSettings(race_scenario.settings())
    kart_object = mkw.KartObject(player_idx)
    kart_move = mkw.KartMove(addr=kart_object.kart_move())
    kart_boost = mkw.KartBoost(addr=kart_move.kart_boost())
    kart_jump = mkw.KartJump(addr=kart_move.kart_jump())
    kart_state = mkw.KartState(addr=kart_object.kart_state())
    kart_collide = mkw.KartCollide(addr=kart_object.kart_collide())
    kart_body = mkw.KartBody(addr=kart_object.kart_body())
    vehicle_dynamics = mkw.VehicleDynamics(addr=kart_body.vehicle_dynamics())
    vehicle_physics = mkw.VehiclePhysics(addr=vehicle_dynamics.vehicle_physics())

    pos = vehicle_physics.position()
    v = mkw_utils.delta_position(player_idx)
    ev = vehicle_physics.external_velocity()
    facing_angle = mkw_utils.get_facing_angle(player=0)

    is_bike = mkw.KartSettings.is_bike(player_idx)
    surface_properties = kart_collide.surface_properties().value

    # Create infodisplay text
    text = (

f"""
Frame: {mkw_utils.frame_of_input()}

Position
  X: {round_str(pos.x)}
  Y: {round_str(pos.y)}
  Z: {round_str(pos.z)}

Velocity
  Engine:  {round_str(kart_move.speed())} / {round_str(kart_move.soft_speed_limit(), 2)}
  XYZ:     {round_str(v.length())}
  XZ:      {round_str(v.length_xz())}
  Y:       {round_str(v.y)}

External Velocity
  XYZ:  {round_str(ev.length())}  ({delta(ev.length(), prev_values[player_idx].get("ev_xyz"))})
  XZ:   {round_str(ev.length_xz())}  ({delta(ev.length_xz(), prev_values[player_idx].get("ev_xz"))})
  Y:    {round_str(ev.y)}  ({delta(ev.y, prev_values[player_idx].get("ev_y"))})

Lean Rotation
  Angle:  {is_bike and round_(kart_move.lean_rot())}
  Rate:   {is_bike and round_(kart_move.lean_rot_increase())}
  Cap:    {is_bike and round_(kart_move.lean_rot_cap())}

Boosts
  MT: {kart_move.mt_charge()} / 270 -> {kart_move.mt_boost_timer()}
  SSMT: {kart_move.ssmt_charge()} / 75 -> {kart_boost.all_mt_timer() - kart_move.mt_boost_timer()}
  Mushroom: {kart_move.mushroom_timer()} | Trick: {kart_boost.trick_and_zipper_timer()}
  Auto Drift: {kart_move.auto_drift_start_frame_counter()} / 12

Checkpoints
  Lap%:  {round_str(race_mgr_player.lap_completion())}
  Race%: {round_str(race_mgr_player.race_completion())}
  CP: {race_mgr_player.checkpoint_id()} | KCP: {race_mgr_player.max_kcp()} | RP: {race_mgr_player.respawn()}

Airtime: {kart_move.airtime()}
Wallhug: {(surface_properties & mkw.SurfaceProperties.WALL) > 0}
Barrel Roll: {kart_state.bitfield(field_idx=3) & 0x10 > 0}

Surface properties: {surface_properties}
""")

    #? Other infodisplay sections that can be copy/pasted in if needed
    _unused = (

"""
HWG Timer: {kart_state.hwg_timer()}
Glitchy corner: {round_(kart_collide.glitchy_corner())}

Cooldowns
  Wheelie: {kart_move.wheelie_cooldown()} | Trick: {kart_jump.cooldown()}

Offroad: {(surface_properties & mkw.SurfaceProperties.OFFROAD) > 0}
OOB Timer: {kart_collide.solid_oob_timer()}

  Forward:  {round_str(v.forward(facing_angle.yaw))}
  Sideways: {round_str(v.sideway(facing_angle.yaw))}

Boost Panel: {kart_boost.mushroom_and_boost_panel_timer() - kart_move.mushroom_timer()}

Airtime: {(kart_move.airtime() + 1) if (surface_properties & 0x1000) == 0 else 0}
""")

    # Store any values that will be needed on the next frame
    prev_values[player_idx].update({
        "ev_xyz": ev.length(),
        "ev_xz": ev.length_xz(),
        "ev_y": ev.y,
    })

    return text.strip()


def update_infodisplay():
    global text_0, text_1
    
    if EXTERNAL_MODE:
        shm_writer.write_text(create_infodisplay())
    else:
        text_0 = create_infodisplay(player_idx=0)
        if GHOST_DISPLAY:
            text_1 = create_infodisplay(player_idx=1)


@event.on_framepresent
def on_present():
    if not EXTERNAL_MODE:
        gui.draw_text((10, 10), TEXT_COLOR, text_0)
        if GHOST_DISPLAY:
            gui.draw_text((260, 10), TEXT_COLOR, text_1)

    
@event.on_frameadvance
def on_frame_advance():
    global current_frame
    if current_frame != (mkw_utils.frame_of_input() - 1):
        for p in prev_values:
            p.clear()
    current_frame = mkw_utils.frame_of_input()

    if mkw_utils.extended_race_state() >= 0:
        update_infodisplay()


@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    if memory.is_memory_accessible() and mkw_utils.extended_race_state() >= 0:
        update_infodisplay()

def main():
    global current_frame
    current_frame = 0

    global prev_values
    prev_values = [ {}, {} ]

    global text_0 #text for player id 0
    text_0 = ''

    global text_1 #text for player id 1
    text_1 = ''

    if EXTERNAL_MODE:
        global shm_writer
        shm_writer = ex.SharedMemoryWriter(name='infodisplay', buffer_size=4096)

        window_script_path = os.path.join(utils.get_script_dir(), "external", "info_display_window.py")
        ex.start_external_script(window_script_path)


if __name__ == '__main__':
    main()
