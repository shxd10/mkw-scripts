from dolphin import controller, event, savestate

from Modules import ttk_lib
from Modules.framesequence import FrameSequence, Frame
from Modules import mkw_utils as mkw_utils
from Modules.mkw_classes import RaceManagerPlayer, VehiclePhysics
import random
import os

def save(name):
    b = savestate.save_to_bytes()
    f = open(name, 'wb')
    f.write(b)
    f.close()
    
def load(name):
    f = open(name, 'rb')
    b = f.read()
    f.close()
    savestate.load_from_bytes(b)

def prevframe(frame, frequency):
    return frame-1 - (frame-2)%frequency


class Input:
    def __init__(self, A, B=None, L=None, H=None, V=None, D=None):
        if B is None:
            if type(A) == int:
                r = A
                self.A = r%2 == 1
                r= r//2
                self.B = r%2 == 1
                r= r//2
                self.L = r%2 == 1
                r= r//2
                self.H = r%15
                r= r//15
                self.V = r%15
                r= r//15
                self.D = r%5
            else :
                raise TypeError("When calling Input(i) with 1 argument, i must be int")
        else :
            self.A = A
            self.B = B
            self.L = L
            self.H = H
            self.V = V
            self.D = D

    def __int__(self):
        r = 0
        r+= int(self.A)
        r+= int(self.B)*2
        r+= int(self.L)*4
        r+= int(self.H)*8
        r+= int(self.V)*120
        r+= int(self.D)*1800
        return r

    def __str__(self):
        return f"{str(self.A)}, {str(self.B)}, {str(self.L)}, {str(self.H)}, {str(self.V)}, {str(self.D)}"


class InputIterable:
    def __init__(self, iterable, rule=None):
        if rule is None:
            rule = lambda x : True
        self.rule = rule
        try:
            inp = next(iterable)
            while not rule(inp):
                inp = next(iterable)
            self.val = inp
            self.iterator = iterable
        except StopIteration:
            self.val = None
            self.iterator = iterable
            print("Tried to Init a InputIterable with iterator not letting any rule(value)")

    def __next__(self):
        self.val = next(self.iterator)
        while not self.rule(self.val):
            self.val = next(self.iterator)
    
    

    

class InputList:
    """Class for List of InputRuled iterator
        Accessing with an index not in the list will create a new InputRuled iterator
        InputList[frame] should be an Input
        InputList.inputlist[frame] is an InputIterable
        ruleset must be a function : int -> rule
            rule type is a function : Input -> bool
        iterset must be a function : int -> itergen
            itergen type is a function : list(Input) -> Iter(Input) """
    def __init__(self, ruleset, iterset):
        self.inputlist = {}
        self.ruleset = ruleset
        self.iterset = iterset
        
    def __getitem__(self, index):
        if not index in list(self.inputlist.keys()):
            if index>0:                   
                iterable = self.iterset(index)([self[index-1]])
                self.inputlist[index] = InputIterable(iterable, self.ruleset(index))
            else:
                iterable = self.iterset(index)([])
                self.inputlist[index] = InputIterable(iterable, self.ruleset(index))                
        return self.inputlist[index].val

    def __str__(self):
        return str([int(self[i]) for i in range(10)])

    def update(self,frame):
        """Update the list.
            Return the frame of last modification"""
        if frame<0:
            raise ValueError('Tried to update a InputList with from a negative frame')
        self[frame]
        self[frame+1]
        self[frame+2]
        del self.inputlist[frame+1]
        del self.inputlist[frame+2]
        try:
            next(self.inputlist[frame])
            return frame
        except StopIteration:
            del self.inputlist[frame]
            return self.update(frame-1)

def first_input_ruled(rule):
    for i in range(9000):
        if rule(i):
            return Input(i)

def last_input_ruled(rule):
    for i in range(8999, -1, -1):
        if rule(i):
            return Input(i)


def simple_order_iterator(l):
    for i in range(9000):
        yield Input(i)

def last_input_iterator(l):
    j = 0
    if len(l)>0:
        j = int(l[0])
    for i in range(9000):
        yield Input((i+j)%9000)

def _123rule(inp):
    return int(inp)<4

def basic_rule(inp):
    #Rule for 3 possible inputs : Gi straight, turn left, turn right
    return inp.A and (not inp.B) and (not inp.L) and (inp.H in [0,7,14]) and (inp.V==7) and (inp.D==0)
def forward_rule(inp):
    #Rule for 1 possible input : Press A.
    return inp.A and (not inp.B) and (not inp.L) and (inp.H ==7) and (inp.V==7) and (inp.D==0)

forward = Input(True, False, False, 7, 7, 0)
ruleset123 = lambda x : _123rule

itersetconst = lambda x : simple_order_iterator

big = InputList(ruleset123, itersetconst)

