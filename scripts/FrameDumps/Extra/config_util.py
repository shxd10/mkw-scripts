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

import configparser


def create_config(filename):
    config = configparser.ConfigParser(allow_no_value=True, allow_unnamed_section=True)
    config.add_section('README')
    config.set('README', 'Visit : https://docs.google.com/document/d/e/2PACX-1vTXoEveB_1MZ3WizOpEWvZ-oyJMgg-3pRLGiNu-5vo853BMcrr8RY69REcTsheurI9qS2kfqrx1BZkT/pub\n\n' )
    config.add_section('Path')
    config.set('Path', '#Enter the full path of your Dump folder.\n#Usually something like "C://path_to//Dolphin/User/Dump"')
    config.set('Path', 'dump_folder', r'C://path_to//Dolphin/User/Dump') 
    
    config.add_section('Encoding options')
    config.set('Encoding options', '\n#Valid options are "normal", "discord", "youtube"')
    '''
    config.set('Encoding options', '#"normal" is no particular encoding settings, for people who want to do more video editing afterward')
    config.set('Encoding options', '#"discord" is for size based encoding, allowing for a specific filesize output')
    config.set('Encoding options', '#"youtube" is for directly uploading on YT. uses encode settings from https://gist.github.com/wuziq/b86f8551902fa1d477980a8125970877')
    '''
    config.set('Encoding options', '#You can also set an integer, to only render the .png of the corresponding frame (useful for trying different display options quickly)')
    config.set('Encoding options', 'encode_style', 'discord')#
    config.set('Encoding options', '\n#Video output size in mb. only used with discord encoding style')
    config.set('Encoding options', 'output_file_size', '9.5')#in MB
    config.set('Encoding options', '\n#range from 0 to 51. Only used with normal encoding style')
    config.set('Encoding options', 'crf_value', '0')#
    config.set('Encoding options', '\n#Choice "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"')
    config.set('Encoding options', '#it affect the size of the output file, and the performances. it also affect quality when using discord encoding style')
    config.set('Encoding options', 'preset', 'slow')#
    config.set('Encoding options', '\n#Threads amount to use for ffmpeg')
    config.set('Encoding options', 'threads', '4')#
    config.set('Encoding options', '\n#Height of the output video in pixel')
    config.set('Encoding options', 'resize_resolution', '1080')#
    config.set('Encoding options', '\n#Choice "stretch", "crop", "fill", "none"')
    config.set('Encoding options', 'resize_style', 'none') #stretch, crop, fill, none
    config.set('Encoding options', '\n#Choice "nearest", "box", "bilinear", "hamming", "bicubic", "lanczos"')
    config.set('Encoding options', '#visit https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters')
    config.set('Encoding options', 'scaling_option', 'lanczos') #https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
    config.set('Encoding options', '\n#filename for the output file. .mp4 extension required')
    config.set('Encoding options', 'output_filename', 'output.mp4')#
    config.set('Encoding options', '\n#time in seconds for the video fade in')
    config.set('Encoding options', 'video_fade_in', '0')#
    config.set('Encoding options', '\n#time in seconds for the video fade out')
    config.set('Encoding options', 'video_fade_out', '0')#
    config.set('Encoding options', '\n#Choice "blur", "contour", "detail", "edge_enhance", "edge_enhance_more", "emboss", "find_edges", "sharpen", "smooth", "smooth_more"')
    config.set('Encoding options', '#You can use several effects by separating them with a ",". DO NOT USE SPACES')
    config.set('Encoding options', 'special_effects', 'none') #https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html#module-PIL.ImageFilter
    config.set('Encoding options', '\n\n##############################################################################\n')

    config.add_section('Audio options')
    config.set('Audio options', '\n#Choice "dsp", "dtk", "none"')
    config.set('Audio options', 'audiodump_target', 'none') #dsp, dtk, none
    config.set('Audio options', '\n#multiplicator on the in game volume')
    config.set('Audio options', 'audiodump_volume', '1.0')#
    config.set('Audio options', '\n#Must be a file in the same folder as this config file')
    config.set('Audio options', 'bgm_filename', '')#
    config.set('Audio options', '\n#multiplicator on the bgm volume')
    config.set('Audio options', 'bgm_volume', '1')#
    config.set('Audio options', '\n#Time in second the BGM should start at in the output video. You can use negative values to skip the beginning of the BGM')
    config.set('Audio options', 'bgm_offset', '0')#
    config.set('Audio options', '\n#time in second for the audio fade in')
    config.set('Audio options', 'fade_in', '0')#
    config.set('Audio options', '\n#time in second for the audio fade out')
    config.set('Audio options', 'fade_out', '0')#
    config.set('Audio options', '\n\n##############################################################################\n')
    
    config.add_section('Infodisplay')
    config.set('Infodisplay', '\n#draw the infodisplay')
    config.set('Infodisplay', 'show_infodisplay', 'True')#
    config.set('Infodisplay', '\n#Font filename. You must put the font in the Font folder.')
    config.set('Infodisplay', 'font', 'CONSOLA.TTF')#
    config.set('Infodisplay', '\n#font size in pixel on the final output resolution.')
    config.set('Infodisplay', 'font_size', '48')#
    config.set('Infodisplay', '\n#Top left anchor for infodisplay text. 0,0 is top left, 1,1 is bottom right, 0.5,0.5 is middle of the screen')
    config.set('Infodisplay', 'top_left', '0.1,0.1')#
    config.set('Infodisplay', '\n#size of the outline of the font in pixel')
    config.set('Infodisplay', 'outline_width', '3')#
    config.set('Infodisplay', '\n#color of the outline of the font')
    config.set('Infodisplay', 'outline_color', '000000FF')#
    
    config.set('Infodisplay', '\n#parameters for the XYZ speed (delta position)')
    config.set('Infodisplay', 'show_speed_xyz', 'True')
    config.set('Infodisplay', 'text_speed_xyz', 'Speed : ')
    config.set('Infodisplay', 'color_speed_xyz', 'FF0000FF')

    
    config.set('Infodisplay', '\n#parameters for the XZ speed (delta position)')   
    config.set('Infodisplay', 'show_speed_xz', 'False')
    config.set('Infodisplay', 'text_speed_xz', 'XZ Speed : ')
    config.set('Infodisplay', 'color_speed_xz', 'FF0000FF')

    config.set('Infodisplay', '\n#parameters for the Y speed (delta position)')
    config.set('Infodisplay', 'show_speed_y', 'False')
    config.set('Infodisplay', 'text_speed_y', 'Y Speed : ')
    config.set('Infodisplay', 'color_speed_y', 'FF0000FF')

    config.set('Infodisplay', '\n#parameters for the XYZ internal velocity')
    config.set('Infodisplay', 'show_iv_xyz', 'True')
    config.set('Infodisplay', 'text_iv_xyz', 'Internal Velocity : ')
    config.set('Infodisplay', 'color_iv_xyz', '00FF00FF')

    config.set('Infodisplay', '\n#parameters for the XZ internal velocity')
    config.set('Infodisplay', 'show_iv_xz', 'False')
    config.set('Infodisplay', 'text_iv_xz', 'XZ Internal Velocity : ')
    config.set('Infodisplay', 'color_iv_xz', '00FF00FF')

    config.set('Infodisplay', '\n#parameters for the Y internal velocity')
    config.set('Infodisplay', 'show_iv_y', 'False')
    config.set('Infodisplay', 'text_iv_y', 'Y Internal Velocity : ')
    config.set('Infodisplay', 'color_iv_y', '00FF00FF')

    config.set('Infodisplay', '\n#parameters for the XYZ external velocity')
    config.set('Infodisplay', 'show_ev_xyz', 'True')
    config.set('Infodisplay', 'text_ev_xyz', 'External Velocity : ')
    config.set('Infodisplay', 'color_ev_xyz', '0000FFFF')

    config.set('Infodisplay', '\n#parameters for the XZ external velocity')
    config.set('Infodisplay', 'show_ev_xz', 'False')
    config.set('Infodisplay', 'text_ev_xz', 'XZ External Velocity : ')
    config.set('Infodisplay', 'color_ev_xz', '0000FFFF')

    config.set('Infodisplay', '\n#parameters for the Y external velocity')
    config.set('Infodisplay', 'show_ev_y', 'False')
    config.set('Infodisplay', 'text_ev_y', 'Y External Velocity : ')
    config.set('Infodisplay', 'color_ev_y', '0000FFFF')
    
    config.set('Infodisplay', '\n\n##############################################################################\n')

    config.add_section('Speed display')
    config.set('Speed display', '\n#draw the speed display')
    config.set('Speed display', 'show_speed_display', 'True')
    config.set('Speed display', '\n#Top left anchor for speed display text. 0,0 is top left, 1,1 is bottom right, 0.5,0.5 is middle of the screen')
    config.set('Speed display', 'top_left', '0.7, 0.5')#
    config.set('Speed display', '\n#Activating this will make the circle rotate with your facing yaw, so it always face up')
    config.set('Speed display', 'rotate_with_yaw', 'True')#
    config.set('Speed display', '\n#Radius of the circle in pixel on the final output resolution')
    config.set('Speed display', 'circle_radius', '200')#
    config.set('Speed display', '\n#Color of the interior of the circle')
    config.set('Speed display', 'circle_color', 'FFFFFF80')#
    config.set('Speed display', '\n#color of the border of the circle')
    config.set('Speed display', 'circle_outline_color', '000000FF')#
    config.set('Speed display', '\n#size of the border of the circle')
    config.set('Speed display', 'circle_outline_width', '4')#
    config.set('Speed display', '\n#Draw the XZ axis when rotating with yaw. Draw the sideways and forward axis when not rotating with yaw')
    config.set('Speed display', 'draw_axis', 'True')#
    config.set('Speed display', '\n#color of the axis')
    config.set('Speed display', 'axis_color', '000000FF')#
    config.set('Speed display', '\n#width of the axis in pixel on the final output resolution')
    config.set('Speed display', 'axis_width', '2')#
    config.set('Speed display', '\n#Draw a pieslice corresponding to the facing yaw') 
    config.set('Speed display', 'draw_pieslice', 'False')#
    config.set('Speed display', '\n#color of that pieslice')
    config.set('Speed display', 'pieslice_color', 'FFFF00FF')
    config.set('Speed display', '\n#width of the arrows')
    config.set('Speed display', 'arrow_width', '6')#
    config.set('Speed display', '\n#size of the border of the arrows')
    config.set('Speed display', 'arrow_outline_width', '1')#
    config.set('Speed display', '\n#color of the border of the arrows')
    config.set('Speed display', 'arrow_outline_color', '000000FF')#
    config.set('Speed display', '\n#maximum speed corresponding to a full arrow. this parameter also scale the length of the arrow')
    config.set('Speed display', 'cap_speed', '125')#
    config.set('Speed display', '\n#arrow corresponding to speed (delta position)')
    config.set('Speed display', 'show_speed', 'True')
    config.set('Speed display', 'color_speed', 'FF0000FF')
    config.set('Speed display', '\n#arrow corresponding to internal velocity')
    config.set('Speed display', 'show_iv', 'True')
    config.set('Speed display', 'color_iv', '00FF00FF')
    config.set('Speed display', '\n#arrow corresponding to external velocity')
    config.set('Speed display', 'show_ev', 'True')
    config.set('Speed display', 'color_ev', '0000FFFF')
    config.set('Speed display', '\n\n##############################################################################\n')
    

    config.add_section('Input display')
    config.set('Input display', '\n#draw the input display')
    config.set('Input display', 'show_input_display', 'True')
    config.set('Input display', '\n#Top left anchor for input display text. 0,0 is top left, 1,1 is bottom right, 0.5,0.5 is middle of the screen')
    config.set('Input display', 'top_left', '0.03,0.7')#
    config.set('Input display', '\n#multiplier on the size of input display. Default size is 250x400 in pixel on the output resolution')
    config.set('Input display', 'scaling', '1')#
    config.set('Input display', '\n#Choice "nearest", "box", "bilinear", "hamming", "bicubic", "lanczos"')
    config.set('Input display', '#visit #https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters')
    config.set('Input display', 'scaling_option', 'lanczos') #https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
    config.set('Input display', '\n#Draw the bounding box. The file itself can be modified in the Input_display folder')
    config.set('Input display', 'draw_box', 'True')#
    config.set('Input display', '\n#Draw the +7,-7 text corresponding to the stick input')
    config.set('Input display', 'draw_stick_text', 'True')#
    config.set('Input display', '\n#Choice "blur", "contour", "detail", "edge_enhance", "edge_enhance_more", "emboss", "find_edges", "sharpen", "smooth", "smooth_more"')
    config.set('Input display', '#You can use several effects by separating them with a ",". DO NOT USE SPACES')
    config.set('Input display', 'special_effects', 'none')#
    config.set('Input display', '\n\n##############################################################################\n')

    config.add_section('Author display')
    config.set('Author display', '\n#draw the author display')
    config.set('Author display', 'show_author_display', 'False')
    config.set('Author display', '\n#Top left anchor for author display text. 0,0 is top left, 1,1 is bottom right, 0.5,0.5 is middle of the screen')
    config.set('Author display', 'top_left', '0.1,0.4')#   
    config.set('Author display', '\n#Must be a file in the same folder as this config file. Mandatory for the author display to work')
    config.set('Author display', 'author_list_filename', 'authors.txt')#
    config.set('Author display', '\n#Font filename. You must put the font in the Font folder.')
    config.set('Author display', 'font', 'CONSOLA.TTF')#
    config.set('Author display', '\n#font size in pixel on the final output resolution')
    config.set('Author display', 'font_size', '48')#
    config.set('Author display', '\n#color used for the text when the author has input on this frame')
    config.set('Author display', 'active_text_color', 'FFFFFFFF')#
    config.set('Author display', '\n#color used for the text when the author does not have input on this frame')
    config.set('Author display', 'unactive_text_color', 'FFFFFF80')#
    config.set('Author display', '\n#outline width for the font used')
    config.set('Author display', 'outline_width', '3')#
    config.set('Author display', '\n#color of the outline width')
    config.set('Author display', 'outline_color', '000000FF')#
    
    with open(filename, 'w') as f:
        config.write(f)

def get_config(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename)
    return config
