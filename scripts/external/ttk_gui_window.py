import tkinter as tk
from tkinter import ttk  # lol
from tkinter import filedialog
import tksheet
import csv
import struct
import external_utils as ex

def open_file():
    return filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

def save_file():
    return filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])


BUTTON_LAYOUT = [
    ["Load from Player", "Load from Ghost"],
]

def main():
    shm_activate = ex.SharedMemoryBlock.connect(name="ttk_gui_activate")
    shm_buttons = ex.SharedMemoryBlock.connect(name="ttk_gui_buttons")

    window = tk.Tk()
    window.title("TAS Toolkit GUI")
    window.geometry("500x250")
    
    root_frame = ttk.Frame(window)
    root_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    activate_state = [tk.BooleanVar(), tk.BooleanVar()]
    def on_checkbox_change():
        shm_activate.write(struct.pack('>??', *[var.get() for var in activate_state]))

    for section_index, section_title in enumerate(["Player Inputs", "Ghost Inputs"]):
        section_frame = ttk.LabelFrame(root_frame, text=section_title)
        section_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        ttk.Checkbutton(section_frame, text="Activate", variable=activate_state[section_index], command=on_checkbox_change) \
            .pack(pady=5)
        
        ttk.Label(section_frame, text="File: [placeholder]")

        for row_index, row in enumerate(BUTTON_LAYOUT):
            btn_row_frame = ttk.Frame(section_frame)
            btn_row_frame.pack(pady=5)

            for col_index, btn_text in enumerate(row):
                button_data = struct.pack('>?BBB', True, section_index, row_index, col_index)
                def on_click(data=button_data):
                    shm_buttons.write(data)
                ttk.Button(btn_row_frame, text=btn_text, command=on_click) \
                    .pack(side=tk.LEFT, padx=5)
    
    window.mainloop()


def _spreadsheet_test():
    window = tk.Tk()
    window.title('TTK Deluxe')
    window.config(bg="grey")
    window.geometry('330x600')

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    frame = tk.Frame(window)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    with open('../MKW_Inputs/bridge.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

    sheet = tksheet.Sheet(frame, data=[])
    sheet.enable_bindings()
    frame.grid(row=0, column=0, sticky="nswe")
    sheet.grid(row=0, column=0, sticky="nswe")

    window.mainloop()


if __name__ == '__main__':
    main()