import struct
import external_utils as ex
import tkinter as tk
from tkinter import filedialog
import pygame

WINDOW_SIZE = 480
SCALE = WINDOW_SIZE/480*100/120/30

def bytes_to_poslist(b):
    p_list = []
    g_list = []
    for i in range(0,len(b),16):
        if i+15 < len(b):
            struct.unpack('f', b[i:i+4])
            p_list.append((struct.unpack('f', b[i:i+4])[0], struct.unpack('f', b[i+4:i+8])[0]))
            g_list.append((struct.unpack('f', b[i+8:i+12])[0], struct.unpack('f', b[i+12:i+16])[0]))
    if not p_list:
        p_list.append((0,0))
        g_list.append((0,0))
    return p_list, g_list


def format_position(position, base_position, scaling, yaw = 0):
    ''' translate and scale and rotate the position
        the base position is mapped to the middle of the screen '''
    x,y = position
    x0, y0 = base_position
    x -= x0
    y -= y0
    x*= scaling
    y*= scaling
    #todo rotate
    x += screen.get_width()/2
    y += screen.get_height()/2
    return x,y

def is_inbound(coordinate):
    x,y = coordinate
    return 0<=x<=screen.get_width() and 0<=y<=screen.get_height()

memory_reader = ex.SharedMemoryReader('mkds minimap')
pygame.init()
screen = pygame.display.set_mode((480, 480))
clock = pygame.time.Clock()
running = True
dt = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    player_positions, ghost_positions = bytes_to_poslist(memory_reader.read())
    base_position = player_positions[0]

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    #Draw player red circle
    pygame.draw.circle(screen, "red", (screen.get_width()/2, screen.get_height()/2), 4)

    #Draw ghost blue circle
    ghost_pos = format_position(ghost_positions[0], base_position, SCALE)
    if is_inbound(ghost_pos):
        pygame.draw.circle(screen, "blue", ghost_pos, 4)
        
    for i in range(len(player_positions) -1):
        p1 = format_position(player_positions[i], base_position, SCALE)
        p2 = format_position(player_positions[i+1], base_position, SCALE)
        if is_inbound(p1) and is_inbound(p2):
            pygame.draw.line(screen, "red", p1, p2)
    for i in range(len(ghost_positions) -1):
        p1 = format_position(ghost_positions[i], base_position, SCALE)
        p2 = format_position(ghost_positions[i+1], base_position, SCALE)
        if is_inbound(p1) and is_inbound(p2):
            pygame.draw.line(screen, "blue", p1, p2)    

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
memory_reader.close_with_writer()

