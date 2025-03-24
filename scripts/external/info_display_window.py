import tkinter
import external_utils
import time

# Fix blurry text
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)


def main():
    try:
        shm_reader = external_utils.SharedMemoryReader(name='infodisplay')
        print("Connected to shared data")
    except FileNotFoundError:
        raise FileNotFoundError("Shared memory buffer not found. Make sure the `external_info_display` script is enabled.")

    window = tkinter.Tk()
    window.title('Infodisplay')
    window.config(bg="black")
    window.geometry('330x600')

    display_text = tkinter.StringVar()

    label = tkinter.Label(
        textvariable=display_text,
        anchor='nw',
        font=('Courier', '9'),
        justify='left',
        width=250,
        fg='white',
        bg='black',
    )
    label.pack(padx=5, pady=5)

    try:
        while True:
            new_text = shm_reader.read_text()
            if new_text and new_text != display_text.get():
                display_text.set(new_text)

            window.update_idletasks()
            window.update()
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Reader stopped.")

    finally:
        shm_reader.close()
        print("Disconnected from shared data")


if __name__ == '__main__':
    main()
