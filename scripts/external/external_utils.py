from multiprocessing import shared_memory
import atexit
import subprocess
import os


def start_external_script(path: str):
    process = subprocess.Popen(["python", path], creationflags=subprocess.CREATE_NO_WINDOW)
    atexit.register(process.terminate)


def run_external_script(path: str):
    output = subprocess.check_output(["python", path], text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return output


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
