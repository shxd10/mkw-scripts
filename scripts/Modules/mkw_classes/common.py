from dolphin import memory, utils

from dataclasses import dataclass
from enum import Enum
import math
import struct

class RegionError(Exception):
    def __init__(self, message=f"Expected Mario Kart Wii game ID (RMCX01), " \
                                 f"got {utils.get_game_id()}"):
        super().__init__(message)

@dataclass
class vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    @staticmethod
    def read(ptr) -> "vec2":
        bts = memory.read_bytes(ptr, 0x8)
        return vec2(*struct.unpack('>' + 'f'*2, bts))

@dataclass
class vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)
    
    def __mul__(self, other):
        """ vec3 * vec3 -> float (dot product)
            vec3 * float -> vec3 (scalar multiplication)"""
        if type(other) == vec3:
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return vec3(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    def __matmul__(self, other):
        """ vec3 @ vec3 -> vec3 (cross product)
            vec3 @ float -> vec3 (scalar multiplication)"""        
        if type(other) == vec3:
            x = self.y*other.z - self.z*other.y
            y = self.z*other.x - self.x*other.z
            z = self.x*other.y - self.y*other.x
            return vec3(x,y,z)
        else:
            return vec3(self.x * other, self.y * other, self.z * other)
        
    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def length_xz(self) -> float:
        return math.sqrt(self.x**2 + self.z**2)

    def forward(self, facing_yaw) -> float:
        speed_yaw = -180/math.pi * math.atan2(self.x, self.z)
        diff_angle_rad = (facing_yaw - speed_yaw)*math.pi/180
        return math.sqrt(self.x**2 + self.z**2)*math.cos(diff_angle_rad)

    def sideway(self, facing_yaw) -> float:
        speed_yaw = -180/math.pi * math.atan2(self.x, self.z)
        diff_angle_rad = (facing_yaw - speed_yaw)*math.pi/180
        return math.sqrt(self.x**2 + self.z**2)*math.sin(diff_angle_rad)

    @staticmethod
    def read(ptr) -> "vec3":
        bts = memory.read_bytes(ptr, 0xC)
        return vec3(*struct.unpack('>' + 'f'*3, bts))

    def write(self, addr):
        memory.write_bytes(addr, self.to_bytes())

    @staticmethod
    def from_bytes(bts) -> "vec3":
        return vec3(*struct.unpack('>' + 'f'*3, bts))

    def to_bytes(self) -> bytearray:
        return bytearray(struct.pack('>fff', self.x, self.y, self.z))

    def __str__(self):
        return str(self.x)+','+str(self.y)+','+str(self.z)

    @staticmethod
    def from_string(string) -> "vec3":
        temp = string.split(',')
        assert len(temp) == 3
        return vec3(float(temp[0]), float(temp[1]), float(temp[2]))
    




@dataclass
class mat34:
    e00: float = 0.0
    e01: float = 0.0
    e02: float = 0.0
    e03: float = 0.0
    e10: float = 0.0
    e11: float = 0.0
    e12: float = 0.0
    e13: float = 0.0
    e20: float = 0.0
    e21: float = 0.0
    e22: float = 0.0
    e23: float = 0.0

    @staticmethod
    def read(ptr) -> "mat34":
        bts = memory.read_bytes(ptr, 0x30)
        return mat34(*struct.unpack('>' + 'f'*12, bts))

@dataclass
class quatf:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0

    def vec(self) -> "vec3":
        ''' Return the vec3 part of a quaternion'''
        return vec3(self.x, self.y, self.z)

    def __abs__(self):
        ''' The norm / absolute value of the quaternion '''
        return math.sqrt(self.x*self.x + self.y*self.y + self.z+self.z + self.w*self.w)

    def normalize(self):
        ''' Return a normalize version of self. Do not modify self '''
        try:
            return self * (1/abs(self))
        except:
            return quatf(0,0,0,0)

    def __mul__(self, other) -> "quatf":
        ''' quatf * quatf -> quatf (quaternion multiplication)
            quatf * vec3 -> quatf (quaternion multiplication with w = 0 for the vec3)
            quatf * float/int -> quatf (scalar mutliplication)'''
        if type(other) == vec3:
            q2 = quatf(other.x, other.y, other.z, 0)
        elif type(other) == quatf:
            q2 = other
        elif type(other) == int or type(other) == float:
            return quatf(self.x*other, self.y*other, self.z*other, self.w*other)
        else:
            raise TypeError('expected vec3 or quatf')
        q1 = self
        w = q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
        x = q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y
        y = q1.w*q2.y - q1.x*q2.z + q1.y*q2.w + q1.z*q2.x
        z = q1.w*q2.z + q1.x*q2.y - q1.y*q2.x + q1.z*q2.w
        return quatf(x,y,z,w)

    def conjugate(self):
        return quatf(-self.x, -self.y, -self.z, self.w)
    
    def __matmul__(self, other):
        ''' quatf @ vec3 -> vec3 (vector rotation by a quaternion)'''
        if not type(other) == vec3:
            raise TypeError('expected vec3')
        conj = self.conjugate()
        res = self * other
        x = res.y * conj.z + res.x * conj.w + res.w * conj.x - res.z * conj.y
        y = res.z * conj.x + res.y * conj.w + res.w * conj.y - res.x * conj.z
        z = res.x * conj.y + res.z * conj.w + res.w * conj.z - res.y * conj.x
        return vec3(x, y, z)

    @staticmethod
    def read(ptr) -> "quatf":
        bts = memory.read_bytes(ptr, 0x10)
        return quatf(*struct.unpack('>' + 'f'*4, bts))

    def __str__(self):
        return str(self.x)+','+str(self.y)+','+str(self.z)+','+str(self.w)

    def write(self, addr):
        memory.write_bytes(addr, self.to_bytes())

    @staticmethod
    def from_string(string) -> "quatf":
        temp = string.split(',')
        assert len(temp) == 4
        return quatf(float(temp[0]), float(temp[1]), float(temp[2]), float(temp[3]))

    @staticmethod
    def from_bytes(bts) -> "quatf":
        return quatf(*struct.unpack('>' + 'f'*4, bts))

    def to_bytes(self) -> bytearray:
        return bytearray(struct.pack('>ffff', self.x, self.y, self.z, self.w))

    @staticmethod
    def from_angles(angles):
        #arg : angles : eulerAngle
        cr = math.cos(angles.pitch * 0.5 / (180/math.pi))
        sr = math.sin(angles.pitch * 0.5 / (180/math.pi))
        cp = math.cos(angles.yaw * 0.5 / (180/math.pi))
        sp = math.sin(angles.yaw * 0.5 / (180/math.pi))
        cy = math.cos(angles.roll * 0.5 / (180/math.pi))
        sy = math.sin(angles.roll * 0.5 / (180/math.pi))

        return quatf(cr * sp * sy + sr * cp * cy,
                     cr * sp * cy + sr * cp * sy,
                     - cr * cp * sy + sr * sp * cy,
                     - cr * cp * cy + sr * sp * sy)

    @staticmethod
    def from_vectors(vect1, vect2):
        #args : 2 vec3, get the rotation from vect1 to vect2
        cross = vect1 @ vect2
        w = vect1.length() * vect2.length() + vect1 * vect2
        return quatf(cross.x, cross.y, cross.z, w).normalize()


def angle_degree_format(angle):
    return ((angle+180)%360) - 180

class eulerAngle:
    """A class for Euler Angles.
    Angles in degrees, between -180 and 180"""
    def __init__(self, pitch=0, yaw=0, roll=0):
        self.pitch = angle_degree_format(pitch)
        self.yaw = angle_degree_format(yaw)
        self.roll = angle_degree_format(roll)

    def __add__(self, other):
        pitch = self.pitch + other.pitch
        yaw = self.yaw + other.yaw
        roll = self.roll + other.roll
        return eulerAngle(pitch, yaw, roll)
               
    def __sub__(self, other):
        pitch = self.pitch - other.pitch
        yaw = self.yaw - other.yaw
        roll = self.roll - other.roll
        return eulerAngle(pitch, yaw, roll)

    def __mul__(self, other):
        ''' angle * number -> angle '''
        pitch = self.pitch * other
        yaw = self.yaw * other
        roll = self.roll * other
        return eulerAngle(pitch, yaw, roll)

    @staticmethod
    def from_quaternion(q : quatf):
        x1, x2 = 2*q.x*q.w-2*q.y*q.z, 1-2*q.x*q.x-2*q.z*q.z
        y1, y2 = 2*q.y*q.w-2*q.x*q.z, 1-2*q.y*q.y-2*q.z*q.z
        z = 2*q.x*q.y + 2*q.z*q.w
        roll = 180/math.pi * math.asin(z) if abs(z) <= 1 else 90*z/abs(z)
        pitch = -180/math.pi * math.atan2(x1, x2)
        yaw = -180/math.pi * math.atan2(y1, y2)
        return eulerAngle(pitch, yaw, roll)

    def get_unit_vec3(self):
        """ Return a vec3 of size 1, which point
            the same direction as self """
        y = math.sin(self.pitch*math.pi /180)
        xz = math.cos(self.pitch*math.pi /180)
        z = xz * math.cos(self.yaw*math.pi /180)
        x = - xz * math.sin(self.yaw*math.pi /180)
        return vec3(x,y,z)

@dataclass
class ExactTimer:
    """This is used in conjunction with the Exact Finish Code.
       This is not the internal timer class. For that, see timer.py"""
    min: int
    sec: int
    mil: float

    def __add__(self, rhs):
        ret = ExactTimer(self.min, self.sec, self.mil)
        ret.min += rhs.min
        ret.sec += rhs.sec
        ret.mil += rhs.mil
        ret.normalize()
        return ret

    def __sub__(self, rhs):
        ret = ExactTimer(self.min, self.sec, self.mil)
        ret.min -= rhs.min
        ret.sec -= rhs.sec
        ret.mil -= rhs.mil
        ret.normalize()
        return ret

    def normalize(self) -> None:
        carry, self.mil = divmod(self.mil, 1000)
        self.sec += carry
        carry, self.sec = divmod(self.sec, 60)
        self.min += int(carry)

    def __str__(self):
        return "{:02d}:{:012.9f}".format(self.min, self.sec + self.mil)

class CupId(Enum):
    MUSHROOM_CUP = 0
    FLOWER_CUP = 1
    STAR_CUP = 2
    SPECIAL_CUP = 3
    SHELL_CUP = 4
    BANANA_CUP = 5
    LEAF_CUP = 6
    LIGHTNING_CUP = 7

class CourseId(Enum):
    MARIO_CIRCUIT = 0
    MOO_MOO_MEADOWS = 1
    MUSHROOM_GORGE = 2
    GRUMBLE_VOLCANO = 3
    TOADS_FACTORY = 4
    COCONUT_MALL = 5
    DK_SNOWBOARD_CROSS = 6
    WARIOS_GOLD_MINE = 7
    LUIGI_CIRCUIT = 8
    DAISY_CIRCUIT = 9
    MOONVIEW_HIGHWAY = 10
    MAPLE_TREEWAY = 11
    BOWSERS_CASTLE = 12
    RAINBOW_ROAD = 13
    DRY_DRY_RUINS = 14
    KOOPA_CAPE = 15
    GCN_PEACH_BEACH = 16
    GCN_MARIO_CIRCUIT = 17
    GCN_WALUIGI_STADIUM = 18
    GCN_DK_MOUNTAIN = 19
    DS_YOSHI_FALLS = 20
    DS_DESERT_HILLS = 21
    DS_PEACH_GARDENS = 22
    DS_DELFINO_SQUARE = 23
    SNES_MARIO_CIRCUIT_3 = 24
    SNES_GHOST_VALLEY_2 = 25
    N64_MARIO_RACEWAY = 26
    N64_SHERBET_LAND = 27
    N64_BOWSERS_CASTLE = 28
    N64_DKS_JUNGLE_PARKWAY = 29
    GBA_BOWSER_CASTLE_3 = 30
    GBA_SHY_GUY_BEACH = 31
    DELFINO_PIER = 32
    BLOCK_PLAZA = 33
    CHAIN_CHOMP_ROULETTE = 34
    FUNKY_STADIUM = 35
    THWOMP_DESERT = 36
    GCN_COOKIE_LAND = 37
    DS_TWILIGHT_HOUSE = 38
    SNES_BATTLE_COURSE_4 = 39
    GBA_BATTLE_COURSE_3 = 40
    N64_SKYSCRAPER = 41

class VehicleId(Enum):
    STANDARD_KART_S = 0
    STANDARD_KART_M = 1
    STANDARD_KART_L = 2
    BOOSTER_SEAT = 3
    CLASSIC_DRAGSTER = 4
    OFFROADER = 5
    MINI_BEAST = 6
    WILD_WING = 7
    FLAME_FLYER = 8
    CHEEP_CHARGER = 9
    SUPER_BLOOPER = 10
    PIRANHA_PROWLER = 11
    TINY_TITAN = 12
    DAYTRIPPER = 13
    JETSETTER = 14
    BLUE_FALCON = 15
    SPRINTER = 16
    HONEYCOUPE = 17
    STANDARD_BIKE_S = 18
    STANDARD_BIKE_M = 19
    STANDARD_BIKE_L = 20
    BULLET_BIKE = 21
    MACH_BIKE = 22
    FLAME_RUNNER = 23
    BIT_BIKE = 24
    SUGARSCOOT = 25
    WARIO_BIKE = 26
    QUACKER = 27
    ZIP_ZIP = 28
    SHOOTING_STAR = 29
    MAGIKRUISER = 30
    SNEAKSTER = 31
    SPEAR = 32
    JET_BUBBLE = 33
    DOLPHIN_DASHER = 34
    PHANTOM = 35

class CharacterId(Enum):
    MARIO = 0
    BABY_PEACH = 1
    WALUIGI = 2
    BOWSER = 3
    BABY_DAISY = 4
    DRY_BONES = 5
    BABY_MARIO = 6
    LUIGI = 7
    TOAD = 8
    DONKEY_KONG = 9
    YOSHI = 10
    WARIO = 11
    BABY_LUIGI = 12
    TOADETTE = 13
    KOOPA_TROOPA = 14
    DAISY = 15
    PEACH = 16
    BIRDO = 17
    DIDDY_KONG = 18
    KING_BOO = 19
    BOWSER_JR = 20
    DRY_BOWSER = 21
    FUNKY_KONG = 22
    ROSALINA = 23
    SMALL_MII_A_MALE = 24
    SMALL_MII_A_FEMALE = 25
    SMALL_MII_B_MALE = 26
    SMALL_MII_B_FEMALE = 27
    SMALL_MII_C_MALE = 28
    SMALL_MII_C_FEMALE = 29
    MEDIUM_MII_A_MALE = 30
    MEDIUM_MII_A_FEMALE = 31
    MEDIUM_MII_B_MALE = 32
    MEDIUM_MII_B_FEMALE = 33
    MEDIUM_MII_C_MALE = 34
    MEDIUM_MII_C_FEMALE = 35
    LARGE_MII_A_MALE = 36
    LARGE_MII_A_FEMALE = 37
    LARGE_MII_B_MALE = 38
    LARGE_MII_B_FEMALE = 39
    LARGE_MII_C_MALE = 40
    LARGE_MII_C_FEMALE = 41
    MEDIUM_MII = 42
    SMALL_MII = 43
    LARGE_MII = 44
    PEACH_MENU = 45  # biker outfit
    DAISY_MENU = 46  # biker outfit
    ROSALINA_MENU = 47  # biker outfit
    
class WheelCount(Enum):
    _4_WHEELS = 0
    _2_WHEELS = 1
    _2_WHEELS_QUACKER = 2
    _3_WHEELS_BLUE_FALCON = 3

class VehicleType(Enum):
    OUTSIDE_DRIFTING_KART = 0
    OUTSIDE_DRIFTING_BIKE = 1
    INSIDE_DRIFTING_BIKE = 2

class RaceConfigPlayerType(Enum):
    REAL_LOCAL = 0
    CPU = 1
    UNKNOWN = 2  # Most likely never set
    GHOST = 3
    REMOTE = 4
    NONE = 5

class SpecialFloor(Enum):
    BOOST_PANEL = 1
    BOOST_RAMP = 2
    JUMP_PAD = 4

class TrickType(Enum):
    STUNT_TRICK_BASIC = 0
    BIKE_FLIP_TRICK_NOSE = 1
    BIKE_FLIP_TRICK_TAIL = 2
    FLIP_TRICK_Y_LEFT = 3
    FLIP_TRICK_Y_RIGHT = 4
    KART_FLIP_TRICK_Z = 5
    BIKE_SIDE_STUNT_TRICK = 6

class SurfaceProperties():
    def __init__(self, value):
        self.value = value

    WALL = 0x1
    SOLID_OOB = 0x2
    BOOST_RAMP = 0x10
    OFFROAD = 0x40
    BOOST_PANEL_OR_RAMP = 0x100
    TRICKABLE = 0x800
