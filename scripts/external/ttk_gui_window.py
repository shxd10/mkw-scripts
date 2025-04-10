import tkinter as tk
from tkinter import ttk  # lol
import os
import struct
import external_utils as ex

# This constant determines how the buttons are arranged.
# Ex: BUTTON_LAYOUT[section_index][row_index][column_index]
BUTTON_LAYOUT = [
    [
        ["Load from Player", "Load from Ghost"],
        ["Save to RKG", "Load from RKG"],
        ["Open in Editor", "Load from CSV"],
    ],
    [
        ["Load from Player", "Load from Ghost"],
        ["Save to RKG", "Load from RKG"],
        ["Open in Editor", "Load from CSV"],
    ],
]

def main():
    try:
        shm_activate = ex.SharedMemoryBlock.connect(name="ttk_gui_activate")
        shm_buttons = ex.SharedMemoryBlock.connect(name="ttk_gui_buttons")
        shm_player_csv = ex.SharedMemoryReader(name="ttk_gui_player_csv")
        shm_ghost_csv = ex.SharedMemoryReader(name="ttk_gui_ghost_csv")
        shm_close_event = ex.SharedMemoryBlock.connect(name="ttk_gui_window_closed")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Shared memory buffer '{e.filename}' not found. Make sure the `TTK_GUI` script is enabled.")

    window = tk.Tk()
    window.title("TAS Toolkit GUI")
    window.geometry("500x250")
    # window.attributes('-topmost',True)
    
    root_frame = ttk.Frame(window)
    root_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Checkboxes state
    activate_state = [tk.BooleanVar(), tk.BooleanVar()]
    def on_checkbox_change():
        shm_activate.write(struct.pack('>??', *[var.get() for var in activate_state]))
    
    # File name display state
    player_csv = tk.StringVar(value=f"File : {os.path.basename(shm_player_csv.read_text())}")
    ghost_csv = tk.StringVar(value=f"File : {os.path.basename(shm_ghost_csv.read_text())}")

    # Construct page layout
    for section_index, section_title in enumerate(["Player Inputs", "Ghost Inputs"]):
        section_frame = ttk.LabelFrame(root_frame, text=section_title)
        section_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        ttk.Checkbutton(section_frame, text="Activate", variable=activate_state[section_index], command=on_checkbox_change) \
            .pack(pady=5)
        
        ttk.Label(section_frame, textvariable=[player_csv, ghost_csv][section_index]) \
            .pack(pady=5)

        for row_index, row in enumerate(BUTTON_LAYOUT[section_index]):
            btn_row_frame = ttk.Frame(section_frame)
            btn_row_frame.pack(pady=5)

            for col_index, btn_text in enumerate(row):
                button_data = struct.pack('>?BBB', True, section_index, row_index, col_index)
                def on_click(data=button_data):
                    shm_buttons.write(data)
                ttk.Button(btn_row_frame, text=btn_text, command=on_click, width=15) \
                    .pack(side=tk.LEFT, padx=5)
    
    # Function that runs repeatedly while window is open
    def loop_actions():
        new_text = shm_player_csv.read_text()
        if new_text:
            player_csv.set(f"File : {os.path.basename(new_text)}")
        
        new_text = shm_ghost_csv.read_text()
        if new_text:
            ghost_csv.set(f"File : {os.path.basename(new_text)}")
        
        window.after(ms=10, func=loop_actions)

    shm_close_event.write_text("0")
    
    window.after(ms=0, func=loop_actions)
    window.mainloop()

    #This part of the code is only accessed when the window has been closed
    shm_close_event.write_text("1")


if __name__ == '__main__':
    main()
