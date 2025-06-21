from dolphin import memory, utils, event
from collections import deque

from .mkw_classes import mat34, quatf, vec3, ExactTimer, eulerAngle
from .mkw_classes import VehicleDynamics, VehiclePhysics, RaceManagerPlayer, KartObjectManager, RaceManager, RaceState

import math

# These are helper functions that don't quite fit in common.py
# This file also contains getter functions for a few global variables.

# NOTE (xi): wait for get_game_id() to be put in dolphin.memory before clearing
#  these commented-out lines:

fps_const = 59.94 #Constant for fps in mkw (59.94fps)


class History:
    ''' Class for storing each frame some data
        get_data_dict must be a dict of functions that return the desired data
        the functions must be able to take 0 arguments  (Maybe if needed i'll implement an argument dict, for the argument of the corresponding functions
        
        Example : {'position' : VehiclePhysics.position,
                    'rotation'  : VehiclePhysics.main_rotation}
        data is a list containing dict of data corresponding
        data[0] contain the latest added frame'''
    
    def __init__(self, get_data_dict, max_size):
        self.max_size = max_size
        self.get_data = get_data_dict
        self.data = deque()

    def update(self):
        if len(self.data) >= self.max_size:
            self.data.pop()
        cur_frame_dict = {}
        for key in self.get_data.keys():
            cur_frame_dict[key] = self.get_data[key]()
        self.data.appendleft(cur_frame_dict)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def clear(self):
        self.data.clear()
        
    def __bool__(self):
        return bool(self.data)

    def __iter__(self):
        return iter(self.data)
    
def chase_pointer(base_address, offsets, data_type):
    """This is a helper function to allow multiple ptr dereferences in
       quick succession. base_address is dereferenced first, and then
       offsets are applied. Then, the appropriate function based off data_type
       is called with the resulting dereferences + the final offset."""
    current_address = memory.read_u32(base_address)
    for offset in offsets:
        value_address = current_address + offset
        current_address = memory.read_u32(current_address + offset)
    data_types = {
        'u8': memory.read_u8,
        'u16': memory.read_u16,
        'u32': memory.read_u32,
        'u64': memory.read_u64,
        's8': memory.read_s8,
        's16': memory.read_s16,
        's32': memory.read_s32,
        's64': memory.read_s64,
        'f32': memory.read_f32,
        'f64': memory.read_f64,
        'vec3': vec3.read,
        'mat34': mat34.read,
        'quatf': quatf.read,
    }
    return data_types[data_type](value_address)


def frame_of_input():
    id = utils.get_game_id()
    address = {"RMCE01": 0x809BF0B8, "RMCP01": 0x809C38C0,
               "RMCJ01": 0x809C2920, "RMCK01": 0x809B1F00}
    return memory.read_u32(address[id])

def extended_race_state():
    ''' Return an extended RaceState.
    -1 <-> Not in a race
    0  <-> Intro Camera
    1  <-> Countdown
    2  <-> In the race
    3  <-> Race over (waiting for other to finish)
    4  <-> Race over (everyone is finished)
    5  <-> Race over and ghost saved'''
    if KartObjectManager.player_count()==0:
        return -1
    else:
        race_mgr = RaceManager()
        state = race_mgr.state().value
        if state < 4:
            return state
        else:
            try:
                region = utils.get_game_id()
                address = {"RMCE01": 0x809B8F88, "RMCP01": 0x809BD748,
                        "RMCJ01": 0x809BC7A8, "RMCK01": 0x809ABD88}
                rkg_addr = chase_pointer(address[region], [0x18], 'u32')
            except KeyError:
                raise RegionError
            if memory.read_u32(rkg_addr) == 0x524b4744 :
                return 5
            else:
                return 4
            
def delta_position(playerIdx=0):
    dynamics_ref = VehicleDynamics(playerIdx)
    physics_ref = VehiclePhysics(addr=dynamics_ref.vehicle_physics())

    return physics_ref.position() - dynamics_ref.position()

def is_single_player():
    return KartObjectManager().player_count() == 1

# Next 3 functions are used for exact finish display

def get_igt(lap, player):
    if player == 0:
        address = 0x800001B0
    elif player == 1:
        address = 0x800001F8
    else:
        return ExactTimer(0, 0, 0)
    
    race_manager_player_inst = RaceManagerPlayer(player)
    timer_inst = race_manager_player_inst.lap_finish_time(lap-1)
    mins = timer_inst.minutes()
    secs = timer_inst.seconds()
    mils = memory.read_f32(address + (lap-1)*0x4) / 1000 % 1
    return ExactTimer(mins, secs, mils)

