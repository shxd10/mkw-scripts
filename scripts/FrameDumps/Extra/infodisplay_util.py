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


def make_text_key(d, c, font, key):
    text_key = 'text'+key[4:]

    if key == 'show_speed_xyz':
        val = (float(d['spd_x']) ** 2 + float(d['spd_y']) ** 2 + float(d['spd_z']) ** 2)**0.5
    elif key == 'show_speed_xz':
        val = (float(d['spd_x']) ** 2 + float(d['spd_z']) ** 2)**0.5
    elif key == 'show_speed_y':
        val = float(d['spd_y'])
    elif key == 'show_iv_xyz':
        val = (float(d['iv_x']) ** 2 + float(d['iv_y']) ** 2 + float(d['iv_z']) ** 2)**0.5
    elif key == 'show_iv_xz':
        val = (float(d['iv_x']) ** 2 + float(d['iv_z']) ** 2)**0.5
    elif key == 'show_iv_y':
        val = float(d['iv_y'])
    elif key == 'show_ev_xyz':
        val = (float(d['ev_x']) ** 2 + float(d['ev_y']) ** 2 + float(d['ev_z']) ** 2)**0.5
    elif key == 'show_ev_xz':
        val = (float(d['ev_x']) ** 2 + float(d['ev_z']) ** 2)**0.5
    elif key == 'show_ev_y':
        val = float(d['ev_y'])
    elif key == 'show_frame_count':
        val = float(d['frame_of_input'])

    prefix_text = c[text_key]
    if prefix_text[0] in ['.', '"']:
        prefix_text = prefix_text[1:]
    if prefix_text[-1] in ['.', '"']:
        prefix_text = prefix_text[:-2]
    return f'{prefix_text}{val:.2f}'
    

def add_infodisplay(image, id_dict, id_config, font_folder):

    infodisplay_layer = Image.new('RGBA', image.size, (0,0,0,0))
    ID = ImageDraw.Draw(infodisplay_layer)
    
    top_left_text = id_config.get('top_left').split(',')
    top_left = round(float(top_left_text[0])*image.width), round(float(top_left_text[1])*image.height)
    current_h = top_left[1]
    spacing = 4
    font_size =  id_config.getint('font_size')
    font = ImageFont.truetype(os.path.join(font_folder, id_config.get('font')), font_size)
    outline_width = id_config.getint('outline_width')
    outline_color = common.get_color(id_config.get('outline_color'))
    
    for key in id_config.keys():
        if len(key) > 4 and key[:4] == 'show' and key != 'show_infodisplay' and id_config.getboolean(key):
            text = make_text_key(id_dict, id_config, font, key)
            color_text = id_config.get('color'+key[4:])
            color = common.get_color(color_text)
            ID.text( (top_left[0], current_h), text, fill = color, font = font, stroke_width = outline_width, stroke_fill = outline_color)
            current_h += spacing + font_size
            
    infodisplay_layer = common.fade_image_manually(infodisplay_layer, id_dict)
    image.alpha_composite(infodisplay_layer, (0,0))
    
