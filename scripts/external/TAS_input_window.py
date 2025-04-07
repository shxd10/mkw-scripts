from tkinter import *
from tkinter import ttk
from math import floor
import external_utils as ex

input_writer = ex.SharedMemoryWriter('mkw tas input', 30, False)

def convert_drift(t):
    if t ==  'Auto':
        return '-1'
    else:
        return t
def convert_trick(t):
    if t == 'Up':
        return '1'
    if t == 'Down':
        return '2'
    if t == 'Left':
        return '3'
    if t == 'Right':
        return '4'
    return '0'
    
def write_state(_ = None):
    a = ','.join([str(int(Avar.get())),
     str(int(Bvar.get())),
     str(int(Lvar.get())),
     convert_drift(drift_button.get()),
     str(int(BDvar.get())),
     str(floor(float(x_stick.get()))),
     str(floor(float(y_stick.get()))),
     convert_trick(trick_button.get())])
    input_writer.write_text(a)

root = Tk()
root.title('TAS Input')
root.wm_attributes('-topmost', 1) #Always on top

content = ttk.Frame(root, padding = 10)

Avar = BooleanVar(value=False)
Bvar = BooleanVar(value=False)
Lvar = BooleanVar(value=False)
Xvar = StringVar()
Yvar = StringVar()
Tvar = StringVar()
Dvar = StringVar()
BDvar = BooleanVar(value=False)

a_button = ttk.Checkbutton(content, text="A", variable=Avar, onvalue=True, command=write_state)
b_button = ttk.Checkbutton(content, text="B", variable=Bvar, onvalue=True, command=write_state)
l_button = ttk.Checkbutton(content, text="ITEM", variable=Lvar, onvalue=True, command=write_state)
bd_button = ttk.Checkbutton(content, text="BRAKEDRIFT", variable=BDvar, onvalue=True, command=write_state)

x_label = ttk.Label(content, text='X = 0')
def update_x_label(x):
    write_state()
    x_label['text'] = 'X = '+str(floor(float(x)))
x_stick = ttk.Scale(content, orient=HORIZONTAL, length=150, from_=-6.5, to=7.5, variable=Xvar, command=update_x_label)


y_label = ttk.Label(content, text='Y = 0')
def update_y_label(x):
    write_state()
    y_label['text'] = 'Y = '+str(floor(float(x)))
y_stick = ttk.Scale(content, orient=HORIZONTAL, length=150, from_=-6.5, to=7.5, variable=Yvar, command=update_y_label)


trick_button = ttk.Combobox(content, textvariable=Tvar, values = ('None', 'Up', 'Left', 'Right', 'Down'), state = 'readonly')
trick_button.bind('<<ComboboxSelected>>', write_state)
trick_label = ttk.Label(content, text='Trick :')


drift_button = ttk.Combobox(content, textvariable=Dvar, values = ('Auto', '0', '1'), state = 'readonly')
drift_button.bind('<<ComboboxSelected>>', write_state)
drift_label = ttk.Label(content, text='Drift :')
drift_disclaimer = ttk.Label(content, text='Use Auto if unsure')

drift_button.set('Auto')
trick_button.set('None')
x_stick.set(0.5)
y_stick.set(0.5)

content.grid(column=0, row=0)
a_button.grid(column=0, row=3, sticky='w')
b_button.grid(column=0, row=4, sticky='w')
l_button.grid(column=0, row=5, sticky='w')
x_stick.grid(column=1, row=6, columnspan=2)
x_label.grid(column=0, row=6, sticky='w')
y_label.grid(column=0, row=10, sticky='w')
y_stick.grid(column=1, row=10, columnspan=2)
trick_button.grid(column=1, row=11, sticky='w')
trick_label.grid(column=0, row=11, sticky='w')
drift_button.grid(column=1, row=12, sticky='w')
drift_label.grid(column=0, row=12, sticky='w')
drift_disclaimer.grid(column=2, row=12, sticky='e')
bd_button.grid(column=0, row=13, sticky='w')

root.mainloop()

input_writer.close()
