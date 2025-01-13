import re
import json
import os


def read_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

#* step 1: 대본 srt 파일을 편집하기 쉬운 형식으로 변환

"""
1 00:00:10,010 --> 00:00:11,971 [잔잔한 음악]
2 00:00:16,559 --> 00:00:17,893 [부서지는 효과음]
"""

def format_srt_file(file_path, output_path):
    lines = read_srt_file(file_path)

    merged_lines = []
    buffer = []

    for line in lines:
        if re.match(r'^\d+$', line.strip()):
            if buffer:
                merged_lines.append(' '.join(buffer).strip())
                buffer = []
            buffer.append(line.strip())
        elif re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            buffer.append(line.strip())
        else:
            buffer.append(line.strip())

    if buffer:
        merged_lines.append(' '.join(buffer).strip())

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in merged_lines:
            file.write(line + '\n')

#* step2: 타임스탬프와 번호는 따로 json 파일로 저장.
"""
{
    "1": ["00:00:10,010", "00:00:11,971"],
    "2": ["00:00:16,559", "00:00:17,893"],
}
"""
def timestamp_map(file_path):
    timestamp_map = {}
    lines = read_srt_file(file_path)

    for line in lines:
        if re.match(r'^\d+$', line.strip()):
            subtitle_number = int(line.strip())
        elif re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            timestamps = line.strip().split(' --> ')
            timestamp_map[subtitle_number] = timestamps

    return timestamp_map

def save_timestamp_map_to_json(file_path, output_json_path):
    timestamp_map_data = timestamp_map(file_path)
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(timestamp_map_data, json_file, ensure_ascii=False, indent=4)


#* step3: cleaned된 대본 파일 번호에 해당하는 타임스탬프만 json 파일로 저장

def save_cleaned_timestamp_map_to_json(cleaned_output, original_timestamp, cleaned_output_json_path):
    original_timestamp = json.load(open(original_timestamp, 'r', encoding='utf-8'))
    cleaned_timestamp_map = {}
    lines = read_srt_file(cleaned_output)
    for line in lines:
        number = line.strip().split('  ')[0]
        for key in original_timestamp.keys():
            if number == key:
                cleaned_timestamp_map[number] = original_timestamp[key]

    with open(cleaned_output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(cleaned_timestamp_map, json_file, ensure_ascii=False, indent=4)


#*  output.txt 파일에서 타임스탬프를 삭제하고, 또한 효과음만 있는 경우는 아예 그줄을 삭제하여 다시 저장
def remove_timestamps_and_sound_effects(file_path, output_path):
    lines = read_srt_file(file_path)
    result = []

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            # delete timestamps
            line = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', line)

            if re.match(r'^\d+  \[.*\]$', line):
                continue

            file.write(line)

        
if __name__ == '__main__':

    srt_file_folder = ""
    output_folder = ""

    def main(folder_path,output_folder):
        srt_file_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.srt'):
                    srt_file_path = os.path.join(root, file)
                    se = srt_file_path.split('/')[-1].split('.')[3]
                    os.makedirs(os.path.join(output_folder, se), exist_ok=True) # make folder for each episode

                    format_srt_file(srt_file_path, os.path.join(output_folder, se, file))
                    remove_timestamps_and_sound_effects(os.path.join(output_folder, se, file), os.path.join(output_folder, se, 'cleaned_'+file))
                    save_cleaned_timestamp_map_to_json(os.path.join(output_folder, se, 'cleaned_'+file), os.path.join(output_folder, se, 'timestamp_map.json'), os.path.join(output_folder, se, 'cleaned_timestamp_map.json'))

    srt_file_paths = main(srt_file_folder,output_folder)    