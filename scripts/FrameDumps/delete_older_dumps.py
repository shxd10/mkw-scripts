import sys
import os

'''
This script simply delete all audio (.wav only) and
video (.avi only) your Dump/Frames and Dump/Audio folder
Don't run this script before encoding !
'''


print('Are you sure you want to delete all your dumps ?')
answer = input('yes/no\n')
if answer in ['yes', 'y', 'ye', 'YES', 'Y', 'YE']:
    with open('dump_info.txt', 'r') as f:
        dump_folder = f.readline().strip('\n')
        frame_dump_path = os.path.join(dump_folder, 'Frames')
        audio_dump_path = os.path.join(dump_folder, 'Audio')
        for filename in os.listdir(frame_dump_path):
            if filename[-4:] == '.avi':
                print(f'Now deleting {filename}')
                os.remove(os.path.join(frame_dump_path, filename))
        
        for filename in os.listdir(audio_dump_path):
            if filename[-4:] == '.wav':
                print(f'Now deleting {filename}')
                os.remove(os.path.join(audio_dump_path, filename))

    print('All dumps have been deleted.')
    
input("Press Enter to exit")
