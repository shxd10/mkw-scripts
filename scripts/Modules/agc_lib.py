from dolphin import gui, memory, utils
from .mkw_classes import quatf, vec3
from .framesequence import Frame
from .mkw_utils import chase_pointer
from .ttk_lib import write_player_inputs, write_ghost_inputs
from .mkw_classes import VehiclePhysics, KartMove, RaceConfig, Timer, RaceManagerPlayer, RaceConfigPlayer, RaceConfigScenario, Controller, InputMgr
import math

class AGCFrameData:
    """Class to represent a set of value accessible each frame in the memory
        """
    Position : 'vec3'
    Rotation : 'quatf'
    IV : 'vec3'
    EV : 'vec3'
    MaxIV : float
    CurIV : float
    ODA : float #Outside Drift Angle
    Dir : 'vec3'
    Dive : float
    Input : 'Frame'
        
    def __init__(self, usedefault=False, read_slot = 0):
        if not usedefault:            
            self.Position = VehiclePhysics.position(read_slot)
            self.Rotation = VehiclePhysics.main_rotation(read_slot)
            self.IV = VehiclePhysics.internal_velocity(read_slot)
            self.EV = VehiclePhysics.external_velocity(read_slot)
            self.MaxIV = KartMove.soft_speed_limit(read_slot)
            self.CurIV = KartMove.speed(read_slot)
            self.ODA = KartMove.outside_drift_angle(read_slot)
            self.Dir = KartMove.dir(read_slot)
            self.Dive = KartMove.diving_rotation(read_slot)
            self.Input = Frame.from_current_frame(read_slot)           
        else:
            self.Position = vec3(0,0,0)
            self.Rotation = quatf(0,0,0,0)
            self.IV = vec3(0,0,0)
            self.EV = vec3(0,0,0)
            self.MaxIV = 0
            self.CurIV = 0
            self.ODA = 0
            self.Dir = vec3(0,0,0)
            self.Dive = 0
            self.Input = Frame.default()

    def __iter__(self):
        return iter([self.Position,
              self.Rotation,
              self.IV,
              self.EV,
              self.MaxIV,
              self.CurIV,
              self.ODA,
              self.Dir,
              self.Dive,
              self.Input])

    def __str__(self):
        return ';'.join(map(str, self))

    @staticmethod
    def read_from_string(string):
        res = AGCFrameData(usedefault = True)
        temp = string.split(';')
        assert len(temp) == 10
        
        res.Position = vec3.from_string(temp[0])
        res.Rotation = quatf.from_string(temp[1])
        res.IV = vec3.from_string(temp[2])
        res.EV = vec3.from_string(temp[3])
        res.MaxIV = float(temp[4])
        res.CurIV = float(temp[5])
        res.ODA = float(temp[6])
        res.Dir = vec3.from_string(temp[7])
        res.Dive = float(temp[8])
        res.Input = Frame(temp[9].split((',')))

        return res

    def interpolate(self,other, selfi, otheri):
        #BE CAREFUL, THIS FUNCTION MODIFY SELF ! (be sure to call on a copy before)
        v1 = self.Position
        v2 = other.Position
        v = (v1*selfi)+(v2*otheri)
        self.Position = v

    def load(self, write_slot, input_only = False):
        kma = KartMove.chain(write_slot)
        vpa = VehiclePhysics.chain(write_slot)
        
        if not input_only:
            self.Position.write(vpa + 0x68)
            self.Rotation.write(vpa + 0xF0)
            self.IV.write(vpa + 0x14C)
            self.EV.write(vpa + 0x74)
            memory.write_f32(kma + 0x18, self.MaxIV)
            memory.write_f32(kma + 0x20, self.CurIV)
            memory.write_f32(kma + 0x9C, self.ODA)
            self.Dir.write(kma + 0x5C)
            memory.write_f32(kma + 0xF4, self.Dive)
        if write_slot == 0 :
            write_player_inputs(self.Input)
        else:
            write_ghost_inputs(self.Input, write_slot)



