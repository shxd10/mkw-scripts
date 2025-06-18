import moviepy
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFilter
import sys
import os
import time
import subprocess
import math
from Extra import common

def color_white_part(image, color):
    if image.mode != 'RGBA':
        image = image.convert('RGBA') #needed, crashes otherwise if image doesnt have transparency like analog_5_3_part1

    color = tuple(color[:3])
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, _, _, a = pixels[x, y]

            if r == 255:
                pixels[x, y] = (color[0], color[1], color[2], a)
            else: 
                brightness = r / 255
                new_r = int(color[0] * brightness)
                new_g = int(color[1] * brightness)
                new_b = int(color[2] * brightness)
                pixels[x, y] = (new_r, new_g, new_b, a)
            
    return image

def make_input_display(raw_input_text, config_id, font, INPUT_DISPLAY_IMG):
    args = raw_input_text.split(',')
    A = int(args[0])
    B = int(args[1])
    L = int(args[2])
    X = int(args[5])
    Y = int(args[6])
    T = int(args[7])

    w = config_id.getint('width')
    ow = config_id.getint('outline_width')
    color_shoulder_left = common.get_color(config_id.get('color_shoulder_left'))
    color_shoulder_right = common.get_color(config_id.get('color_shoulder_right'))
    color_dpad = common.get_color(config_id.get('color_dpad'))
    color_analog = common.get_color(config_id.get('color_analog'))
    color_a_button = common.get_color(config_id.get('color_a_button'))
    color_stick_text_tmp = common.get_color(config_id.get('color_stick_text'))
    color_stick_text = tuple(color_stick_text_tmp[:3])

    if config_id.getboolean('draw_box'):
        output = INPUT_DISPLAY_IMG['background'].copy()
    else:
        output = Image.new('RGBA', (400,250), (255, 0, 0, 0))

    if A == 0:
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'button_{w}_{ow}'].copy(), color_a_button)
        output.alpha_composite(colored_img, (267,115))
    elif A ==1 :
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'button_filled_{w}_{ow}'].copy(), color_a_button)
        output.alpha_composite(colored_img, (267,115))

    if B == 0:
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'shoulder_{w}_{ow}'].copy(), color_shoulder_right)
        output.alpha_composite(colored_img, (236,46))
    elif B ==1 :
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'shoulder_filled_{w}_{ow}'].copy(), color_shoulder_right)
        output.alpha_composite(colored_img, (236,46))
        
    if L == 0:
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'shoulder_{w}_{ow}'].copy(), color_shoulder_left)
        output.alpha_composite(colored_img, (56,46))
        #output.alpha_composite(INPUT_DISPLAY_IMG[f'shoulder_{w}_{ow}'], (56,46))
    elif L ==1 :
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'shoulder_filled_{w}_{ow}'].copy(), color_shoulder_left)
        output.alpha_composite(colored_img, (56,46))

    colored_img = color_white_part(INPUT_DISPLAY_IMG[f'dpad_fill_{T}'].copy(), color_dpad)
    output.alpha_composite(colored_img, (57,107))    
    colored_img = color_white_part(INPUT_DISPLAY_IMG[f'dpad_{w}_{ow}'].copy(), color_dpad) 
    output.alpha_composite(colored_img, (47,97))       

    colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_base_{w}_{ow}'].copy(), color_analog)
    output.alpha_composite(colored_img, (152,94))    

    colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_outer_{w}_{ow}'].copy(), color_analog)
    output.alpha_composite(colored_img, (155 + X * 3,97 - Y * 3))

    if config_id.getboolean('draw_box'):
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_bg_{w}_{ow}_part1'].copy(), color_analog)
        output.paste(colored_img, (155+34 + X * 3, 97+20 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_bg_{w}_{ow}_part2'].copy(), color_analog)
        output.paste(colored_img, (155+27 + X * 3, 97+25 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_bg_{w}_{ow}_part3'].copy(), color_analog)
        output.paste(colored_img, (155+21 + X * 3, 97+31 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_bg_{w}_{ow}_part4'].copy(), color_analog)
        output.paste(colored_img, (155+27 + X * 3, 97+64 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_bg_{w}_{ow}_part5'].copy(), color_analog)
        output.paste(colored_img, (155+34 + X * 3, 97+70 - Y * 3))
    else:
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_{w}_{ow}_part1'].copy(), color_analog)
        output.paste(colored_img, (155+34 + X * 3, 97+20 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_{w}_{ow}_part2'].copy(), color_analog)
        output.paste(colored_img, (155+27 + X * 3, 97+25 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_{w}_{ow}_part3'].copy(), color_analog)
        output.paste(colored_img, (155+21 + X * 3, 97+31 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_{w}_{ow}_part4'].copy(), color_analog)
        output.paste(colored_img, (155+27 + X * 3, 97+64 - Y * 3))
        colored_img = color_white_part(INPUT_DISPLAY_IMG[f'analog_{w}_{ow}_part5'].copy(), color_analog)
        output.paste(colored_img, (155+34 + X * 3, 97+70 - Y * 3))

    if config_id.getboolean('draw_stick_text'):
        ID = ImageDraw.Draw(output)
        text = f'({"+" if X>0 else (" " if X==0 else '')}{X},{"+" if Y>0 else (" " if Y==0 else '')}{Y})'
        ID.text( (132,198), text, font = font, fill = color_stick_text, stroke_width = 3, stroke_fill = (0,0,0))

    scaling = config_id.getfloat('scaling')
    if scaling != 1.0:
        resample_filter = common.get_resampler(config_id.get('scaling_option'))
        output = output.resize((round(400*scaling), round(250*scaling)), resample_filter)

    for filtre in common.get_filter_list(config_id.get('special_effects')):
        output = output.filter(filtre)

    return output

def add_input_display(image, frame_dict, config, font_folder, INPUT_DISPLAY_IMG):
    font = ImageFont.truetype(os.path.join(font_folder, 'CONSOLA.TTF'), 36)
    input_display = make_input_display(frame_dict['input'], config['Input display'], font, INPUT_DISPLAY_IMG)
    top_left_text = config['Input display'].get('top_left').split(',')
    top_left = round(float(top_left_text[0])*image.width), round(float(top_left_text[1])*image.height)

    input_display = common.fade_image_manually(input_display, frame_dict)
    image.alpha_composite(input_display, top_left)
    
