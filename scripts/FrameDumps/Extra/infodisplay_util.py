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

#credit to https://github.com/nkfr26/mkwii-text-generator-tkinter
width_offset_table = {"A" : -8, "B" :-16, "C" :-21, "D" :-16,
                      "E" :-16, "F" :-21, "G" :-18, "H" :-16,
                      "I" :-14, "J" :-16, "K" :-15, "L" :-14,
                      "M" :-17, "N" :-16, "O" :-13, "P" :-15,
                      "Q" :-12, "R" :-12, "S" :-16, "T" :-15,
                      "U" :-16, "V" :-12, "W" :-22, "X" :-22,
                      "Y" :-24, "Z" :-12, "+" :-32, "-" :-32,
                      "/" :-28, ":" : -1, "." : -1, "0" : -1,
                      "1" : -1, "2" : -1, "3" : -1, "4" : -1,
                      "5" : -1, "6" : -1, "7" : -1, "8" : -1,
                      "9" : -1, "&" :-32}


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
        prefix_text = prefix_text[:-1]
    return f'{prefix_text}',f'{val:.2f}'


def add_mkw_text(line_layer, x, text, mkw_font_dict, color, mkw_scaling):
    for letter in text:
        if letter in mkw_font_dict.keys():
            cur_letter = mkw_font_dict[letter].copy()
            channels = list(cur_letter.split())
            for i in range(4):
                channels[i] = channels[i].point(lambda x : round(x*color[i]/255))            
            cur_letter = Image.merge("RGBA", tuple(channels))
            line_layer.alpha_composite(cur_letter, (x,0))
            x += cur_letter.size[0] + round(width_offset_table[letter]*4*mkw_scaling)
        elif letter == '>' :
            x += round(10*mkw_scaling)
        elif letter == '<':
            x -= round(10*mkw_scaling)
        else:
            x += round(268*mkw_scaling) + round(4*mkw_scaling*-1) #Make spaces the exact same width as numbers
    return x


