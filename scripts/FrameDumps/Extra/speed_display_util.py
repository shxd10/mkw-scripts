import moviepy
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import sys
import os
import time
import subprocess
import math

from Extra import common

def get_color(color_text):
    n = int(color_text, 16)
    l = []
    for _ in range(4):
        l.append(n%256)
        n//=256
    l.reverse()
    return tuple(l)

def rotate_point(point, angle, center):
    angle *= -math.pi/180
    x,y = point
    x0, y0 = center
    x -= x0
    y -= y0
    x,y = x*math.cos(angle) - y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)
    x += x0
    y += y0
    return int(x),int(y)

def add_arrow(im, startpoint, vector, color, width, outline_color, outline_width, radius):
    arrow_image = Image.new('RGBA', (radius*2+1, radius*2+1), (255, 0, 0, 0))
    ID = ImageDraw.Draw(arrow_image)
    endpoint = (startpoint[0]+vector[0], startpoint[1]+vector[1])
    t = 0.85
    angle = 8
    mid_point = (startpoint[0]+vector[0]*t, startpoint[1]+vector[1]*t)
    left_point = rotate_point(mid_point, angle, startpoint)
    right_point = rotate_point(mid_point, -angle, startpoint)
    xy = [startpoint, endpoint]
    lyr = [left_point, endpoint, right_point]
    ID.line(xy, outline_color, outline_width+width, 'curve')
    ID.line(xy, color, width, 'curve')
    ID.line(lyr, outline_color, outline_width+width, 'curve')
    ID.line(lyr, color, width, 'curve')

    im.alpha_composite(arrow_image, (0,0))
    

def normalize_speed(vec, cap, ratio):
    magn = (vec[0]**2+vec[1]**2)**0.5
    if magn > cap:
        return vec[0]*ratio*cap/magn, vec[1]*ratio*cap/magn
    else:
        return vec[0]*ratio, vec[1]*ratio
    
def add_speed_display(im, d, config):
    c = config['Speed display']
    state, state_counter = int(d['state']), int(d['state_counter'])
    radius = c.getint('circle_radius')
    circle_color = get_color(c.get('circle_color'))
    circle_width = c.getint('circle_outline_width')
    cirlce_border_color = get_color(c.get('circle_outline_color'))
    center = (radius, radius)
    yaw = float(d['yaw'])+180
    speed_display_image = Image.new('RGBA', (radius*2+1, radius*2+1), (255, 0, 0, 0))

    #draw circle
    ID = ImageDraw.Draw(speed_display_image)
    ID.circle(center, 0.95*radius, fill = circle_color, outline = cirlce_border_color, width = circle_width)

    #draw axis
    if c.getboolean('draw_axis'):
        axis_color = get_color(c.get('axis_color'))
        axis_width = c.getint('axis_width')
        if c.getboolean('rotate_with_yaw'):            
            ID.line([rotate_point((0, radius), yaw, center), rotate_point((radius*2+1, radius), yaw, center)], axis_color, axis_width)
            ID.line([rotate_point((radius, 0), yaw, center), rotate_point((radius, radius*2+1), yaw, center)], axis_color, axis_width)
        else:
            ID.line([center, rotate_point((radius, 0), -yaw, center)], axis_color, axis_width)
            ID.line([center, rotate_point((0, radius), -yaw, center)], axis_color, axis_width)
            ID.line([center, rotate_point((radius*2+1, radius), -yaw, center)], axis_color, axis_width)

    #draw pieslice
    if c.getboolean('draw_pieslice'):
        angle = 10
        pieslice_color = get_color(c.get('pieslice_color'))
        if c.getboolean('rotate_with_yaw'):            
            ID.pieslice([(0.2*radius, 0.2*radius), (1.8*radius, 1.8*radius)], 270-angle, 270+angle, pieslice_color)
        else:
            ID.pieslice([(0.2*radius, 0.2*radius), (1.8*radius, 1.8*radius)], 270-angle+yaw, 270+angle+yaw, pieslice_color)    

    #Get speed vectors      
    speed_activated = []
    for key in c.keys():
        if len(key) > 5 and key[:4] == 'show' and key != 'show_speed_display' and c.getboolean(key):
            speed_activated.append(key[5:])

    correspondance_dict = {"speed" : (float(d['spd_x']), float(d['spd_z'])),
                            "iv" : (float(d['iv_x']), float(d['iv_z'])),
                            "ev" : (float(d['ev_x']), float(d['ev_z']))}

    #Normalize to screen pixel size
    top_speed = c.getint('cap_speed')
    ratio = 0.95*radius/top_speed
    speed_vec_activated = [normalize_speed(correspondance_dict[txt], top_speed, ratio) for txt in speed_activated]
    if c.getboolean('rotate_with_yaw'):
        for i in range(len(speed_vec_activated)):
            speed_vec_activated[i] = rotate_point(speed_vec_activated[i], yaw, (0,0))

    #draw arrows
    arrow_width = c.getint('arrow_width')
    arrow_outline_width = c.getint('arrow_outline_width')
    arrow_outline_color = get_color(c.get('arrow_outline_color'))
    for i in range(len(speed_vec_activated)):
        color_key = 'color_'+speed_activated[i]
        color = get_color(c.get(color_key))
        spd_vec = speed_vec_activated[i]
        add_arrow(speed_display_image, center, spd_vec, color, arrow_width, arrow_outline_color, arrow_outline_width, radius)

    top_left_text = c.get('top_left').split(',')
    top_left = round(float(top_left_text[0])*im.width), round(float(top_left_text[1])*im.height)

    if config['Encoding options'].get('animation_style') == 'fly_in':
        fly_in_mode = c.get('fly_in_')
        ITEM_POSITION = 381/1440    # the box where you see the item, idk how else to call it. Its what I used to measure the fly in animations. the distance to the top was this ratio
        SPEED_DISPLAY_POSITION = (1 - float(top_left_text[1]))
        height_correction =  round((SPEED_DISPLAY_POSITION - ITEM_POSITION)*im.height)
        
        if state == 4 and state_counter >= 192 or state == 1 and state_counter <= 10:
            return Image.new('RGBA', (im.width, im.height), (0, 0, 0, 0))
        
        y_offset = common.fly_in(d, im.height)
        if y_offset is not None:
            if c.get('fly_in_direction') == 'bottom':
                im.alpha_composite(speed_display_image, (top_left[0], im.height - height_correction - y_offset))
            else:
                im.alpha_composite(speed_display_image, (top_left[0], top_left[1] - round(ITEM_POSITION*im.height) + y_offset))
        else:
            im.alpha_composite(speed_display_image, top_left)
    else:
        speed_display_image = common.fade_image_manually(speed_display_image, d)
        im.alpha_composite(speed_display_image, top_left)
    