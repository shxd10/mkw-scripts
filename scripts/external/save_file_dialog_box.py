import struct
import external_utils
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

type_reader = external_utils.SharedMemoryReader('save_file_dialog')
reader_text = type_reader.read_text()
type_reader.close()

''' Example of types list format :
    "RKG files,*.rkg;CSV files,*.csv;All files,*"
    ";" separate all entries, and "," separate the name from the extension'''

temp = reader_text.split('|')
file_types = temp[0]
initialDir = temp[1]
title = temp[2]
defaultextension = temp[3]

types_list = file_types.split(';')
for i in range(len(types_list)):
    type_tuple = types_list[i].split(',')
    types_list[i] = (type_tuple[0], type_tuple[1])


file_path = filedialog.asksaveasfilename(title = title,
                                       filetypes = types_list,
                                       initialdir = initialDir,
                                       defaultextension = defaultextension)


print(file_path, end='')

