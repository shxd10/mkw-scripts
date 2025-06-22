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

def make_list_author(c, main_folder):
    #return a dict so that result[frame] contain an ordered list of author that contributed on that frame
    #also return a list of all author
    result = {}
    raw_author_list = []
    author_file = os.path.join(main_folder, c.get('author_list_filename'))
    if os.path.isfile(author_file):
        with open(author_file, 'r', encoding='utf-8') as f:
            entry_list = f.read().split('\n')
            for entry in entry_list:
                temp = entry.split(':')
                author_name = temp[0]
                raw_author_list.append(author_name) 
                frames_entry = temp[1].split(',')
                for token in frames_entry:
                    temp = token.split('-')
                    for frame in range(int(temp[0]), int(temp[-1])+1):
                        if not frame in result.keys():
                            result[frame] = []
                        result[frame].append(author_name)
    return raw_author_list, result
                        

def add_author_display(image, frame_dict, ad_config, main_folder, raw_author_list, author_dict):
    author_display_layer = Image.new('RGBA', image.size, (0,0,0,0))
    ID = ImageDraw.Draw(author_display_layer)
    font_folder = os.path.join(main_folder, 'Fonts')
    top_left_text = ad_config.get('top_left').split(',')
    top_left = round(float(top_left_text[0])*image.width), round(float(top_left_text[1])*image.height)
    font_size =  ad_config.getint('font_size')
    font = ImageFont.truetype(os.path.join(font_folder, ad_config.get('font')), font_size)
    active_text_color = common.get_color(ad_config.get('active_text_color'))
    unactive_text_color = common.get_color(ad_config.get('unactive_text_color'))
    outline_width = ad_config.getint('outline_width')
    outline_color = common.get_color(ad_config.get('outline_color'))
    curframe = int(frame_dict['frame_of_input'])
    spacing = 4
    current_h = top_left[1]
    
    for author_name in raw_author_list:
        if curframe in author_dict.keys() and author_name in author_dict[curframe]:
            ID.text( (top_left[0], current_h), author_name, fill = active_text_color, font = font, stroke_width = outline_width, stroke_fill = outline_color)
        else:
            ID.text( (top_left[0], current_h), author_name, fill = unactive_text_color , font = font, stroke_width = outline_width, stroke_fill = outline_color)
        current_h += spacing + font_size

        
    author_display_layer = common.fade_image_manually(author_display_layer, frame_dict)
    image.alpha_composite(author_display_layer, (0,0))
