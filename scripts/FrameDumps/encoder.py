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

from Extra import config_util
from Extra import input_display_util
from Extra import infodisplay_util
from Extra import speed_display_util
from Extra import author_display_util
from Extra import extradisplay_util
from Extra import common

time.sleep(1) #waits a bit to make sure the framedump metadata is written

current_folder = os.path.dirname(sys.argv[0])
extra_display_folder = os.path.dirname(sys.argv[0])


#Initializing MKW Font images
mkw_font_folder = os.path.join(current_folder, 'Fonts', 'MKW_Font')
MKW_FONT_IMG = {}
for filename in os.listdir(mkw_font_folder):
    if filename[-4:] == '.png':
        letter = filename[:-4]
        if letter == 'SLASH_':
            letter = '/'
        if letter == 'SLASH':
            letter = '&'
        elif letter == 'COLON':
            letter = ':'
        elif letter == 'PERIOD':
            letter = '.'
        MKW_FONT_IMG[letter] = Image.open(os.path.join(mkw_font_folder, filename))


def make_dict(filetext):
    d = {}
    for line in filetext.split('\n'):
        temp = line.split(':')
        if len(temp) == 2:
            d[temp[0]] = temp[1]
    return d

    
def transform_image(image, i=-1):
    #Resample algorithm
    resample_filter = config['Encoding options'].get('scaling_option')
    resampler = common.get_resampler(resample_filter)
    resize_style = config['Encoding options'].get('resize_style')
    target_height = config['Encoding options'].getint('resize_resolution')
    target_width = round(target_height*16/9)
    target_resolution = (target_width, target_height)

    #Convert from numpy array to PIL Image
    image = Image.fromarray(image)

    #Resize the image
    if resize_style in ['stretch', 'Stretch', 'STRETCH']:
        image = image.resize(target_resolution, resampler)
    if resize_style in ['crop', 'Crop', 'CROP']:
        dump_width, dump_height = image.size
        if dump_width*9 >= dump_height*16: 
            ratio = target_height/dump_height
            image = image.resize((round(dump_width*ratio), round(dump_height*ratio)), resampler)
            image = image.crop(((image.width-target_width)//2, 0, target_width+(image.width-target_width)//2, target_height))
        else:
            ratio = target_width/dump_width
            image = image.resize((round(dump_width*ratio), round(dump_height*ratio)), resampler)
            image = image.crop(((0, (image.height-target_height)//2, target_width, target_height+image.height-target_height)//2))
    if resize_style in ['fill', 'Fill', 'FILL']:
        dump_width, dump_height = image.size
        if dump_width*9 >= dump_height*16: 
            ratio = target_width/dump_width
            image = image.resize((round(dump_width*ratio), round(dump_height*ratio)), resampler)
            black_background = Image.new('RGB', target_resolution, (0,0,0))
            black_background.paste(image, (0, (target_height-image.height)//2))
            image = black_background
        else:
            ratio = target_height/dump_height
            image = image.resize((round(dump_width*ratio), round(dump_height*ratio)), resampler)
            black_background = Image.new('RGB', target_resolution, (0,0,0))
            black_background.paste(image, ((target_width-image.width)//2), 0)
            image = black_background

            
    image = image.convert("RGBA")
    font_folder = os.path.join(current_folder, 'Fonts')
    
    if os.path.isfile(os.path.join(extra_display_folder, 'RAM_data', f'{i}.txt')):
        with open(os.path.join(extra_display_folder, 'RAM_data', f'{i}.txt'), 'r') as f:
            t = f.read()
            if len(t)>1:
                frame_dict = make_dict(t)

                if config['Input display'].getboolean('show_input_display'):
                    input_display_util.add_input_display(image, frame_dict, config, font_folder, recolored_images, w, ow)
                if config['Speed display'].getboolean('show_speed_display'):
                    speed_display_util.add_speed_display(image, frame_dict, config)
                if config['Infodisplay'].getboolean('show_infodisplay'):
                    infodisplay_util.add_infodisplay(image, frame_dict, config, font_folder, scaled_fonts_dict)
                if config['Author display'].getboolean('show_author_display'):
                    author_display_util.add_author_display(image, frame_dict, config, current_folder, raw_author_list, author_dict)

    if os.path.isfile(os.path.join(extra_display_folder, 'RAM_data', f'{i}.rawtxt')):
        with open(os.path.join(extra_display_folder, 'RAM_data', f'{i}.rawtxt'), 'r') as f:
            text = f.read()                
            if config['Extra display'].getboolean('show_extradisplay'):
                extradisplay_util.add_extradisplay(image, text, config['Extra display'], font_folder, MKW_FONT_IMG)

    filters = common.get_filter_list(config['Encoding options'].get('special_effects'))
    for filtre in filters:
        image = image.filter(filtre)
    return np.array(image.convert("RGB"))

def transform_video(get_frame, t):
    image = get_frame(t)
    i = round(t*59.94) -1
    print('')
    return transform_image(image, i)

def main():
    extra_display_folder = os.path.dirname(sys.argv[0])
    current_folder = os.path.dirname(sys.argv[0])

    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
    else:
        config_filename = os.path.join(extra_display_folder, 'config.ini')
    if not os.path.isfile(config_filename):
        config_util.create_config(config_filename)

    
    global config
    config = config_util.get_config(config_filename)


    global w
    global ow
    w = config['Input display'].getint('width')
    ow = config['Input display'].getint('outline_width')
    bg = config['Input display'].getboolean('draw_box')
    #Initializing input display images
    input_display_folder = os.path.join(current_folder, 'Input_display')
    INPUT_DISPLAY_IMG = {}

    for filename in os.listdir(input_display_folder):
        is_w_ow = (filename[-7:] == f'{w}_{ow}.png')
        aligns_with_bg = ('bg' in filename) == bg
        if is_w_ow and (not 'part' in filename) or is_w_ow and aligns_with_bg or filename == 'background.png' or filename[:9] == 'dpad_fill':
            INPUT_DISPLAY_IMG[filename[:-4]] = Image.open(os.path.join(current_folder, 'Input_display', filename))


    color_dict = {'color_shoulder_left': common.get_color(config['Input display'].get('color_shoulder_left')),
    'color_shoulder_right': common.get_color(config['Input display'].get('color_shoulder_right')),
    'color_dpad': common.get_color(config['Input display'].get('color_dpad')),
    'color_analog': common.get_color(config['Input display'].get('color_analog')),
    'color_a_button': common.get_color(config['Input display'].get('color_a_button')),
    'color_stick_text': common.get_color(config['Input display'].get('color_stick_text')),}

    base_keys = {
    'shoulder': ['color_shoulder_left', 'color_shoulder_right'], 'shoulder_filled': ['color_shoulder_left',
    'color_shoulder_right'], 'dpad': ['color_dpad'], 'analog_outer': ['color_analog'],
    'analog_base': ['color_analog'], 'button': ['color_a_button'], 'button_filled': ['color_a_button']}

    analog_keys = {'analog_part1': ['color_analog'], 'analog_part2': ['color_analog'],
    'analog_part3': ['color_analog'], 'analog_part4': ['color_analog'], 'analog_part5': ['color_analog']}

    analog_bg_keys = {'analog_bg_part1': ['color_analog'], 'analog_bg_part2': ['color_analog'], 
    'analog_bg_part3': ['color_analog'], 'analog_bg_part4': ['color_analog'], 'analog_bg_part5': ['color_analog']}

    if bg:
        base_keys.update(analog_bg_keys)
    else:
        base_keys.update(analog_keys)

    global recolored_images
    recolored_images = {}

    for base_key, colors in base_keys.items():
        img_key = f"{base_key}_{w}_{ow}"
        base_img = INPUT_DISPLAY_IMG[img_key]
        for color_name in colors:
            color = color_dict[color_name]
            recolored_key = f"{img_key}|{color_name}"
            recolored_images[recolored_key] = common.color_white_part(base_img.copy(), color)

    recolored_images['background'] = INPUT_DISPLAY_IMG['background']
    recolored_images['dpad_fill_0'] = INPUT_DISPLAY_IMG['dpad_fill_0']
    for x in range(1,5):
        recolored_images[f'dpad_fill_{x}'] = common.color_white_part(INPUT_DISPLAY_IMG[f'dpad_fill_{x}'].copy(), color_dict['color_dpad'])


    global raw_author_list, author_dict
    raw_author_list, author_dict = author_display_util.make_list_author(config['Author display'], extra_display_folder)


    i = 1
    scaling_set = {eval(config['Infodisplay'].get('mkw_font_scaling'))/12}
    scaling_set.add(0.2375) # 2.85 / 12, this is for the pretty speedometer.
    while f'custom_text_{i}' in config['Infodisplay']:
        scaling_set.add(eval(config['Infodisplay'].get(f'custom_text_scaling_{i}'))/12)
        i += 1

    global scaled_fonts_dict
    scaled_fonts_dict = {}
    for scale in scaling_set:
        tmp_dict = {}
        for key in MKW_FONT_IMG.keys():
            size = MKW_FONT_IMG[key].size
            w2,h2 = (round(size[0]*scale), round(size[1]*scale))
            tmp_dict[key] = MKW_FONT_IMG[key].resize((w2,h2) , Image.Resampling.LANCZOS)
        scaled_fonts_dict[scale] = tmp_dict 

    #Getting filenames
    with open(os.path.join(extra_display_folder, 'dump_info.txt'), 'r') as f:
        temp = f.read().split('\n')
        framedump_prefix = temp[0]
        dump_folder = config['Path'].get('dump_folder')
        if not os.path.isdir(dump_folder):
            print('No framedump found')
            print('Did you configure your dump path correctly in the config file ?')
            input('Press ENTER to exit')
            return False
        framedump_folder = os.path.join(dump_folder, 'Frames')
        audiodump_folder = os.path.join(dump_folder, 'Audio')

    framedump_filenames = []
    for filename in os.listdir(framedump_folder):
        if len(filename) > len(framedump_prefix) :
            if filename[:len(framedump_prefix)] == framedump_prefix:
                framedump_filenames.append(os.path.join(framedump_folder,filename))

        
    framedump_clip = [moviepy.VideoFileClip(filename) for filename in framedump_filenames]
    #Concatening directly the clip from framedump_clip to source was sometimes duplicating frames...
    #This is why I do this workaround, which expects very few frames from all clip except the last one.
    list_frame_beginning = []
    for i in range(len(framedump_clip) -1):
        for cur_frame in framedump_clip[i].iter_frames():
            list_frame_beginning.append(cur_frame)
    if len(framedump_clip) > 1 :    
        beg_clip = moviepy.ImageSequenceClip(list_frame_beginning, fps = 59.94)    
        source = moviepy.concatenate_videoclips([beg_clip, framedump_clip[-1]])
    else:
        source = framedump_clip[-1]

    #Add audio dump
    audio_dumper = config['Audio options'].get('audiodump_target')
    audio_source = []
    if audio_dumper in ['dsp', 'DSP', 'Dsp']:        
        audiodump_filename = os.path.join(audiodump_folder, framedump_prefix+'_dspdump.wav')        
    elif audio_dumper in ['dtk', 'DTK', 'Dtk']:
        audiodump_filename = os.path.join(audiodump_folder, framedump_prefix+'_dtkdump.wav')
    else:
        audiodump_filename = None
    if audiodump_filename:        
        audio_source.append(moviepy.AudioFileClip(audiodump_filename))
        volume = config['Audio options'].getfloat('audiodump_volume')
        audio_source[-1] = audio_source[-1].with_effects([moviepy.afx.MultiplyVolume(volume)])
    
    #Add bgm
    bgm_filename = config['Audio options'].get('bgm_filename')
    if os.path.isfile(os.path.join(extra_display_folder, bgm_filename)):
        bgm = moviepy.AudioFileClip(bgm_filename)
        offset = config['Audio options'].getint('bgm_offset')
        if offset <= 0:            
            audio_source.append(bgm[-offset:-offset+source.duration])
        else:
            audio_source.append((moviepy.audio.AudioClip.AudioClip(lambda t: [0], offset, bgm) + bgm)[:source.duration])
        volume = config['Audio options'].getfloat('bgm_volume')

        audio_source[-1] = audio_source[-1].with_effects([moviepy.afx.MultiplyVolume(volume)])
    if audio_source:
        fade_in = config['Audio options'].getfloat('fade_in')
        fade_out = config['Audio options'].getfloat('fade_out')    
        source.audio = moviepy.CompositeAudioClip(audio_source).with_effects([moviepy.afx.AudioFadeOut(fade_out),
                                                                              moviepy.afx.AudioFadeIn(fade_in)])

    #Fade effect
    fade_in = config['Encoding options'].getfloat('video_fade_in')
    fade_out = config['Encoding options'].getfloat('video_fade_out')
    
    #Encode
    t = time.time()
    encode_style = config['Encoding options'].get('encode_style')
    output_filename = os.path.join(extra_display_folder, config['Encoding options'].get('output_filename'))
    no_vid = False
    if encode_style in ['Normal', 'normal', 'NORMAL', 'n', 'N', 'norm',]:
        output_video = source.transform(transform_video, apply_to="mask").with_effects([moviepy.vfx.FadeOut(fade_out),
                                                                                        moviepy.vfx.FadeIn(fade_in)])
        output_video.write_videofile(output_filename,
                                     codec = 'libx264',
                                     preset = config['Encoding options'].get('preset'),
                                     threads = config['Encoding options'].getint('threads'),
                                     ffmpeg_params = ['-crf', config['Encoding options'].get('crf_value')])
    elif encode_style in ['Discord', 'DISCORD', 'discord', 'd', 'D', 'disc']:
        output_video = source.transform(transform_video, apply_to="mask").with_effects([moviepy.vfx.FadeOut(fade_out),
                                                                                       moviepy.vfx.FadeIn(fade_in)])
        video_length = output_video.duration
        target_bitrate = str(int(0.90*8000000*config['Encoding options'].getfloat('output_file_size')/video_length))
        output_video.write_videofile(output_filename,
                                     codec = 'libx264',
                                     preset = config['Encoding options'].get('preset'),
                                     threads = config['Encoding options'].getint('threads'),
                                     bitrate = target_bitrate,
                                     audio_bitrate = str(int(target_bitrate)//100),
                                     ffmpeg_params = ['-movflags', 'faststart']
                                     )
    elif encode_style in ['Youtube', 'youtube', 'YT', 'Yt', 'yt', 'YOUTUBE', 'y', 'Y']: #https://gist.github.com/wuziq/b86f8551902fa1d477980a8125970877
        output_video = source.transform(transform_video, apply_to="mask").with_effects([moviepy.vfx.FadeOut(fade_out),
                                                                                        moviepy.vfx.FadeIn(fade_in)])
        output_video.write_videofile(output_filename,
                                     codec = 'libx264',
                                     preset = config['Encoding options'].get('preset'),
                                     threads = config['Encoding options'].getint('threads'),
                                     ffmpeg_params = ['-movflags', 'faststart',
                                                      '-profile:v' ,'high',
                                                      '-bf', '2',
                                                      '-g', '30',
                                                      '-coder' ,'1',
                                                      '-crf' ,'16',
                                                      '-pix_fmt', 'yuv420p',
                                                      '-c:a', 'aac', '-profile:a', 'aac_low',
                                                      '-b:a' ,'384k'])
    
    else:
        no_vid = True
        counter = 0
        for frame in source.iter_frames():
            counter += 1
            if counter == int(encode_style):
                im = Image.fromarray(transform_image(frame, counter))
                im.show()
                im.save(f'{counter}.png')
    if not no_vid :           
        print('time : ', time.time() -t)
        print('frames expected :', -1+len(os.listdir(os.path.join(current_folder, 'RAM_data'))))
        print('frames dumped :', round(output_video.fps * output_video.duration))
        input('Press ENTER to exit')
main()
