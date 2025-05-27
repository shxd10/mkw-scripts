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

def get_color(color_text):
    n = int(color_text, 16)
    l = []
    for _ in range(4):
        l.append(n%256)
        n//=256
    l.reverse()
    return tuple(l)

def get_filter_list(config_text):
    raw_list = config_text.split(',')
    filters = []
    for raw_text in raw_list:
        if raw_text in ['BLUR', 'blur', 'Blur']:
            filters.append(ImageFilter.BLUR)
        elif raw_text in ['CONTOUR', 'contour', 'Countour']:
            filters.append(ImageFilter.CONTOUR)
        elif raw_text in ['DETAIL', 'detail', 'Detail']:
            filters.append(ImageFilter.DETAIL)
        elif raw_text in ['EDGE_ENHANCE', 'Edge_enhance', 'edge_enhance', 'Edge_Enhance']:
            filters.append(ImageFilter.EDGE_ENHANCE)
        elif raw_text in ['EDGE_ENHANCE_MORE', 'Edge_enhance_more', 'edge_enhance_more', 'Edge_Enhance_More', 'Edge_enhance_More']:
            filters.append(ImageFilter.EDGE_ENHANCE_MORE)
        elif raw_text in ['EMBOSS', 'Emboss', 'emboss']:
            filters.append(ImageFilter.EMBOSS)
        elif raw_text in ['FIND_EDGES', 'Find_edges', 'find_edges', 'Find_Edges']:
            filters.append(ImageFilter.FIND_EDGES)
        elif raw_text in ['SHARPEN', 'Sharpen', 'sharpen']:
            filters.append(ImageFilter.SHARPEN)
        elif raw_text in ['SMOOTH', 'Smooth', 'smooth']:
            filters.append(ImageFilter.SMOOTH)
        elif raw_text in ['SMOOTH_MORE', 'Smooth_more', 'smooth_more', 'Smooth_More']:
            filters.append(ImageFilter.SMOOTH_MORE)
    return filters

def get_resampler(resample_filter):
    if resample_filter in ['nearest', 'Nearest', 'NEAREST']:            
        return Image.Resampling.NEAREST 
    elif resample_filter in ['bicubic', 'Bicubic', 'BICUBIC']:            
        return Image.Resampling.BICUBIC    
    elif resample_filter in ['bilinear', 'Bilinear', 'BILINEAR']:            
        return Image.Resampling.BILINEAR    
    elif resample_filter in ['box', 'Box', 'BOX']:            
        return Image.Resampling.BOX    
    elif resample_filter in ['hamming', 'Hamming', 'HAMMING']:            
        return Image.Resampling.HAMMING    
    else:
        return Image.Resampling.LANCZOS

def fade_image_manually(image, frame_dict):
    fade_in_len = 20
    fade_out_len = 120
    state, state_counter = int(frame_dict['state']), int(frame_dict['state_counter'])
    if state == 1:
        alpha = min(state_counter/fade_in_len, 1)
        r,g,b,a = image.split()
        a = a.point(lambda x:x*alpha)
        image = Image.merge("RGBA", (r,g,b,a))
    elif state ==4:
        alpha = 1 - min(state_counter/fade_out_len, 1)
        r,g,b,a = image.split()
        a = a.point(lambda x:x*alpha)
        image = Image.merge("RGBA", (r,g,b,a))
    return image