def add_mkw_font_line(id_layer, prefix, value, color, mkw_font_dict, anchor, mkw_scaling, anchor_style, invert_design):
    w,h = anchor
    if value == None or prefix == None:
        custom_text_layer = Image.new('RGBA', (id_layer.size[0], round(mkw_scaling*336)+1), (0,0,0,0))
        x = add_mkw_text(custom_text_layer, 0, prefix or value, mkw_font_dict, color, mkw_scaling)
        if anchor_style == 'right':
            id_layer.alpha_composite(custom_text_layer, (w-x,h))  # for pretty speedometer
        else:
            id_layer.alpha_composite(custom_text_layer, (w-x//2,h)) # for custom text
        return None
    
    line_layer = Image.new('RGBA', (id_layer.size[0], round(mkw_scaling*336)+1), (0,0,0,0))

    if invert_design and not prefix == '<>':
        text = value,prefix
    else:
        text = prefix,value

    left_x = 0
    middle_x = add_mkw_text(line_layer, left_x, text[0], mkw_font_dict, color, mkw_scaling)
    right_x = add_mkw_text(line_layer, middle_x, text[1], mkw_font_dict, color, mkw_scaling)

    if prefix == '<>':
        id_layer.alpha_composite(line_layer, (w-(middle_x+right_x)//2,h))
        return None
    
    if anchor_style == 'left':
        offset = left_x
    elif anchor_style == 'middle':
        offset = middle_x
    else:
        offset = right_x
    w -= offset

    id_layer.alpha_composite(line_layer, (w,h))


def add_infodisplay(image, id_dict, id_config, font_folder, mkw_font_dict):
    state, state_counter = int(id_dict['state']), int(id_dict['state_counter'])
    infodisplay_layer = Image.new('RGBA', image.size, (0,0,0,0))
    ID = ImageDraw.Draw(infodisplay_layer)
    mkw_scaling = eval(id_config.get('mkw_font_scaling'))/12
    top_left_text = id_config.get('anchor').split(',')
    top_left = round(float(top_left_text[0])*image.width), round(float(top_left_text[1])*image.height)
    current_h = top_left[1]
    spacing = id_config.getint('spacing')
    font_size =  id_config.getint('font_size')
    font_filename = os.path.join(font_folder, id_config.get('font'))
    if os.path.isfile(font_filename):        
        font = ImageFont.truetype(font_filename, font_size)
    else:
        font = None
    outline_width = id_config.getint('outline_width')
    outline_color = common.get_color(id_config.get('outline_color'))
    anchor_style = id_config.get('anchor_style')
    invert = id_config.getboolean('invert_text')


    if id_config.get('pretty_speedometer_type') in ('xyz', 'xz', 'iv'):
        custom_color = common.get_color(id_config.get('pretty_speedometer_color'))
        if id_config.get('pretty_speedometer_type') == 'xyz':
            val = (float(id_dict['spd_x']) ** 2 + float(id_dict['spd_y']) ** 2 + float(id_dict['spd_z']) ** 2)**0.5
        elif id_config.get('pretty_speedometer_type') == 'xz': 
            val = (float(id_dict['spd_x']) ** 2 + float(id_dict['spd_z']) ** 2)**0.5
        else: 
            val = (float(id_dict['iv_x']) ** 2 + float(id_dict['iv_y']) ** 2 + float(id_dict['iv_z']) ** 2)**0.5
        value_text = f'{val:.2f}'
        add_mkw_font_line(infodisplay_layer, None, value_text.upper(), custom_color, mkw_font_dict[0.2375], (round(0.932*image.width), round(0.862*image.height)), 0.2375, 'right', False)


    if id_config.getboolean('enable_custom_text'):
        i = 1
        while f'custom_text_{i}' in id_config:
            custom_text_anchor = id_config.get(f'custom_text_anchor_{i}').split(',')
            custom_anchor = round(float(custom_text_anchor[0])*image.width), round(float(custom_text_anchor[1])*image.height)
            custom_scaling = eval(id_config.get(f'custom_text_scaling_{i}'))/12
            custom_text = id_config.get(f'custom_text_{i}')
            custom_color = common.get_color(id_config.get(f'custom_text_color_{i}'))
            add_mkw_font_line(infodisplay_layer, custom_text.upper(), None, custom_color, mkw_font_dict[custom_scaling], (custom_anchor[0], custom_anchor[1]), custom_scaling, 'centered', False)
            i += 1
    
    
    for key in id_config.keys():
        if len(key) > 4 and key[:4] == 'show' and key != 'show_infodisplay' and id_config.getboolean(key):
            prefix_text,value_text = make_text_key(id_dict, id_config, font, key)
            color_text = id_config.get('color'+key[4:])
            color = common.get_color(color_text)

            if font is None:                
                add_mkw_font_line(infodisplay_layer, prefix_text.upper(), value_text.upper(), color, mkw_font_dict[mkw_scaling], (top_left[0], current_h), mkw_scaling, anchor_style, invert)
                current_h += round(336*mkw_scaling) + spacing
            else:
                if invert:
                    text = value_text + prefix_text
                    if anchor_style == 'left':
                        offset = 0
                    elif anchor_style == 'middle':
                        offset = -ID.textlength(value_text, font, font_size = font_size)
                    else:
                        offset = -ID.textlength(text, font, font_size = font_size)
                else:
                    text = prefix_text + value_text
                    if anchor_style == 'left':
                        offset = 0
                    elif anchor_style == 'middle':
                        offset = -ID.textlength(prefix_text, font, font_size = font_size)
                    else:
                        offset = -ID.textlength(text, font, font_size = font_size)
                
                ID.text( (top_left[0]+offset, current_h), text, fill = color, font = font, stroke_width = outline_width, stroke_fill = outline_color)
                current_h += spacing + font_size
                

    if id_config.getboolean('fade_animation'):
        infodisplay_layer = common.fade_image_manually(infodisplay_layer, id_dict)
    
    
    if id_config.getboolean('fly_animation'):

        if state == 1 and state_counter <= 10:
            return None
        
        offset = common.fly_in(id_dict, image.height)
        
        if state == 4 and 192 < state_counter < 202:
            image.alpha_composite(infodisplay_layer, (round(0 - image.width*offset), 0))
            return None
        
        ITEM_POSITION = 381/1440
        INFODISPLAY_POSITION = (1 - float(top_left_text[1]))
        height_correction =  round((INFODISPLAY_POSITION - ITEM_POSITION)*image.height)
    
        if offset is not None:
            if id_config.get('fly_in_direction') == 'bottom':
                image.alpha_composite(infodisplay_layer, (0, image.height - top_left[1] - height_correction - offset))
            else:
                image.alpha_composite(infodisplay_layer, (0, offset - round(ITEM_POSITION*image.height)))
        else:
            image.alpha_composite(infodisplay_layer, (0,0))
    else:
        image.alpha_composite(infodisplay_layer, (0,0))
    
