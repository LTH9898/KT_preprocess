import os
import json
from pymkv import MKVFile
import ffmpeg

def parse_json_timestamps(json_data):
    timestamps = []
    for key, value in json_data.items():
        start = value[0].replace(",", ".")  # FFmpeg에서는 ',' 대신 '.' 사용
        end = value[1].replace(",", ".")
        timestamps.append((start, end))
    return timestamps

def extract_clips_from_json(input_file, json_timestamps, output_file):
    timestamps = parse_json_timestamps(json_timestamps)
    inputs = []

    for start, end in timestamps:
        inputs.extend(['-ss', start, '-to', end, '-i', input_file])

    filter_complex = ''.join([f'[{i}:v:0][{i}:a:0]' for i in range(len(timestamps))])
    filter_complex += f'concat=n={len(timestamps)}:v=1:a=1[outv][outa]'

    ffmpeg_cmd = ['ffmpeg'] + inputs + ['-filter_complex', filter_complex, '-map', '[outv]', '-map', '[outa]', output_file]
    os.system(' '.join(ffmpeg_cmd))

if __name__ == "__main__":
    # 내남결 파일이 있는 폴더 경로
    video_folder = ""
    output_folder = ""
    result_folder = ""

    input_mkv_files = [os.path.join(video_folder, f) for f in sorted(os.listdir(video_folder)) if f.endswith(".mkv")]


    # 입력 MKV 파일 경로
    for input_mkv in input_mkv_files:
        # JSON 형식의 타임스탬프 데이터
        se = input_mkv.split('/')[-1].split('.')[3]
        cleaned_timestamp_path = os.path.join(result_folder, se, "cleaned_timestamp_map.json")
        output_mkv_path = os.path.join(output_folder, "clips", se)
        os.makedirs(output_mkv_path, exist_ok=True)
        output_mkv_file = os.path.join(output_mkv_path, f"merged_video_{se}.mkv")

        # print("input_mkv: ", input_mkv)
        # print("cleaned_timestamp_path ", cleaned_timestamp_path)
        # print("output_mkv: ", output_mkv_path)
        # print("output_mkv_file: ", output_mkv_file)

        with open(cleaned_timestamp_path, "r", encoding="utf-8") as f:
            json_timestamps = json.load(f)
        
        # 클립 추출 및 병합

        extract_clips_from_json(input_mkv, json_timestamps, output_mkv_file)

        print(f"새로운 MKV 파일 생성됨: {output_mkv_file}")