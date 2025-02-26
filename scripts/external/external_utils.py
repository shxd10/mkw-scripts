from multiprocessing import shared_memory
import atexit
import subprocess


def start_external_script(path: str):
    process = subprocess.Popen(["python", path], creationflags=subprocess.CREATE_NO_WINDOW)
    atexit.register(process.terminate)


class SharedMemoryWriter:
    def __init__(self, name: str, buffer_size: int):
        self._shm = shared_memory.SharedMemory(create=True, name=name, size=buffer_size)
        atexit.register(self.close)

    def write(self, bytes: bytes):
        if len(bytes) > len(self._shm.buf):
            raise ValueError("Data is too large for shared memory buffer.")
        self._shm.buf[:len(self._shm.buf)] = b'\x00' * len(self._shm.buf)
        self._shm.buf[:len(bytes)] = bytes

    def write_text(self, text: str):
        bytes = text.encode('utf-8')
        self.write(bytes)

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
