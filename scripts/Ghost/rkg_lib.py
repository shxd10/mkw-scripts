import configparser
from math import floor
import os
import zlib
from typing import List, Optional
import csv

class Frame:
    """
    A class representing an input combination on a frame.

    Attributes:
        accel (bool): Whether or not we press 'A' on that frame.
        brake (bool): Whether or not we press 'B' on that frame.
        item (bool): Whether or not we press 'L' on that frame.
        stick_x (int): Horizontal stick input, ranging from -7 to +7.
        stick_y (int): Vertical stick input, ranging from -7 to +7.
        dpad_up (bool): Whether or not we press 'Up' on that frame.
        dpad_down (bool): Whether or not we press 'Down' on that frame.
        dpad_left (bool): Whether or not we press 'Left' on that frame.
        dpad_right (bool): Whether or not we press 'Right' on that frame.
        valid (bool): Whether or not the Frame is valid.
        iter_idx (int): Tracks current iteration across the inputs
    """
    accel: bool
    brake: bool
    item: bool
    drift: bool
    brakedrift: bool

    stick_x: int
    stick_y: int

    dpad_up: bool
    dpad_down: bool
    dpad_left: bool
    dpad_right: bool

    valid: bool
    
    iter_idx: int

    def __init__(self, raw: List):
        """
        Initializes a Frame object given a CSV line.

        The structure of the list is as follows:
            * raw[0] (str) - A
            * raw[1] (str) - B/R
            * raw[2] (str) - L
            * raw[5] (str) - Horizontal stick
            * raw[6] (str) - Vertical stick
            * raw[7] (str) - Dpad
            * raw[3] (str) - Drift "ghost" button
            * raw[4] (str) - BrakeDrift "ghost" button
        Args:
            raw (List): CSV line to be read
        """
        self.valid = True

        self.accel = self.read_button(raw[0])
        self.brake = self.read_button(raw[1])
        self.item = self.read_button(raw[2])
        self.drift = self.read_button(raw[3])
        self.brakedrift =  self.read_button(raw[4])
        self.stick_x = self.read_stick(raw[5])
        self.stick_y = self.read_stick(raw[6])
        self.read_dpad(raw[7])

    
    def __iter__(self):
        self.iter_idx = 0
        return self
    
    def __next__(self):
        # If we update to Python 3.10, replace with switch statement
        self.iter_idx += 1
        if (self.iter_idx == 1):
            return int(self.accel)
        if (self.iter_idx == 2):
            return int(self.brake)
        if (self.iter_idx == 3):
            return int(self.item)
        if (self.iter_idx == 4):
            return int(self.drift)
        if (self.iter_idx == 5):
            return int(self.brakedrift)
        if (self.iter_idx == 6):
            return self.stick_x
        if (self.iter_idx == 7):
            return self.stick_y
        if (self.iter_idx == 8):
            return self.dpad_raw()

        raise StopIteration


    
    @staticmethod
    def default():
        return Frame([0,0,0,0,0,0,0,0])

    def __str__(self):
        return ','.join(map(str, self))
    
        
    def read_button(self, button: str) -> bool:
        """
        Parses the button input into a boolean. Sets `self.valid` to False if invalid.
        """
        try:
            val = int(button)
        except ValueError:
            self.valid = False
            return False

        if val < 0 or val > 1:
            self.valid = False

        return bool(val)

    def read_stick(self, stick: str) -> int:
        """
        Parses the stick input into an int. Sets `self.valid` to False if invalid.
        """
        try:
            val = int(stick)
        except ValueError:
            self.valid = False
            return 0

        if val < -7 or val > 7:
            self.valid = False

        return val

    def read_dpad(self, dpad: str) -> None:
        """
        Sets dpad members based on dpad input. Sets `self.valid` to False if invalid.
        """
        try:
            val = int(dpad)
        except ValueError:
            self.valid = False
            return

        if val < 0 or val > 4:
            self.valid = False

        self.dpad_up = val == 1
        self.dpad_down = val == 2
        self.dpad_left = val == 3
        self.dpad_right = val == 4
        
    def dpad_raw(self) -> int:
        """
        Converts dpad values back into its raw form, for writing to the csv
        """
        if self.dpad_up:
            return 1
        if self.dpad_down:
            return 2
        if self.dpad_left:
            return 3
        if self.dpad_right:
            return 4
        return 0

