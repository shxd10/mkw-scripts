import struct
import external_utils as ex
import pygame
import math

WINDOW_SIZE = 480
SCALE = 1*WINDOW_SIZE/480*100/120/30
FONT_SIZE = 15

def bytes_to_poslist(b):
    p_list = []
    g_list = []
    for i in range(0,len(b),16):
        if i+15 < len(b):
            struct.unpack('f', b[i:i+4])
            p_list.append((struct.unpack('f', b[i:i+4])[0], struct.unpack('f', b[i+4:i+8])[0]))
            g_list.append((struct.unpack('f', b[i+8:i+12])[0], struct.unpack('f', b[i+12:i+16])[0]))
    if len(p_list) == 0:
        p_list.append((0,0))
    if len(g_list) == 0:
        g_list.append((0,0))
    return p_list, g_list

def bytes_to_idlist(b):
    res = []
    for i in range(len(b)):
        res.append(struct.unpack('b', b[i:i+1])[0])
    return res
    

def format_position(position, base_position, scaling, yaw = 180):
    ''' translate and scale and rotate the position
        from MKW coordinate to pygame screen coordinate
        the base position is mapped to the middle of the screen '''
    yaw *= -math.pi/180
    x,y = position
    x0, y0 = base_position
    x -= x0
    y -= y0
    x*= SCALE * scaling
    y*= SCALE * scaling
    x,y = -x*math.cos(yaw) + y*math.sin(yaw), -x*math.sin(yaw) - y*math.cos(yaw)
    x += screen.get_width()/2
    y += screen.get_height()/2
    return x,y

def is_inbound(coordinate):
    x,y = coordinate
    return 0<=x<=screen.get_width() and 0<=y<=screen.get_height()
 
memory_reader = ex.SharedMemoryReader('mkds minimap')
cp_reader = ex.SharedMemoryReader('mkds minimap checkpoints')
cp_id_reader = ex.SharedMemoryReader('mkds minimap checkpoints_id')
yaw_reader = ex.SharedMemoryReader('mkds minimap yaw')
pygame.init()
screen = pygame.display.set_mode((480, 480), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True
dt = 0
scale_mult = 1
draw_line = True
draw_circle = True
draw_help = True
align_with_yaw = True
help_font = pygame.font.SysFont('Courier New', FONT_SIZE)
pygame.key.set_repeat(300, 50)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            draw_help = not draw_help
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            scale_mult *= 1.1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            scale_mult /= 1.1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            draw_line = not draw_line
        if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            draw_circle = not draw_circle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            align_with_yaw = not align_with_yaw
        

    player_positions, ghost_positions = bytes_to_poslist(memory_reader.read())
    cp_left, cp_right = bytes_to_poslist(cp_reader.read())
    id_list = bytes_to_idlist(cp_id_reader.read())
    base_position = player_positions[0]
    yaw = struct.unpack('f', yaw_reader.read()[:4])[0]
    if not align_with_yaw:
        yaw = 180
    #hacky way to get rid of some unwanted data
    for i in range(len(cp_left)-1, -1, -1):
        if (cp_right[i][0] == 0 or cp_left[i][0] == 0):
            cp_right.pop(i)
            cp_left.pop(i)
            id_list.pop(i)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    #Draw help
    if draw_help:
        screen.blit(help_font.render('Help - Keybinds', False, (0, 255, 0)), (0,0))
        screen.blit(help_font.render('Toggle help : h', False, (0, 255, 0)), (0,FONT_SIZE))
        screen.blit(help_font.render('Zoom in : b', False, (0, 255, 0)), (0,FONT_SIZE*2))
        screen.blit(help_font.render('Zoom out : n', False, (0, 255, 0)), (0,FONT_SIZE*3))
        screen.blit(help_font.render('Draw path dots : k', False, (0, 255, 0)), (0,FONT_SIZE*4))
        screen.blit(help_font.render('Draw path lines : j', False, (0, 255, 0)), (0,FONT_SIZE*5))
        screen.blit(help_font.render('Rotate with facing yaw : l', False, (0, 255, 0)), (0,FONT_SIZE*6))
    #Draw player red circle
    player_pos = format_position(player_positions[0], base_position, scale_mult, yaw)
    pygame.draw.circle(screen, "red", player_pos, 4)

    #Draw ghost blue circle
    ghost_pos = format_position(ghost_positions[0], base_position, scale_mult, yaw)
    pygame.draw.circle(screen, "blue", ghost_pos, 4)

    #Draw Player Path   
    for i in range(0, len(player_positions) -1):
        if not (player_positions[i+1][0] == 0):            
            p1 = format_position(player_positions[i], base_position, scale_mult, yaw)
            p2 = format_position(player_positions[i+1], base_position, scale_mult, yaw)
            if draw_line:
                pygame.draw.line(screen, "red", p1, p2)
            if draw_circle:
                pygame.draw.circle(screen, "red", p1, 2)
    #Draw Ghost Path
    for i in range(len(ghost_positions) -1):
        if not (ghost_positions[i+1][0] == 0): 
            p1 = format_position(ghost_positions[i], base_position, scale_mult, yaw)
            p2 = format_position(ghost_positions[i+1], base_position, scale_mult, yaw)
            if draw_line:
                pygame.draw.line(screen, "blue", p1, p2)
            if draw_circle:
                pygame.draw.circle(screen, "blue", p1, 2)
    #Draw CP box
    for i in range(len(cp_left)):
        if id_list[i] == -1:
            color = 'black'
        elif id_list[i] == 0:
            color = 'purple'
        elif id_list[i] > 0:
            color = 'red'
        p1 = format_position(cp_left[i], base_position, scale_mult, yaw)
        p2 = format_position(cp_left[(i+1)%len(cp_left)], base_position, scale_mult, yaw)
        pygame.draw.line(screen, color, p1, p2) #left side of the box
        p1 = format_position(cp_right[i], base_position, scale_mult, yaw)
        p2 = format_position(cp_right[(i+1)%len(cp_left)], base_position, scale_mult, yaw)
        pygame.draw.line(screen, color, p1, p2) #right side of the box
        p1 = format_position(cp_left[i], base_position, scale_mult, yaw)
        p2 = format_position(cp_right[i], base_position, scale_mult, yaw)
        pygame.draw.line(screen, color, p1, p2) #cp line
        

        
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
memory_reader.close_with_writer()
cp_reader.close_with_writer()
cp_id_reader.close_with_writer()
yaw_reader.close_with_writer()
