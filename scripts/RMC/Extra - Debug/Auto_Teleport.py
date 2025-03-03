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
LIST_OF_PARAM_ITERATOR : List of iterators. Must be the same length as LIST_OF_PARAM_EDITOR_FUNCTION.
            LIST_OF_PARAM_ITERATOR[i] must be an iterator of valid argument for the function LIST_OF_PARAM_EDITOR_FUNCTION[i]
            The script will iterate on all combinaison of possible valid arguments given by those iterators.
            The total amount of iteration of the script is the product of all iterators in LIST_OF_PARAM_ITERATOR
filter_attempt : Read the comment of the function to edit it.
'''
from dolphin import event, savestate 
from Modules.mkw_classes import VehiclePhysics
import Modules.mkw_utils as mkw_utils
from itertools import product

SAVEFILENAME = 'collect_data.csv'

TELEPORT_FRAME = 1858

LIST_OF_PARAM_EDITOR_FUNCTION = [lambda x : mkw_utils.player_teleport(0, x=x), #X position teleport function
                                 lambda y : mkw_utils.player_teleport(0, y=y), #Z position teleport function
                                 lambda z: mkw_utils.player_teleport(0, z=z)]#Yaw teleport function

def make_range(middle, radius, step):
    return iter(range(middle-radius, middle+radius, step))

LIST_OF_PARAM_ITERATOR = [make_range(14012, 20, 2),  
                          make_range(22482, 20, 2),
                          make_range(51857, 20, 2)]

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
        return str(cur_param)[1:-1]+'\n'
    else:
        return ''
    
def main():
    global save
    save = savestate.save_to_bytes()

    global savestring
    savestring = ''

    global params_iterator
    params_iterator = product(*LIST_OF_PARAM_ITERATOR)

    global cur_param
    cur_param = next(params_iterator)

    global end
    end = False

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
    global cur_param
    global end
    global iteration

    if not end:
            
        newframe = mkw_utils.frame_of_input() != frame
        frame = mkw_utils.frame_of_input()

        if newframe:
            save_str = filter_attempt()
            if not (save_str is None):
                savestring += save_str
                with open(SAVEFILENAME, 'w') as f:
                    f.write(savestring)
                try:
                    cur_param = next(params_iterator)
                    print('iteration_count', iteration)
                    iteration += 1
                    savestate.load_from_bytes(save)
                except StopIteration:
                    end = True
        
        if frame == TELEPORT_FRAME:
            print('current param', str(cur_param))
            for i in range(len(LIST_OF_PARAM_EDITOR_FUNCTION)):
                f = LIST_OF_PARAM_EDITOR_FUNCTION[i]
                arg = cur_param[i]
                f(arg)
    
    