def run_input(inp):
    gc_input = {}
    #trick input
    gc_input['Left'] = inp.D==3
    gc_input['Right'] = inp.D==4
    gc_input['Up'] = inp.D==1
    gc_input['Down'] = inp.D==2

    #button input
    gc_input['A'] = inp.A
    gc_input['B'] = inp.B
    gc_input['L'] = inp.L

    #stick input
    match = {0 : 59,
             1 : 68,
             2 : 77,
             3 : 86,
             4 : 95,
             5 : 104,
             6 : 112,
             7 : 128,
             8 : 152,
             9 : 161,
             10 : 170,
             11 : 179,
             12 : 188,
             13 : 197,
             14 : 205}
    gc_input['StickX'] = match[inp.H]
    gc_input['StickY'] = match[inp.V]

    #Everything else, irrelevant
    gc_input['Z'] = False
    gc_input['R'] = False
    gc_input['X'] = False
    gc_input['Y'] = False
    gc_input['Start'] = False
    gc_input['CStickX'] = 0
    gc_input['CStickY'] = 0
    gc_input['TriggerLeft'] = 0
    gc_input['TriggerRight'] = 0
    gc_input['AnalogA'] = 0
    gc_input['AnalogB'] = 0
    gc_input['Connected'] = True

    controller.set_gc_buttons(0, gc_input)

def makeFrame(inp):
    f = Frame([str(int(i)) for i in [inp.A, inp.B, inp.L, inp.H-7, inp.V-7, inp.D]])
    return f

def run_input2(inp):
    f = makeFrame(inp)
    ttk_lib.write_player_inputs(f)


class Randomizer_Raw_Stick:
    ''' Class for making random modification to a FrameSequence
        Only modify 1 stick input at a time
        
        direction : either horizontal or vertical
        frame is the frame of input you want to randomize
        probability is the probability of a random modification actually happenning when calling the random method
        modif_range is the max amplitude of the modification.
            example with 2, you can only change a +4 stick input to {+2, +3, +4, +5, +6}'''
    def __init__(self, direction, frame, probability = 0.1, modif_range = 15):
        self.direction = direction
        self.proba = probability
        self.range = modif_range
        self.frame = frame

    def random(self, inputList : FrameSequence):
        '''THIS FUNCTION MODIFIES inputList'''
        if self.frame < len(inputList.frames):
            if random.random() < self.proba:
                baseFrame = inputList.frames[self.frame]
                if self.direction in ["X", "x", "horizontal"]:
                    baseFrame.stick_x = random.randint(max(-7, baseFrame.stick_x - self.range), min(7, baseFrame.stick_x + self.range))
                elif self.direction in ["Y", "y", "vertical"]:
                    baseFrame.stick_y = random.randint(max(-7, baseFrame.stick_y - self.range), min(7, baseFrame.stick_y + self.range))
                else:
                    raise IndexError(f'Index {self.direction} is not supported yet')

class Randomizer_Alternate_Stick:
    ''' Class for making random modification to a FrameSequence
        Modify 2 consecutive inputs with +d/-d
        Example :  +5, -3 -> +4, -2.

        direction : either horizontal or vertical
        frame is the frame of input you want to randomize
        probability is the probability of a random modification actually happenning when calling the random method
        modif_range is the max amplitude of the modification.
            example with 2, you can only change a +4 stick input to {+2, +3, +4, +5, +6}
        '''
    
    def __init__(self, direction, frame, probability = 0.1, modif_range = 15):
        self.direction = direction
        self.proba = probability
        self.range = modif_range
        self.frame = frame

    def random(self, inputList : FrameSequence):
        '''THIS FUNCTION MODIFIES inputList'''
        if self.frame + 1 < len(inputList.frames):
            if random.random() < self.proba:
                baseFrame1 = inputList.frames[self.frame]
                baseFrame2 = inputList.frames[self.frame+1]
                shift = random.randint(1, self.range)
                sign = random.randint(0,1)*2 -1 #either -1 or 1
                if self.direction in ["X", "x", "horizontal"]:
                    if sign == 1:
                        max1 = 7 - baseFrame1.stick_x
                        max2 = 7 + baseFrame2.stick_x
                    else:
                        max1 = 7 + baseFrame1.stick_x
                        max2 = 7 - baseFrame2.stick_x
                    max_all = min(max1, max2, shift)
                    baseFrame1.stick_x = baseFrame1.stick_x + sign * max_all
                    baseFrame2.stick_x = baseFrame2.stick_x - sign * max_all
                elif self.direction in ["Y", "y", "vertical"]:
                    if sign == 1:
                        max1 = 7 - baseFrame1.stick_y
                        max2 = 7 + baseFrame2.stick_y
                    else:
                        max1 = 7 + baseFrame1.stick_y
                        max2 = 7 - baseFrame2.stick_y
                    max_all = min(max1, max2, shift)
                    baseFrame1.stick_y = baseFrame1.stick_y + sign * max_all
                    baseFrame2.stick_y = baseFrame2.stick_y - sign * max_all
                else:
                    raise IndexError(f'Index {self.direction} is not supported yet')

                
def score_racecomp(frame_limit):
    def res():
        frame = mkw_utils.frame_of_input()
        if frame < frame_limit :
            return None
        return RaceManagerPlayer(0).race_completion()
    return res

def score_XZ_EV(frame_limit):
    def res():
        frame = mkw_utils.frame_of_input()
        if frame < frame_limit :
            return None
        return VehiclePhysics(0).external_velocity().length_xz()
    return res

def score_Z_position(frame_limit, negative=False):
    def res():
        frame = mkw_utils.frame_of_input()
        if frame < frame_limit :
            return None
        return VehiclePhysics(0).position().z * -1 if negative else 1
    return res
