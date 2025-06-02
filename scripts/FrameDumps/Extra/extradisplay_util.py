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
                      "/" :-32, ":" : -1, "." : -1, "0" : -1,
                      "1" : -1, "2" : -1, "3" : -1, "4" : -1,
                      "5" : -1, "6" : -1, "7" : -1, "8" : -1,
                      "9" : -1}



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


def add_mkw_font_line(id_layer, text, color, mkw_font_dict, anchor, mkw_scaling, anchor_style):
    w,h = anchor
    line_layer = Image.new('RGBA', (id_layer.size[0], round(mkw_scaling*336)+1), (0,0,0,0))


    left_x = 0
    middle_x = add_mkw_text(line_layer, left_x, text[0], mkw_font_dict, color, mkw_scaling)
    right_x = add_mkw_text(line_layer, middle_x, text[1], mkw_font_dict, color, mkw_scaling)

    if anchor_style == 'left':
        offset = left_x
    elif anchor_style == 'middle':
        offset = middle_x
    else:
        offset = right_x
    w -= offset

    id_layer.alpha_composite(line_layer, (w,h))


def add_extradisplay(image, extra_text, ex_config, font_folder, mkw_font_dict):

    infodisplay_layer = Image.new('RGBA', image.size, (0,0,0,0))
    ID = ImageDraw.Draw(infodisplay_layer)
    mkw_scaling = eval(ex_config.get('mkw_font_scaling'))/12
    top_left_text = ex_config.get('anchor').split(',')
    top_left = round(float(top_left_text[0])*image.width), round(float(top_left_text[1])*image.height)
    current_h = top_left[1]
    spacing = ex_config.getint('spacing')
    font_size =  ex_config.getint('font_size')
    font_filename = os.path.join(font_folder, ex_config.get('font'))
    if os.path.isfile(font_filename):        
        font = ImageFont.truetype(font_filename, font_size)
    else:
        font = None
    outline_width = ex_config.getint('outline_width')
    outline_color = common.get_color(ex_config.get('outline_color'))
    color = common.get_color(ex_config.get('color'))
    
    for text in extra_text.split('\n'):
        if font is None:                
            add_mkw_font_line(infodisplay_layer, text, color, mkw_font_dict, (top_left[0], current_h), mkw_scaling, 'left')
            current_h += round(336*mkw_scaling) + spacing
        else:            
            ID.text( (top_left[0], current_h), text, fill = color, font = font, stroke_width = outline_width, stroke_fill = outline_color)
            current_h += spacing + font_size
            
    image.alpha_composite(infodisplay_layer, (0,0))
    