def compressInputList(rawInputList):
    """A function that convert Raw Input List (List of Frames) to
        Compressed Input List (List of 7-int-list, TTK .csv format)"""
    compressedInputList = []
    prevInputRaw = Frame(["0"]*8)
    prevInputCompressed = [0,0,0,0,0,0,-1]
    for rawInput in rawInputList:
        compressedInput = [int(rawInput.accel),
                           0,  
                           int(rawInput.item),
                           rawInput.stick_x,
                           rawInput.stick_y,
                           rawInput.dpad_raw(),
                           -1] 
        if not rawInput.brake:
            compressedInput[1] = 0
        elif rawInput.brakedrift:
            compressedInput[1] = 3
        elif not prevInputRaw.brake:
            compressedInput[1] = 1
        elif rawInput.drift and not prevInputRaw.drift:
            compressedInput[1] = 3-prevInputCompressed[1]
        else:
            compressedInput[1] = prevInputCompressed[1]

        if rawInput.accel and rawInput.brake and (not rawInput.drift):
            if prevInputRaw.accel and prevInputRaw.brake and prevInputRaw.drift:
                compressedInput[6] = 0
            elif not prevInputRaw.brake:
                compressedInput[6] = 0

        if ((not rawInput.accel) or (not rawInput.brake)) and rawInput.drift:
            compressedInput[6] = 1

        prevInputRaw = rawInput
        prevInputCompressed = compressedInput
        compressedInputList.append(compressedInput)
    return compressedInputList

def decompressInputList(compressedInputList):
    """A function that convert Compressed Input List (List of 7-int-list, TTK .csv format) to
        Raw Input List (List of Frames)"""
    prevInputRaw = Frame(["0"]*8)
    prevInputCompressed = [0,0,0,0,0,0,-1]
    rawInputList = []
    for compressedInput in compressedInputList:
        accel = compressedInput[0]
        brake = int(compressedInput[1]>0)
        item = compressedInput[2]
        X = compressedInput[3]
        Y = compressedInput[4]
        dpad = compressedInput[5]
        brakedrift = int(compressedInput[1]==3)

        if accel + brake < 2: 
            drift = 0
        elif prevInputRaw.drift:
            drift = 1
        elif prevInputCompressed[1] == compressedInput[1]:
            drift = 0
        else:
            drift = 1

        if compressedInput[6] != -1:
            drift = compressedInput[6]

        rawInput = Frame(list(map(str, (accel, brake, item, drift, brakedrift, X, Y, dpad))))
        prevInputRaw = rawInput
        prevInputCompressed = compressedInput
        rawInputList.append(rawInput)
    return rawInputList


    