def update_exact_finish(lap, player):
    currentLapTime = get_igt(lap, player)
    if lap > 1:
        pastLapTime = get_igt(lap-1, player)
    else:
        pastLapTime = ExactTimer(0, 0, 0.0)

    return currentLapTime - pastLapTime

def get_unrounded_time(lap, player):
    t = ExactTimer(0, 0, 0)
    for i in range(lap):
        t += update_exact_finish(i + 1, player)
    return t

def calculate_exact_finish(positions, lap):
    '''
    Calculate the exact finish time, assuming this
    function is called the 1st frame you cross the line.
    Store it to EVA at 0x800002E0 + lap*0x4 as a 4bytes float.
    '''
    if len(positions) < 3:
        return 0
    prevPos = positions[2]['pos']
    pos = positions[1]['pos']
    fl1, fl2 = get_finish_line_coordinate()
    t = time_to_cross(prevPos, pos-prevPos, fl1, fl2)
    if not (0<= t <= 1):
        #Error detected. We write a default value instead
        address = 0x800002E0 + lap*0x4
        print('Error in Exact Finish Time')
        memory.write_f32(address, 999.999999)
    else:
        exact_finish = (frame_of_input()+t-241)/fps_const
        address = 0x800002E0 + lap*0x4
        memory.write_f32(address, exact_finish)

def read_exact_finish(lap):
    #Read exact finish from EVA, stored with above function
    address = 0x800002E0 + lap*0x4
    return memory.read_f32(address)


def calculate_extra_finish_data(exact_finish):
    '''
    This function returns how much exact finish time
    you need to gain a rounded millisecond, and
    you need to lose a rounded millisecond
    Return in MICROSECONDS
    '''
    t = (exact_finish*fps_const)%1
    frame_count = math.floor(exact_finish*fps_const)
    
    frame_rounded_ms = math.floor(frame_count/fps_const*1000)
    subframe_rounded_ms = math.ceil(t/fps_const*1000)
    
    if subframe_rounded_ms < 17:
        exact_ahead = subframe_rounded_ms/1000*fps_const - t #time in frames needed for gaining 1ms
    else:
        exact_ahead = 1-t - (math.floor((frame_count+1)/fps_const*1000) - frame_rounded_ms - 17)/1000*fps_const
        
    if subframe_rounded_ms > 1 :
        exact_behind = (subframe_rounded_ms-1)/1000*fps_const - t #time in frames needed for losing 1ms
    else:
        exact_behind = -t - (math.floor((frame_count-1)/fps_const*1000) - frame_rounded_ms + 17)/1000*fps_const
        
    return (round(exact_ahead/fps_const*1000000), round(exact_behind/fps_const*1000000))

#Rotation display helper functions
def quaternion_to_euler_angle(q):
    """Param : quatf
        Return : eulerAngle """
    x1, x2 = 2*q.x*q.w-2*q.y*q.z, 1-2*q.x*q.x-2*q.z*q.z
    y1, y2 = 2*q.y*q.w-2*q.x*q.z, 1-2*q.y*q.y-2*q.z*q.z
    z = 2*q.x*q.y + 2*q.z*q.w
    roll = 180/math.pi * math.asin(z)
    pitch = -180/math.pi * math.atan2(x1, x2)
    yaw = -180/math.pi * math.atan2(y1, y2)
    return eulerAngle(pitch, yaw, roll)

def get_facing_angle(player = 0):
    """Param : int player_id
        Return : eulerAngle , correspond to facing angles"""
    quaternion = VehiclePhysics(player).main_rotation()
    return quaternion_to_euler_angle(quaternion)

def speed_to_euler_angle(speed):
    """Param : vec3 speed
        Return : eulerAngle"""
    s = speed
    pitch = 180/math.pi * math.atan2(s.z, s.y) #unsure and unused
    yaw = -180/math.pi * math.atan2(s.x, s.z)
    roll = -180/math.pi * math.atan2(s.y, s.x)#unsure and unused
    return eulerAngle(pitch, yaw, roll)

def get_moving_angle(player):
    """Param : int player_id
        Return : eulerAngle , correspond to moving angles"""
    speed = delta_position(player)
    return speed_to_euler_angle(speed)

def get_unit_vectors_from_angles(angles):
    sp, cp = math.sin(angles.pitch/180*math.pi) , math.cos(angles.pitch/180*math.pi)
    sy, cy = math.sin(angles.yaw/180*math.pi) , math.cos(angles.yaw/180*math.pi)
    sr, cr = math.sin(angles.roll/180*math.pi) , math.cos(angles.roll/180*math.pi)

    #Vec pointing "forward"
    y1 = sp
    x1 = - cp * sy
    z1 = cp * cy 

    #Vec pointing "upward"
    z2 = - cy * sp * cr -  sy * sr #not sure if it's ++, +-, -+ or --
    y2 = cp * cr
    x2 = sy * sp * cr - cy * sr
    
    return vec3(x1,y1,z1), vec3(x2,y2,z2)