class AGCMetaData:
    """Class for the metadata of a ghost.
        Contain Character ID, Vehicle ID, Drift ID, and all 3 lap splits"""

    def __init__(self, useDefault = False, read_id = 0):
        if not useDefault:
            rcp = RaceConfigPlayer(RaceConfigScenario(RaceConfig.race_scenario()).player(read_id))
            gc_controller = Controller(InputMgr().gc_controller(read_id))
            self.charaID = rcp.character_id().value
            self.vehicleID = rcp.vehicle_id().value
            self.driftID = int(gc_controller.drift_is_auto()) #ASSUME YOU USE A GCN CONTROLLER ! TODO : HANDLE ALL CONTROLLER
            self.timer_data = [Split.from_timer(RaceManagerPlayer.lap_finish_time(read_id, lap)) for lap in range(3)]
        else:
            self.charaID = 0
            self.vehicleID = 0
            self.driftID = 0
            self.timer_data = [Split(0),Split(0),Split(0)]

    def __str__(self):
        return ";".join(map(str, self))

    def __iter__(self):
        return iter([self.charaID, self.vehicleID, self.driftID]+self.timer_data)

    @staticmethod
    def read_from_string(string):
        res = AGCMetaData(useDefault = True)
        temp = string.split(";")

        assert len(temp) >= 6

        res.charaID = int(temp[0])
        res.vehicleID = int(temp[1])
        res.driftID = int(temp[2])
        res.timer_data = [Split.from_string(temp[i]) for i in range(3, len(temp))]

        return res

    def load(self, write_slot):
        pass

    def delay_timer(self, delay):
        region = utils.get_game_id()
        try:
            address = {"RMCE01": 0x809BFDC0, "RMCP01": 0x809C4680,
                    "RMCJ01": 0x809C36E0, "RMCK01": 0x809B2CC0}
            timer_addr = chase_pointer(address[region], [0x1D0, 0x16C, 0xC], 'u32') + 0x2B8
        except KeyError:
            raise RegionError

        
        for lap in range(3):
            lap_time = self.timer_data[lap].val
            if lap > 0:
                lap_time -= self.timer_data[lap-1].val #timer_data is cumulative format so you have to substract each cumulative laps
            lap_time = max(0, lap_time - delay)
            m, s, ms = Split(lap_time).time_format()
            memory.write_u16(timer_addr + lap*0xC + 0x4, m)
            memory.write_u8(timer_addr + lap*0xC + 0x6, s)
            memory.write_u16(timer_addr + lap*0xC + 0x8, ms)
        

class Split:
    """Class for a lap split. Contain just a float, representing the split in seconds"""
    def __init__(self, f):
        self.val = f
    def __str__(self):
        return f"{self.val:.3f}"
    def __add__(self,other):
        return Split(max(0, self.val+other.val)) 

    @staticmethod
    def from_string(string):
        return Split(float(string))

    @staticmethod
    def from_time_format(m,s,ms):
        return Split(m*60+s+ms/1000)
    
    @staticmethod
    def from_timer(timer_inst):
        return Split(timer_inst.minutes()*60+timer_inst.seconds()+timer_inst.milliseconds()/1000)
    
    @staticmethod
    def from_bytes(b):
        data_int = b[0]*256*256+b[1]*256+b[2]
        ms = data_int%1024
        data_int = data_int//1024
        s = data_int%128
        data_int = data_int//128
        m = data_int%128
        return Split(m*60+s+ms/1000)

    @staticmethod
    def from_rkg(rkg_addr,lap):
        timer_addr = rkg_addr+0x11+0x3*(lap-1)
        b = memory.read_bytes(timer_addr, 3)
        return Split.from_bytes(b)
        
    
    def time_format(self):
        #return m,s,ms corresponding
        f = self.val
        ms = round((f%1)*1000)
        s = math.floor(f)%60
        m = math.floor(f)//60
        return m,s,ms
    
    def bytes_format(self):
        #return a bytearray of size 3 for rkg format
        m,s,ms = self.time_format()
        data_int = ms+s*1024+m*1024*128
        b3 = data_int%256
        data_int = data_int//256
        b2 = data_int%256
        data_int = data_int//256
        b1 = data_int%256
        return bytearray((b1,b2,b3))

    def time_format_bytes(self):
        #return a bytearray of size 6, for the timer format.
        #2 first bytes are m, then s on 1 byte, then 00, then ms on 2 bytes
        m,s,ms = self.time_format()
        return bytearray([m//256, m%256, s%256, 0, ms//256, ms%256])

        

        
def file_to_framedatalist(filename):
    datalist = []
    file = open(filename, 'r')
    if file is None :
        gui.add_osd_message("Error : could not load "+filename)
        return None
    else:
        listlines = file.readlines()
        metadata = AGCMetaData.read_from_string(listlines[0])
        for i in range(1, len(listlines)):
            datalist.append(AGCFrameData.read_from_string(listlines[i]))
        file.close()
        gui.add_osd_message(f"Data successfully loaded from {filename}")
        return metadata, datalist


def framedatalist_to_file(filename, datalist, rid):
    metadata = AGCMetaData(rid)
    file = open(filename, 'w')
    if file is None :
        gui.add_osd_message("Error : could not create "+filename)
    else:
        file.write(str(metadata)+'\n')
        for frame in range(max(datalist.keys())+1):
            if frame in datalist.keys():
                file.write(str(datalist[frame])+'\n')
            else:
                file.write(str(AGCFrameData(usedefault=True))+'\n')
        file.close()



 
