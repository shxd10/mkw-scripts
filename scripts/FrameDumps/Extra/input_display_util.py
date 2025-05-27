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


def make_input_display(raw_input_text, config_id, font, INPUT_DISPLAY_IMG):
    args = raw_input_text.split(',')
    A = int(args[0])
    B = int(args[1])
    L = int(args[2])
    X = int(args[5])
    Y = int(args[6])
    T = int(args[7])

    if config_id.getboolean('draw_box'):
        output = INPUT_DISPLAY_IMG['background'].copy()
    else:
        output = Image.new('RGBA', (400,250), (255, 0, 0, 0))

    if A == 0:
        output.alpha_composite(INPUT_DISPLAY_IMG['button'], (270,118))
    elif A ==1 :
        output.alpha_composite(INPUT_DISPLAY_IMG['button_filled'], (270,118))

    if B == 0:
        output.alpha_composite(INPUT_DISPLAY_IMG['shoulder'], (240,50))
    elif B ==1 :
        output.alpha_composite(INPUT_DISPLAY_IMG['shoulder_filled'], (240,50))

    if L == 0:
        output.alpha_composite(INPUT_DISPLAY_IMG['shoulder'], (60,50))
    elif L ==1 :
        output.alpha_composite(INPUT_DISPLAY_IMG['shoulder_filled'], (60,50))

    output.alpha_composite(INPUT_DISPLAY_IMG[f'dpad_{T}'], (50,100))
    
    output.alpha_composite(INPUT_DISPLAY_IMG['analog_outer'], (155,97))
    output.alpha_composite(INPUT_DISPLAY_IMG['analog'], (155 + X * 3 ,97 - Y * 3))

    if config_id.getboolean('draw_stick_text'):
        ID = ImageDraw.Draw(output)
        text = f'({"+" if X>0 else (" " if X==0 else '')}{X},{"+" if Y>0 else (" " if Y==0 else '')}{Y})'
        ID.text( (132,198), text, font = font, fill = (255,255,255), stroke_width = 3, stroke_fill = (0,0,0))

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
    
