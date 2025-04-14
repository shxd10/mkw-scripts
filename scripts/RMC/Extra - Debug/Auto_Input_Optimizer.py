'''
This script can automatically modify inputs, with random input generation.
It is used to optimize some part of a TAS.
-You have to MANUALLY tell the script which function it need to maximize
    by modifying the function 'calculate_score'.
    Example : maximize the RaceCompletion of the player by frame 4242.
    some example are coded in bruteforcer_lib.py
-You have to MANUALLY tell the script which random modification it can do
    on your inputs. This is done with a list of "Randomizer" instance (class from bruteforcer_lib.py)
    Typically those instances can do 1 random modification to a FrameSequence at a time.
    the global variable randlist, definied in main(), is a list of all those Randomizer instance you
    want to apply on each try.

Currently, this script ALWAYS save an improvement, and NEVER saves a slower attempt.
this might change in the future, with a monte carlo approach.

THIS SCRIPT USES SAVESTATE SLOT 4
'''
from dolphin import event, savestate, utils
from Modules import ttk_lib
import Modules.mkw_utils as mkw_utils
from Modules.framesequence import FrameSequence, Frame
from Modules.bruteforcer_lib import Randomizer, score_racecomp, score_XZ_EV
import random
import os




def calculate_score():
    ''' This function has to return a score corresponding to what you want to optimize
        from the current attempt. 
        If you want the current attempt to keep going, YOU HAVE TO RETURN NONE
        This function is called on every newframe, so you can store data with
        some mkw_utils.History for more complex data to calculate score for example'''
    
    return score_racecomp(4242)()
    
def main():

    global randlist
    randlist = []
    for frame in range(3265, 3600):
        randlist.append(Randomizer(5, frame, 1/100, 15))

    global highscore
    highscore = None

    global cur_csv
    cur_csv = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)

    global best_csv
    best_csv = cur_csv

    global attempt_counter
    attempt_counter = 0

    savestate.load_from_slot(4)


@event.on_frameadvance
def on_frame_advance():
    global best_csv
    global cur_csv
    global attempt_counter
    global highscore

    if True:
        frame = mkw_utils.frame_of_input()

        if True:
            score = calculate_score()
            if not (score is None):
                if (highscore is None) or (score > highscore):
                    attempt_counter = 0
                    highscore = score
                    best_csv = cur_csv
                    savefilename = os.path.join(utils.get_script_dir(), "Input_optimizer", f"{highscore}.csv")
                    if best_csv.write_to_file(savefilename):
                        print(f"saved to {savefilename}")
                    else:
                        print('error with saving')
                cur_csv = best_csv.copy()
                for rand in randlist:
                    rand.random(cur_csv)
                attempt_counter+= 1
                print(f"random attempt since last improvement : {attempt_counter}")
                savestate.load_from_slot(4)
                
    
@event.on_framebegin
def on_frame_begin():
    frame = mkw_utils.frame_of_input()
    
    player_input = cur_csv[frame]
    if player_input:
        ttk_lib.write_player_inputs(player_input)
        
if __name__ == '__main__':
    main()
