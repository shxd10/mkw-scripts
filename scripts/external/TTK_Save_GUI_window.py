from tkinter import *
from tkinter import ttk, filedialog
from math import floor
import external_utils as ex
from random import randint
from datetime import datetime


global save_button_row
global misscount
save_button_row = 5
misscount = 0

af_text = ['How did you get there ?', 'what.', 'Huh WTF ?', 'Keep trying', 'Almost!', 'Bad QM', 'Not this time', 'Cmon already', "It's just 20%", 'You can do it!', "You can't do it!",  'Just a little more', 'Is it really that hard to click on a button ?', 'Even my grandma can do it', 'How many messages are there ?', 'I wonder if there is something special at the end...', "(Spoiler : there isn't", ")*", "forgot the bracket, oops", 'Unless there is actually something ...', "It's starting to get very long", "You had about 1.5% chance to get that far", "There is no end btw, you just need luck", "You should get it in average every 6 tries", "Okay I'll tell you something", "Soon", "In like just a few messages", "It's a cool hidden feature", "Nothing incredible, but still cool to know", "Fact 1 : press S on the connect4 ending screen to access settings", "Fact 2 : You can play whenever you want the connect4 game !", 'Fact 2 (part 2) : Just launch "special.py" in Scripts/external', 'This is the end of the messages', 'Good luck if you are still trying to save your TTK inputs lol']

def write_state(_ = None):
    if source_combobox.get():
        std_text = source_combobox.get()
        if std_text == 'File':
            std_text = source_file_text.get(1.0, END).split('\n')[0]
        if csv_player_var.get():
            std_text += '|' + 'csv_player'
        if csv_ghost_var.get():
            std_text += '|' + 'csv_ghost'
        if dest_file_var.get():
            std_text += '|' + dest_file_text.get(1.0, END).split('\n')[0]
        print(std_text, end = '')
        root.destroy()
    else:
        status_label['text'] = 'Select a source to save'
def tp(_=None):
    global save_button_row
    global misscount
    d = datetime.now()
    a = randint(0,5)
    if a == save_button_row or d.day != 1 or d.month != 4:
        misscount = 0
        write_state()
    else:
        save_button_row = a
        misscount += 1
        if misscount < len(af_text):            
            status_label['text'] = af_text[misscount]
        save_button.grid(column=1, row=a)



root = Tk()
root.title('TTK Save')
root.wm_attributes('-topmost', 1) #Always on top

content = ttk.Frame(root, padding = 10)

dialog_frame = ttk.Frame(content, padding = 5)
dialog_frame.grid(column = 0, row = 0, rowspan = 6)



csv_pick_var = StringVar()
rkg_pick_var = StringVar()


save_label = ttk.Label(dialog_frame, text = 'Save ')
save_label.grid(column = 0, row = 0, rowspan = 4)


source_var = StringVar() 
source_file_text = Text(dialog_frame, height = 4, width = 20, state = 'disabled')
source_file_text.grid(column=1, row=5, sticky='w')
source_combobox = ttk.Combobox(dialog_frame, textvariable=source_var, values = ('Player Inputs', 'Ghost Inputs', 'CSV Player', 'CSV Ghost', 'File'), state = 'readonly')
def source_ask_open_file(_ = None):
    if source_combobox.get() == 'File':
        filename = filedialog.askopenfilename(parent = dialog_frame,
                                                title = 'Open an input file',
                                              filetypes = [('RKG Files', '*.rkg'), ('CSV Files', '*.csv'), ('All Files', '*')])
        if filename == '':
            source_combobox.set('Player Inputs')
        else:
            source_file_text['state'] = 'normal'
            source_file_text.delete(1.0, END)
            source_file_text.insert(END, filename)
            source_file_text['state'] = 'disabled'
    else:
        source_file_text['state'] = 'normal'
        source_file_text.delete(1.0, END)
        source_file_text['state'] = 'disabled'
        
source_combobox.bind('<<ComboboxSelected>>', source_ask_open_file)
source_combobox.grid(column=1, row=0, rowspan = 4)

to_label = ttk.Label(dialog_frame, text = ' to ')
to_label.grid(column = 2, row = 0, rowspan = 4)

csv_player_var = BooleanVar(value=False)
csv_player_button = ttk.Checkbutton(dialog_frame, text="CSV Player", variable=csv_player_var, onvalue=True)
csv_player_button.grid(column=4, row=0, sticky='w')

csv_ghost_var = BooleanVar(value=False)
csv_ghost_button = ttk.Checkbutton(dialog_frame, text="CSV Ghost", variable=csv_ghost_var, onvalue=True)
csv_ghost_button.grid(column=4, row=1, sticky='w')

dest_file_var = BooleanVar(value=False)
dest_file_text = Text(dialog_frame, height = 4, width = 20, state = 'disabled')
dest_file_text.grid(column=3, row=5, columnspan=2)
def dest_ask_save_file(_=None):
    if dest_file_var.get():
        filename = filedialog.asksaveasfilename(parent = dialog_frame, defaultextension = '.rkg',
                                                title = 'Save to an input file',
                                              filetypes = [('RKG Files', '*.rkg'), ('CSV Files', '*.csv'), ('All Files', '*')])
        if filename == '':
            dest_file_var.set(False)
        else:
            dest_file_text['state'] = 'normal'
            dest_file_text.delete(1.0, END)
            dest_file_text.insert(END, filename)
            dest_file_text['state'] = 'disabled'
    else:
        dest_file_text['state'] = 'normal'
        dest_file_text.delete(1.0, END)
        dest_file_text['state'] = 'disabled'

dest_file_button = ttk.Checkbutton(dialog_frame, text="File", variable=dest_file_var, onvalue=True, command=dest_ask_save_file)
dest_file_button.grid(column=4, row=2, sticky='w')

save_button = ttk.Button(content, text='Save', command=tp)
save_button.grid(column=2, row=save_button_row )

status_label = ttk.Label(content, text='')
status_label.grid(column=0, row=7 )


content.grid(column=0, row=0)

root.mainloop()

