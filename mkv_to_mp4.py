import os
import subprocess

def convert_mkv_to_mp4(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-codec', 'copy', output_file]
    subprocess.run(command, check=True)

if __name__ == '__main__':
    convert_mkv_to_mp4('/hub_data2/taehoonlee/clips/S01E03/merged_video_S01E03.mkv', '/home/taehoonlee/KT/mp4s/Marry.My.Husband.S01E03.1080p.x264.AAC-BCG.mp4')