import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for compatibility

import matplotlib.pyplot as plt
import struct
import external_utils

# Connect to shared memory block
shm_reader = external_utils.SharedMemoryReader(name="graphdata")
current_frame = 0
max_height = 0

# Initialize data storage
x_data = []
y_data_xyz = []
y_data_xz = []

MAX_FRAMES = 200
MIN_HEIGHT = 75

# Create a figure and axis
fig, ax = plt.subplots(figsize=(5, 4))
xyz_line, = ax.plot([], [], label="XYZ")
# xyz_line.set_color('orange')
xz_line, = ax.plot([], [], label="XZ")
# xz_line.set_color('lightblue')



# Configure plot
ax.set_xlim(0, MAX_FRAMES)
ax.set_ylim(0, MIN_HEIGHT)  # Fixed y-axis range for sine wave
ax.set_xlabel('Frame')
ax.set_ylabel('Units')
ax.set_title('External Velocity')
ax.legend()
ax.grid(True)

# Enable interactive mode and show the window
plt.ion()
plt.show(block=False)

# Draw and create the background after showing the window
fig.canvas.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)

# Event handler to exit when window is closed
running = True
def on_close(event):
    global running
    running = False
fig.canvas.mpl_connect('close_event', on_close)

try:
    while running:
        # Read new data point
        new_data = shm_reader.read()
        frame, ev_xyz, ev_xz = struct.unpack('>Iff', new_data[:12])

        if frame == current_frame:
            fig.canvas.flush_events()
            continue
        elif frame < current_frame:
            try:
                cutoff = x_data.index(frame)
                x_data = x_data[:cutoff]
                y_data_xyz = y_data_xyz[:cutoff]
                y_data_xz = y_data_xz[:cutoff]
            except ValueError:
                x_data.clear()
                y_data_xyz.clear()
                y_data_xz.clear()
        
        current_frame = frame
        max_height = max(max_height, ev_xyz)

        # Append new data
        x_data.append(frame)
        y_data_xyz.append(ev_xyz)
        y_data_xz.append(ev_xz)

        # Avoid memory overflow
        if len(x_data) > MAX_FRAMES:
            x_data.pop(0)
            y_data_xyz.pop(0)
            y_data_xz.pop(0)

        # Update the line data
        xyz_line.set_xdata(x_data)
        xyz_line.set_ydata(y_data_xyz)
        xz_line.set_xdata(x_data)
        xz_line.set_ydata(y_data_xz)

        # Automatically adjust axes to fit data
        ax.set_xlim(max(0, frame - MAX_FRAMES), max(frame, MAX_FRAMES))
        ax.set_ylim(0, max(max_height + 10, MIN_HEIGHT))

        # Restore the background, draw the line, and blit
        fig.canvas.restore_region(background)
        ax.draw_artist(xyz_line)
        ax.draw_artist(xz_line)
        fig.canvas.blit(ax.bbox)
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("Real-time plotting stopped.")
