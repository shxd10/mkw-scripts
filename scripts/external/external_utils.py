from multiprocessing import shared_memory
import atexit
import subprocess
import os
import configparser
import platform


def start_external_script(path: str, force_exit = True, create_no_window = True, *args):
    ''' Start an external script using the user's own python env
        path (str) : path to the filename of the script to start
        force_exit (bool) : Can force the external script to stop when the calling script ends.
        create_no_window (bool) : Can prevent the external script from creating a new window.
        *agrs : extra args to give to the external script. (access with sys.argv)'''
    if create_no_window:
        process = subprocess.Popen(["python", path, *args], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        process = subprocess.Popen(["python", path, *args])
    if force_exit:
        atexit.register(process.terminate)


def run_external_script(path: str, *args):
    output = subprocess.check_output(["python", path, *args], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return output

#Open a file with the default application
def open_file(path: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', path))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(path, 'edit')
    else:                                   # linux variants
        subprocess.call(('xdg-open', path))

class SharedMemoryWriter:
    def __init__(self, name: str, buffer_size: int, create=True):
        self._shm = shared_memory.SharedMemory(create=create, name=name, size=buffer_size)
        atexit.register(self.close)

    def write(self, bytes_: bytes):
        if len(bytes_) > len(self._shm.buf):
            raise ValueError("Data is too large for shared memory buffer.")
        self._shm.buf[:len(self._shm.buf)] = bytes_ + b'\x00' * (len(self._shm.buf) -  len(bytes_))

    def write_text(self, text: str):
        bytes_ = text.encode('utf-8')
        self.write(bytes_)

    def close(self):
        self._shm.close()
        self._shm.unlink()


class SharedMemoryReader:
    def __init__(self, name: str):
        self._shm = shared_memory.SharedMemory(name=name)
        atexit.register(self.close)
    
    def read(self):
        return bytes(self._shm.buf)
    
    def read_text(self):
        return self.read().rstrip(b'\x00').decode('utf-8')
    
    def close(self):
        self._shm.close()

    def close_with_writer(self):
        self._shm.close()
        self._shm.unlink()


class SharedMemoryBlock:
    """ Allows both reading and writing to a shared memory block """
    def __init__(self, _shm: shared_memory.SharedMemory):
        self._shm = _shm

    @staticmethod
    def create(name: str, buffer_size: int):
        """ Create new shared memory block """
        shm = SharedMemoryBlock(shared_memory.SharedMemory(create=True, name=name, size=buffer_size))
        atexit.register(shm.destroy)
        return shm
    
    @staticmethod
    def connect(name: str):
        """ Connect to existing shared memory block """
        shm = SharedMemoryBlock(shared_memory.SharedMemory(name=name))
        atexit.register(shm.disconnect)
        return shm

    def clear(self):
        self._shm.buf[:len(self._shm.buf)] = b'\x00' * len(self._shm.buf)

    def read(self):
        return bytes(self._shm.buf)
    
    def read_text(self):
        return self.read().rstrip(b'\x00').decode('utf-8')

    def write(self, bytes: bytes):
        if len(bytes) > len(self._shm.buf):
            raise ValueError("Data is too large for shared memory buffer.")
        self.clear()
        self._shm.buf[:len(bytes)] = bytes

    def write_text(self, text: str):
        bytes = text.encode('utf-8')
        self.write(bytes)
    
    def disconnect(self):
        self._shm.close()
    
    def destroy(self):
        self.disconnect()
        self._shm.unlink()


def open_dialog_box(scriptDir, filetypes = [('All files', '*')], initialdir = '', title = '', multiple = False):
    ''' Shortcut function to prompt a openfile dialog box
        type_list : list of types allowed for the open dialog box
            format : ('{File dormat description}', '*.{file extension}') 
            exemple : ('RKG files', '*.rkg')              '''   

    #Todo : maybe having the text as a subprocess check_output argument instead of SharedMemory, but idk how to implement it
    script_path = os.path.join(scriptDir, "external", 'open_file_dialog_box.py')
    type_writer = SharedMemoryWriter('open_file_dialog', 1024)
    str_list = []
    for type_ in filetypes:
        str_list.append(','.join(type_))
    type_writer.write_text(';'.join(str_list) + '|' + initialdir + '|' + title + '|' + str(multiple))
    filename = subprocess.check_output(["python", script_path], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    type_writer.close()
    return filename

def save_dialog_box(scriptDir, filetypes = [('All files', '*')], initialdir = '', title = '', defaultextension = ''):
    ''' Shortcut function to prompt a savefile dialog box
        type_list : list of types allowed for the open dialog box
            format : ('{File dormat description}', '*.{file extension}') 
            exemple : ('RKG files', '*.rkg')              '''   

    #Todo : maybe having the text as a subprocess check_output argument instead of SharedMemory, but idk how to implement it
    script_path = os.path.join(scriptDir, "external", 'save_file_dialog_box.py')
    type_writer = SharedMemoryWriter('save_file_dialog', 1024)
    str_list = []
    for type_ in filetypes:
        str_list.append(','.join(type_))
    type_writer.write_text(';'.join(str_list) + '|' + initialdir + '|' + title + '|' + defaultextension)
    filename = subprocess.check_output(["python", script_path], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    type_writer.close()
    return filename

#The 2 following functions are used to save and restore
#various tkinter settings
def save_external_setting(config_file, setting_name, setting_value):
    ''' Param : config_file : str, filename of the savefile
                setting_name : str, unique name of the setting (used as a key in the config file)
                setting_value : str, value of the setting'''
    
    #create an empty file if it doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            pass

    config = configparser.ConfigParser()
    config.read(config_file)
    if not config.sections():
        config["SETTINGS"] = {}
    config["SETTINGS"][setting_name] = setting_value

    with open(config_file, 'w') as f:
        config.write(f)
    
def load_external_setting(config_file, setting_name):
    ''' Param : config_file : str, filename of the savefile
                setting_name : str, unique name of the setting (used as a key in the config file)'''
    
    if not os.path.exists(config_file):
        return None
    config = configparser.ConfigParser()
    config.read(config_file)
    if not config.sections():
        return None
    if config["SETTINGS"].get(setting_name):
        return config["SETTINGS"].get(setting_name)
    return None
   