class FrameSequence:
    """
    A class representing a sequence of inputs, indexed by frames.

    Attributes:
        frames (list): The sequence of frames.
        filename (str): The name of the CSV file initializing the frame sequence.
    """
    frames: list
    filename: str
    iter_idx: int

    def __init__(self, filename: Optional[str]=None):
        self.frames = []
        self.filename = filename

        if self.filename:
            self.read_from_file()
    
    def __len__(self):
        return len(self.frames)
        
    def __getitem__(self, i):
        if (i < len(self.frames)):
            return self.frames[i]
        return None
        
    def __iter__(self):
        self.iter_idx = -1
        return self
        
    def __next__(self):
        self.iter_idx += 1
        if (self.iter_idx < len(self.frames)):
            return self.frames[self.iter_idx]
        raise StopIteration
        
    def read_from_list(self, inputs: List) -> None:
        """
        Constructs the frames list by using a list instead of a csv
        
        Args:
            input (List): The raw input data we want to store
        Returns: None
        """
        for input in inputs:
            frame = self.process(input)
            if not frame:
                pass
            self.frames.append(frame)

    def read_from_list_of_frames(self, inputs: List) -> None:
        """
        Constructs the frames list by using a list of Frames instead of a csv
        
        Args:
            input (List): The raw input data we want to store
        Returns: None
        """
        for frame in inputs:
            self.frames.append(frame)
    
    def read_from_file(self) -> None:
        """
        Loads the CSV into a new frame sequence. Ideally called on savestate load.

        Args: None
        Returns: None
        """
        self.frames.clear()
        try:
            with open(self.filename, 'r') as f:
                reader = csv.reader(f)
                compressedInputList = []
                for row in reader:
                    compressedInputList.append(list(map(int,row)))
            for frame in decompressInputList(compressedInputList):
                self.frames.append(frame)
        except IOError:
            return
                
    def write_to_file(self, filename: str) -> bool:
        """
        Writes the frame sequence to a csv
        
        Args:
            filename (str): The path to the file we wish to write to
        Returns:
            A boolean indicating whether the write was successful
        """
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerows(compressInputList(self.frames))
        except IOError:
            return False
        return True

    def process(self, raw_frame: List) -> Optional[Frame]:
        """
        Processes a raw frame into an instance of
        the Frame class. Ideally used internally.

        Args:
            raw_frame (List): Line from the CSV to process.

        Returns:
            A new Frame object initialized with the raw frame,
            or None if the frame is invalid.
        """
        assert len(raw_frame) == 8
        if len(raw_frame) != 8:
            return None

        frame = Frame(raw_frame)
        if not frame.valid:
            return None

        return frame


