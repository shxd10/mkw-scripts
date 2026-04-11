from dolphin import event, gui
import Modules.mkw_classes as mkw
import Modules.mkw_utils as utils

def is_null_input(i):
	return (i[0] == 0) and (i[1] == 0) and (i[2] == 0) and (i[3] == 7) and (i[4] == 7) and (i[5] == 0) and (i[6] == 0)

def update_boost():
	return (utils.get_boost_flag(), utils.get_offroad_immunity_flag())

def is_boosting(prev_boost):
	cur_boost = update_boost()
	return (prev_boost[0] == 1) or (prev_boost[1] == 1)

def main():
    global boost_timer_list
    boost_timer_list = update_boost()

    global frame
    frame = utils.frame_of_input()

if __name__ == '__main__':
    main()

@event.on_frameadvance
def on_frame_advance():
    global boost_timer_list
    global frame

    if utils.frame_of_input() == frame+1:
        if utils.extended_race_state() > 0:
            if (frame+1) > 240:
                if (not is_null_input(utils.get_current_input_state())) and (not is_boosting(boost_timer_list)):
                    gui.add_osd_message(f"Detected non-null inputs outside a boost on frame {frame+1}!")
        boost_timer_list = update_boost()
    frame = utils.frame_of_input()