def get_relative_angles(absolute_angles, up_vector):
    r_y = up_vector
    r_x = r_y @ vec3(0,0,1)
    r_z = r_x @ r_y

    forward_vec, upward_vec = get_unit_vectors_from_angles(absolute_angles)

    pitch = math.asin(forward_vec*r_y)

    return pitch*180/math.pi


#The time difference functions.
"""
time_difference_[name](P1, S1, P2, S2) is a function that takes as arguments
P1,S1 : Player1's Position and Speed vec3.
P2,S2 : Player2's Position and Speed vec3
Return the time it would take for Player1 to catch Player2 (not always symmetric)

get_time_difference_[name](Player1, Player2) takes as arguments
Player1 : Player1 ID
Player2 : Player2 ID
Return the time it would take for Player1 to catch Player2 (not always symmetric)
It's the function called in draw_infodisplay.py
"""

def get_physics(player1, player2):
    """Take the Player1 and Player2 ID's, return their
        P1, S1, P2, S2 data"""
    P1, S1 = VehiclePhysics(player1).position(), delta_position(player1)
    P2, S2 = VehiclePhysics(player2).position(), delta_position(player2)
    return P1,S1,P2,S2


def get_distance_ghost_vec():
    """Give the distance (vec3) between the player and the ghost
        Player to ghost vec"""
    player_position = VehiclePhysics(0).position()
    ghost_position = VehiclePhysics(1).position()
    return (ghost_position - player_position)

def get_distance_ghost():
    """Give the distance(float) between the player and the ghost"""
    return get_distance_ghost_vec().length()

def time_difference_absolute(P1, P2, S1, S2):
    s = S1.length()
    if s != 0:
        return (P2-P1).length() / s
    return float('inf')
    
def get_time_difference_absolute(player1, player2):
    """Time difference "Absolute" (simple and bad)
    Simply takes the distance player-ghost, and divide it by raw speed (always positive)"""
    P1, S1, P2, S2 = get_physics(player1, player2)
    return time_difference_absolute(P1, P2, S1, S2)

def time_difference_relative(P1, P2, S1, S2):
    L = (P2 - P1).length()
    if L == 0:
        return 0
    s = S1*(P2-P1)/L
    if s == 0:
        return float('inf')  
    return (P2-P1).length() / s

def get_time_difference_relative(player1, player2):
    """Time difference "Relative" 
    Take distance player-ghost. Divide it by the player's speed "toward" the ghost (dot product)"""
    P1, S1, P2, S2 = get_physics(player1, player2)
    return time_difference_relative(P1, P2, S1, S2)

def time_difference_projected(P1, P2, S1, S2):
    s = S1.length()
    if s == 0:
        return float('inf')
    return (P2-P1)*S1/(s**2)

def get_time_difference_projected(player1, player2):
    """ Time difference "Projected"
    Take the distance between the player and the plane oriented by the player speed, covering the ghost.
    Then divide it by the player raw speed
    This is the 2D version because no numpy"""
    P1, S1, P2, S2 = get_physics(player1, player2)
    return time_difference_projected(P1, P2, S1, S2)


def time_to_cross(A, S, B, C):
    """If A is going at a constant speed S, how many frame will it take
        to cross the vertical plan containing B and C
        Param : A, S, B, C : (vec3),(vec3),(vec3),(vec3)
        Return t (float) """
    N = (B-C)@vec3(0,1,0) #normal vector to the plan containing B,C
    ns = N*S
    if ns != 0:
        return N*(B-A)/ns
    return float('inf')

    
def time_difference_crosspath(P1, P2, S1, S2):
    t1 = time_to_cross(P1, S1, P2, P2+S2)
    t2 = time_to_cross(P2, S2, P1, P1+S1)
    return t1-t2


def get_time_difference_crosspath(player1, player2):
    """Time difference "CrossPath"
    Take both XZ trajectories of the player and the ghost
    Calculate how much time it takes them to reach the crosspoint. (2D only)
    Return the difference."""
    P1, S1, P2, S2 = get_physics(player1, player2)
    return time_difference_crosspath(P1, P2, S1, S2)