def extract_bits(data, start_bit, length):
    byte_index = start_bit // 8
    bit_offset = start_bit % 8
    bits = 0

    for i in range(length):
        bit_position = bit_offset + i
        bits <<= 1
        bits |= (data[byte_index + (bit_position // 8)] >> (7 - (bit_position % 8))) & 1

    return bits






def crc16(i):
    '''Argument : bytearray
        Return : 16bit int'''
    #https://stackoverflow.com/questions/25239423/crc-ccitt-16-bit-python-manual-calculation
    def _update_crc(crc, c):
        def _initial(c):
            POLYNOMIAL = 0x1021
            PRESET = 0
            crc = 0
            c = c << 8
            for j in range(8):
                if (crc ^ c) & 0x8000:
                    crc = (crc << 1) ^ POLYNOMIAL
                else:
                    crc = crc << 1
                c = c << 1
            return crc
        POLYNOMIAL = 0x1021
        PRESET = 0
        _tab = [ _initial(i) for i in range(256) ]
        cc = 0xff & c
        tmp = (crc >> 8) ^ cc
        crc = (crc << 8) ^ _tab[tmp & 0xff]
        crc = crc & 0xffff
        return crc
    POLYNOMIAL = 0x1021
    PRESET = 0
    crc = PRESET
    for c in i:
        crc = _update_crc(crc, c)
    return crc


def convertTimer(bits: int):
    '''Convert a 24 bits int representing a Timer (m,s,ms), to a float in seconds'''
    ms = bits & 1023
    bits >>= 10
    s = bits & 127
    bits >>= 7
    m = bits & 127
    return m*60+s+ms/1000

def convertTimerBack(split: float):
    '''Convert a float in seconds, to a 24 bits int representing a Timer (m,s,ms)'''
    m = floor(split/60)
    s = floor(split%60)
    ms = floor(split*1000)%1000
    return ms + (s<<10) + (m <<17)

def add_bits(bit_list, number, size):
    ''' Add to a bit list another number, with a bit size'''
    for i in range(size):
        bit_list.append((number >> (size - i -1)) & 1)

def bits_to_bytearray(bit_list):
    ''' Convert an array of bits to an array of bytes (grouping bits by 8)'''
    b = bytearray()
    byte = 0
    for i in range(len(bit_list)):
        byte = (byte << 1) + bit_list[i]
        if i%8 == 7:
            b.append(byte)
            byte = 0
    if byte != 0:
        b.append(byte)
    return b

class RKGMetaData:
    def __init__(self, rkg_data, useDefault = False):
        if not useDefault:
            self.finish_time = convertTimer(extract_bits(rkg_data, 4*8+0, 24))
            self.track_id = extract_bits(rkg_data, 7*8+0, 6)
            self.character_id = extract_bits(rkg_data, 8*8+6, 6)
            self.vehicle_id = extract_bits(rkg_data, 8*8+0, 6)
            self.year = extract_bits(rkg_data, 9*8+4, 7)
            self.month = extract_bits(rkg_data, 0xA*8+3, 4)
            self.day = extract_bits(rkg_data, 0xA*8+7, 5)
            self.controller_id = extract_bits(rkg_data, 0xB*8+4, 4)
            self.compressed_flag = extract_bits(rkg_data, 0xC*8+4, 1)
            self.ghost_type = extract_bits(rkg_data, 0xC*8+7, 7)
            self.drift_id = extract_bits(rkg_data, 0xD*8+6, 1)
            self.input_data_length = extract_bits(rkg_data, 0xE*8+0, 16)
            self.lap_count = extract_bits(rkg_data, 0x10*8+0, 8)
            self.lap1_split = convertTimer(extract_bits(rkg_data, 0x11*8+0, 24))
            self.lap2_split = convertTimer(extract_bits(rkg_data, 0x14*8+0, 24))
            self.lap3_split = convertTimer(extract_bits(rkg_data, 0x17*8+0, 24))
            self.country_code = extract_bits(rkg_data, 0x34*8+0, 8)
            self.state_code = extract_bits(rkg_data, 0x35*8+0, 8)
            self.location_code = extract_bits(rkg_data, 0x36*8+0, 16)
        else:
            self.finish_time = 100
            self.track_id = 0
            self.character_id = 0
            self.vehicle_id = 0
            self.year = 25
            self.month = 1
            self.day = 1
            self.controller_id = 3
            self.compressed_flag = 0
            self.ghost_type = 38
            self.drift_id = 0
            self.input_data_length = 908
            self.lap_count = 3
            self.lap1_split = 0
            self.lap2_split = 5999.999
            self.lap3_split = 5999.999
            self.country_code = 255
            self.state_code = 255
            self.location_code = 65535

    def __iter__(self):
        return iter([self.finish_time,
            self.track_id,
            self.character_id,
            self.vehicle_id,
            self.year,
            self.month,
            self.day,
            self.controller_id,
            self.compressed_flag,
            self.ghost_type,
            self.drift_id,
            self.input_data_length,
            self.lap_count,
            self.lap1_split,
            self.lap2_split,
            self.lap3_split,
            self.country_code,
            self.state_code,
            self.location_code])

    def __str__(self):
        res = ""
        res += "finish_time = " + str(self.finish_time)+"\n"
        res += "track_id = " + str(self.track_id)+"\n"
        res += "character_id = " + str(self.character_id)+"\n"
        res += "vehicle_id = " + str(self.vehicle_id)+"\n"
        res += "year = " + str(self.year)+"\n"
        res += "month = " + str(self.month)+"\n"
        res += "day = " + str(self.day)+"\n"
        res += "controller_id = " + str(self.controller_id)+"\n"
        res += "compressed_flag = " + str(self.compressed_flag)+"\n"
        res += "ghost_type = " + str(self.ghost_type)+"\n"
        res += "drift_id = " + str(self.drift_id)+"\n"
        res += "input_data_length = " + str(self.input_data_length)+"\n"
        res += "lap_count = " + str(self.lap_count)+"\n"
        res += "lap1_split = " + str(self.lap1_split)+"\n"
        res += "lap2_split = " + str(self.lap2_split)+"\n"
        res += "lap3_split = " + str(self.lap3_split)+"\n"
        res += "country_code = " + str(self.country_code)+"\n"
        res += "state_code = " + str(self.state_code)+"\n"
        res += "location_code = " + str(self.location_code)
        return res
    
    @staticmethod
    def from_string(string):
        lines = string.split("\n")
        self = RKGMetaData(None, True)
        self.finish_time = float(lines[0].split('=')[1])
        self.track_id = int(lines[1].split('=')[1])
        self.character_id = int(lines[2].split('=')[1])
        self.vehicle_id = int(lines[3].split('=')[1])
        self.year = int(lines[4].split('=')[1])
        self.month = int(lines[5].split('=')[1])
        self.day = int(lines[6].split('=')[1])
        self.controller_id = int(lines[7].split('=')[1])
        self.compressed_flag = int(lines[8].split('=')[1])
        self.ghost_type = int(lines[9].split('=')[1])
        self.drift_id = int(lines[10].split('=')[1])
        self.input_data_length = int(lines[11].split('=')[1])
        self.lap_count = int(lines[12].split('=')[1])
        self.lap1_split = float(lines[13].split('=')[1])
        self.lap2_split = float(lines[14].split('=')[1])
        self.lap3_split = float(lines[15].split('=')[1])
        self.country_code = int(lines[16].split('=')[1])
        self.state_code = int(lines[17].split('=')[1])
        self.location_code = int(lines[18].split('=')[1])
        return self

    def to_bytes(self):
        bit_list = []
        add_bits(bit_list, convertTimerBack(self.finish_time), 24)
        add_bits(bit_list, self.track_id, 6)
        add_bits(bit_list, 0, 2) 
        add_bits(bit_list, self.vehicle_id, 6)
        add_bits(bit_list, self.character_id, 6)
        add_bits(bit_list, self.year, 7)
        add_bits(bit_list, self.month, 4)
        add_bits(bit_list, self.day, 5)
        add_bits(bit_list, self.controller_id, 4)
        add_bits(bit_list, 0, 4)
        add_bits(bit_list, self.compressed_flag, 1)
        add_bits(bit_list, 0, 2)
        add_bits(bit_list, self.ghost_type, 7)
        add_bits(bit_list, self.drift_id, 1)
        add_bits(bit_list, 0, 1)
        add_bits(bit_list, self.input_data_length, 8*2)
        add_bits(bit_list, self.lap_count, 8*1)
        add_bits(bit_list, convertTimerBack(self.lap1_split), 24)
        add_bits(bit_list, convertTimerBack(self.lap2_split), 24)
        add_bits(bit_list, convertTimerBack(self.lap3_split), 24)
        add_bits(bit_list, 0, 2*3*8)
        add_bits(bit_list, 0, 8*0x14)
        add_bits(bit_list, self.country_code, 8)
        add_bits(bit_list, self.state_code, 8)
        add_bits(bit_list, self.location_code, 8*2)
        add_bits(bit_list, 0, 8*4)

        res = bytearray(b'RKGD') + bits_to_bytearray(bit_list)
        return res


def decompress_ghost_input(ghost_src):
    if len(ghost_src) > 0x8F and ghost_src[0x8C:0x90] == b'Yaz1':
        uncompressed_size = (ghost_src[0x90] << 24) + (ghost_src[0x91] << 16) + (ghost_src[0x92] << 8) + ghost_src[0x93]
        return decode_Yaz1(ghost_src, 0x9c, uncompressed_size)
    else:
        return list(ghost_src[0x88:])

def decode_Yaz1(src, offset, uncompressed_size):
    src_pos = offset
    valid_bit_count = 0
    try:
        curr_code_byte = src[offset + src_pos]
    except:
         curr_code_byte = src[src_pos]

    dst = []
    
    while len(dst) < uncompressed_size:
        if valid_bit_count == 0:
            curr_code_byte = src[src_pos]
            src_pos += 1
            valid_bit_count = 8

        if (curr_code_byte & 0x80) != 0:
            dst.append(src[src_pos])
            src_pos += 1
        else:
            byte1 = src[src_pos]
            byte2 = src[src_pos + 1]
            src_pos += 2
            dist = ((byte1 & 0xF) << 8) | byte2
            copy_source = len(dst) - (dist + 1)
            num_bytes = byte1 >> 4
            if num_bytes == 0:
                num_bytes = src[src_pos] + 0x12
                src_pos += 1
            else:
                num_bytes += 2

            for _ in range(num_bytes):
                dst.append(dst[copy_source])
                copy_source += 1

        curr_code_byte <<= 1
        valid_bit_count -= 1

    return dst


def decode_rkg_inputs(rkg_data):
    raw_data = decompress_ghost_input(rkg_data)
    button_inputs = []
    analog_inputs = []
    trick_inputs = []
    cur_byte = 8
    nr_button_inputs = (raw_data[0] << 8) | raw_data[1]
    nr_analog_inputs = (raw_data[2] << 8) | raw_data[3]
    nr_trick_inputs = (raw_data[4] << 8) | raw_data[5]

    for _ in range(nr_button_inputs):
        if cur_byte + 1 < len(raw_data):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
        else:
            inputs = 0
            frames = 0
        accelerator = inputs & 0x1
        drift = (inputs & 0x2) >> 1
        item = (inputs & 0x4) >> 2
        pseudoAB = (inputs & 0x8) >> 3
        breakdrift = (inputs & 0x10) >> 4
        button_inputs += [(accelerator, drift, item, pseudoAB, breakdrift)] * frames
        cur_byte += 2

    for _ in range(nr_analog_inputs):
        if cur_byte + 1 < len(raw_data):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
        else:
            inputs = 0
            frames = 0
        horizontal = ((inputs >> 4) & 0xF) - 7
        vertical = (inputs & 0xF) - 7
        analog_inputs += [(horizontal, vertical)] * frames
        cur_byte += 2

    for _ in range(nr_trick_inputs):
        if cur_byte + 1 < len(raw_data):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
        else:
            inputs = 0
            frames = 0
        trick = (inputs & 0x70) >> 4
        extra_frames = (inputs & 0x0F) << 8
        trick_inputs += [trick] * (frames + extra_frames)
        cur_byte += 2
    inputList = []
    for i in range(len(button_inputs)):
        if i >= len(analog_inputs):
            analog_inputs.append((0,0))
        if i >= len(trick_inputs):
            trick_inputs.append(0)
        inputList.append(Frame([button_inputs[i][0],
                          button_inputs[i][1],
                          button_inputs[i][2],
                          button_inputs[i][3],
                          button_inputs[i][4],
                          analog_inputs[i][0],
                          analog_inputs[i][1],
                          trick_inputs[i]]))
    res = FrameSequence()
    res.read_from_list_of_frames(inputList)
    return res


def encodeFaceButton(aButton, bButton, lButton, pabButton, bdButton):
    return aButton * 0x1 + bButton * 0x2 + lButton * 0x4 + pabButton * 0x8 + bdButton * 0x10

def encodeDirectionInput(horizontalInput, verticalInput):
    return ((horizontalInput+7) << 4) + verticalInput+7

def encodeTrickInput(trickInput):
    return trickInput << 4

def encodeRKGInput(inputList : 'FrameSequence'):
    data = bytearray()
    dataIndex = 0
    iL = inputList.frames    
    fbBytes, diBytes, tiBytes = 0, 0, 0

    #Encode face buttons inputs
    prevInput = encodeFaceButton(iL[0].accel, iL[0].brake, iL[0].item, iL[0].drift, iL[0].brakedrift)
    amountCurrentFrames = 0x0   
    for ipt in iL:
        currentInput = encodeFaceButton(ipt.accel, ipt.brake, ipt.item, ipt.drift, ipt.brakedrift)
        if prevInput != currentInput or amountCurrentFrames >= 0xFF:
            data.append(prevInput)
            data.append(amountCurrentFrames)  
            prevInput = currentInput
            amountCurrentFrames = 0x1
            fbBytes = fbBytes + 1
        else:
            amountCurrentFrames = amountCurrentFrames + 1
    data.append(prevInput)
    data.append(amountCurrentFrames)  
    fbBytes = fbBytes + 1

    #Encode joystick inputs
    prevInput = encodeDirectionInput(iL[0].stick_x, iL[0].stick_y)
    amountCurrentFrames = 0x0
    for ipt in iL:
        currentInput = encodeDirectionInput(ipt.stick_x, ipt.stick_y)
        if prevInput != currentInput or amountCurrentFrames >= 0xFF:
            data.append(prevInput)
            data.append(amountCurrentFrames)  
            prevInput = currentInput
            amountCurrentFrames = 0x1
            diBytes = diBytes + 1
        else:
            amountCurrentFrames = amountCurrentFrames + 1
    data.append(prevInput)
    data.append(amountCurrentFrames)  
    diBytes = diBytes + 1
    
    #Encode trick inputs
    prevInput = encodeTrickInput(iL[0].dpad_raw())
    amountCurrentFrames = 0x0  
    for ipt in iL:
        currentInput = encodeTrickInput(ipt.dpad_raw())
        if prevInput != currentInput or amountCurrentFrames >= 0xFFF:
            data.append(prevInput + (amountCurrentFrames >> 8))
            data.append(amountCurrentFrames % 0x100)
            prevInput = currentInput
            amountCurrentFrames = 0x1
            tiBytes = tiBytes + 1
        else:
            amountCurrentFrames = amountCurrentFrames + 1

    data.append(prevInput + (amountCurrentFrames >> 8))
    data.append(amountCurrentFrames % 0x100)
    tiBytes = tiBytes + 1
            
    return data, fbBytes, diBytes, tiBytes


def decode_RKG(raw_data : bytearray):
    ''' Decode RKG data to 3 objetcs :
            - RKGMetaData
            - FrameSequence
            - Mii Raw data (bytearray, size 0x4A)'''
    if len(raw_data) < 0x88:
        print("decode_RKG can't decode raw_data : raw_data too small")
    else:
        metadata = RKGMetaData(raw_data)
        inputList = decode_rkg_inputs(raw_data)
        mii_data = raw_data[0x3C:0x86]
        return metadata, inputList, mii_data


def encode_RKG(metadata : 'RKGMetaData', inputList : 'FrameSequence', mii_data : bytearray):
    ''' Encode to a RKG raw data (bytearray) '''
    inputData, fbBytes, diBytes, tiBytes = encodeRKGInput(inputList)
    dataIndex = (fbBytes + diBytes + tiBytes) * 0x2
    metadata.input_data_length = dataIndex + 0x8
    metadata.compressed_flag = 0
    crc16_int = crc16(mii_data)

    metadata_bytes = metadata.to_bytes()
    crc16_data = bytearray([crc16_int >> 8, crc16_int & 0xFF])
    inputHeader = bytearray([fbBytes >> 8, fbBytes & 0xFF, diBytes >> 8, diBytes & 0xFF, tiBytes >> 8, tiBytes & 0xFF, 0, 0])

    rkg_data = metadata_bytes + mii_data + crc16_data + inputHeader + inputData
    crc32 = zlib.crc32(rkg_data)
    arg1 = floor(crc32 / 0x1000000)
    arg2 = floor((crc32 & 0x00FF0000) / 0x10000)
    arg3 = floor((crc32 & 0x0000FF00) / 0x100)
    arg4 = floor(crc32 % 0x100)
        
        
    return rkg_data + bytearray([arg1, arg2, arg3, arg4])


