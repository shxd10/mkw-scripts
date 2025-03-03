'''
Start the script on the savestate frame !
To use this script : You have to edit : SAVEFILENAME, TELEPORT_FRAME, LIST_OF_PARAM_EDITOR_FUNCTION,
LIST_OF_PARAM_ITERATOR, filter_attempt.
SAVEFILENAME : filename for the file you will save results in
TELEPORT_FRAME : frame you want the memory edits to happen (usually a teleportation)
LIST_OF_PARAM_EDITOR_FUNCTION : List of functions that will perform a memory edit when you get to TELEPORT_FRAME
            Those functions MUST take only 1 argument, which is generally value of the memory edit desired.
                Example : lambda x : mkw_utils.player_teleport(0, x=x) is a function that take an argument x, and teleport to the corresponding x position
            You can get more fancy, and use this to modify other parameters, like the external velocity
BASE_LIST : The first arguments of the functions in LIST_OF_PARAM_EDITOR_FUNCTION that will be tried
STEP_LIST : The steps you will take when looking for nearby arguments for LIST_OF_PARAM_EDITOR_FUNCTION
MAX_LIST : Put a maximum value for each argument of LIST_OF_PARAM_EDITOR_FUNCTION
    You can use None for no max value
MIN_LIST : same but minimum value
filter_attempt : Read the comment of the function to edit it.
'''
from dolphin import event, savestate, utils 
from Modules.mkw_classes import VehiclePhysics
import Modules.mkw_utils as mkw_utils
from itertools import product
from collections import deque

SAVEFILENAME = 'collect_data.csv'

TELEPORT_FRAME = 1858

LIST_OF_PARAM_EDITOR_FUNCTION = [lambda x : mkw_utils.player_teleport(0, x=x), #X position teleport function
                                 lambda y : mkw_utils.player_teleport(0, y=y), #Z position teleport function
                                 lambda z: mkw_utils.player_teleport(0, z=z)]#Yaw teleport function


BASE_LIST = [14012, 22600, 51857]

STEP_LIST = [1, 0, 1]

MAX_LIST = [None, None, None]

MIN_LIST = [None, None, None]

def filter_attempt():
    ''' This function has to return the string corresponding to the data you want to save
        from the current attempt. Generally, you want atleast cur_param, and eventually more data
        You can return an empty string if you don't want to save anything from the current attempt
        If you want the current attempt to keep going, YOU HAVE TO RETURN NONE
        This function is called on every newframe, so you can store data with some mkw_utils.History for more complex data to save for example'''
    
    frame = mkw_utils.frame_of_input()
    if frame < 1900 :
        return None
    if VehiclePhysics.position(0).x > 15000: 
        return str(tuple([cur_coordinate[i] * STEP_LIST[i] + BASE_LIST[i] for i in range(DEPTH)]))[1:-1]+'\n'
    else:
        return ''
    
def main():
    global DEPTH
    DEPTH = len(BASE_LIST)
    
    global save
    save = savestate.save_to_bytes()

    global savestring
    savestring = ''

    global waiting_list
    waiting_list = deque()
    waiting_list.append(tuple([0]*DEPTH))

    global visited_dict
    visited_dict = {}
    visited_dict[tuple([0]*DEPTH)] = True

    global end
    end = False

    global cur_coordinate
    cur_coordinate = tuple([0]*DEPTH)
    
    global iteration
    iteration = 1

    global frame
    frame = mkw_utils.frame_of_input()
    
if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global frame
    global params_iterator
    global save
    global savestring
    global cur_coordinate
    global end
    global iteration
    global waiting_list
    global visited_dict

    if not end:
            
        newframe = mkw_utils.frame_of_input() != frame
        frame = mkw_utils.frame_of_input()

        if newframe:
            save_str = filter_attempt()
            if not (save_str is None):
                savestring += save_str
                with open(SAVEFILENAME, 'w') as f:
                    f.write(savestring)
                if save_str != '':
                    for change in product((-1,0,1), repeat = DEPTH):
                        new_coordinate = tuple([cur_coordinate[i] + change[i]*int(STEP_LIST[i] != 0) for i in range(DEPTH)])
                        if not (new_coordinate in visited_dict.keys()):
                            #todo : check if new_coordinate doesn't go outside min and max
                            visited_dict[new_coordinate] = True
                            waiting_list.append(new_coordinate)
                            print('new coordinate added') 
                if waiting_list:
                    cur_coordinate = waiting_list.popleft()
                    print('wait list size:', len(waiting_list))
                    savestate.load_from_bytes(save)
                else:
                    end = True
                    utils.toggle_play() 
                
        
        if newframe and frame == TELEPORT_FRAME:
            print('current param', str(cur_coordinate))
            for i in range(DEPTH):
                f = LIST_OF_PARAM_EDITOR_FUNCTION[i]
                arg = cur_coordinate[i] * STEP_LIST[i] + BASE_LIST[i]
                f(arg)
    
    