def get_finish_line_coordinate():
    """pointA is the position of the left side of the finish line (vec3)
        point B ---------------------right------------------------------
        both have 0 as their Y coordinate."""
    game_id = utils.get_game_id()
    address = {"RMCE01": 0x809B8F28, "RMCP01": 0x809BD6E8,
               "RMCJ01": 0x809BC748, "RMCK01": 0x809ABD28}
    kmp_ref = chase_pointer(address[game_id], [0x4, 0x0], 'u32')
    offset = memory.read_u32(kmp_ref+0x24)
    pointA = vec3(memory.read_f32(kmp_ref+0x4C+offset+0x8+0x0), 0, memory.read_f32(kmp_ref+0x4C+offset+0x8+0x4))
    pointB = vec3(memory.read_f32(kmp_ref+0x4C+offset+0x8+0x8), 0, memory.read_f32(kmp_ref+0x4C+offset+0x8+0xC))
    return pointA, pointB


def expected_time_left(player_id=0):
    """return the expected time left for the
        player before it crosses the finish line"""
    prevPos = VehicleDynamics.position(player_id)
    pos = VehiclePhysics.position(player_id)
    fl1, fl2 = get_finish_line_coordinate()
    return time_to_cross(pos, pos-prevPos, fl1, fl2)

def time_difference_tofinish(P1, P2, S1, S2):
    A,B = get_finish_line_coordinate()
    t1 = time_to_cross(P1, S1, A, B)
    t2 = time_to_cross(P2, S2, A, B)
    return t1-t2

def get_time_difference_tofinish(player1, player2):
    """Assume player and ghost are not accelerated.
    Calculate the time to the finish line for both, and takes the difference."""
    P1, S1, P2, S2 = get_physics(player1, player2)
    return time_difference_tofinish(P1, P2, S1, S2)


def find_index(value, value_list):
    """Find the index i so value_list[i]>=value>value_list[i+1]
        We suppose value_list[i+1] < value_list[i]
            and value_list[0]>= value>=value_list[-1]"""
    n = len(value_list)
    if n == 1 :
        return 0
    h = n//2
    if value <= value_list[h]:
        return h+find_index(value, value_list[h:])
    return find_index(value, value_list[:h])
    
def get_time_difference_racecompletion(history):
    """Use RaceCompletionData History to calculate the frame difference
        The function assume that RaceCompletion is increasing every frames"""
    if history:
        curframe = history[0]
        lastframe = history[-1]
        inf = float('inf')
        if curframe['prc'] >= curframe['grc']:
            if curframe['grc'] > lastframe['prc']:
                l = [dic['prc'] for dic in history]
                i = find_index(curframe['grc'], l)
                t = i + (curframe['grc'] - l[i])/ (l[i+1] - l[i])
                return -t
            return -inf
        else:
            if curframe['prc'] > lastframe['grc']:
                l =[dic['grc'] for dic in history]
                i = find_index(curframe['prc'], l)
                t = i + (curframe['prc'] - l[i])/ (l[i+1] - l[i])
                return t
            return inf
    else:
        return float('inf')


def get_timediff_settings(string):
    if string == 'player':
        return 0, 1
    if string == 'ghost':
        return 1, 0
    pp, sp, pg, sg = get_physics(0,1)
    player_is_ahead = int(sp*(pg-pp)>0)
    if string == 'ahead':
        return 1-player_is_ahead, player_is_ahead
    if string == 'behind':
        return player_is_ahead, 1-player_is_ahead
    else:
        print('TimeDiff setting value not recognized. Default to "player"')
        return 0, 1

def player_teleport(player_id = 0,
                    x = None, y = None, z = None,
                    pitch = None, yaw = None, roll = None):
    '''Function to teleport the player in player_id to the
        corresponding position and rotation.
        Use None for parameter you don't wanna change'''
    
    addr = VehiclePhysics.chain(player_id)
    position = VehiclePhysics.position(player_id)
    quaternion = VehiclePhysics.main_rotation(player_id)
    angles = eulerAngle.from_quaternion(quaternion)

    if not x is None:
        position.x = x
    if not y is None:
        position.y = y
    if not z is None:
        position.z = z
    if not pitch is None:
        angles.pitch = pitch
    if not yaw is None:
        angles.yaw = yaw
    if not roll is None:
        angles.roll = roll
    
    quaternion = quatf.from_angles(angles)
    position.write(addr + 0x68)
    quaternion.write(addr + 0xF0)

def add_angular_ev(player_id = 0, angle = 90, magnitude = 100, y = 0):
    addr = VehiclePhysics.chain(player_id)
    yaw = get_facing_angle(player_id).yaw
    z = math.cos((-yaw+angle)*math.pi/180) * magnitude
    x = math.sin((-yaw+angle)*math.pi/180) * magnitude
    ev = vec3(x,y,z)
    ev.write(addr + 0x74)

        
