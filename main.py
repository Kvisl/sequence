import os
import re
import subprocess

# INPUT_DIR = " "  # Путь к директории, в которой находятся исходные изображения
# OUTPUT_DIR = " "  # Путь к директории, куда будут сохраняться видео
FRAME_RATE = 24  # Частота кадров в секунду
CODEC = 'mjpeg'  # Кодек для выходного видео


# Функция для поиска всех jpg файлов
def find_jpg_files(input_dir):
    jpg_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                jpg_files.append(os.path.join(root, file))
    return jpg_files


# Функция для группировки файлов по секвенциям
def group_files_by_sequence(jpg_files):
    sequences = {}
    pattern = re.compile(r'(.+?)(?:_(\d+))?_(\d+)\.jpg$|(.+?)(\d+)(?:[._](\d+))?\.jpg$', re.IGNORECASE)

    for file in jpg_files:
        basename = os.path.basename(file)
        match = pattern.match(basename)

        if match:
            if match.group(1):  # Если соответствует первому формату
                sequence_name = match.group(1)
                frame_number = match.group(3)
            else:  # Если соответствует второму формату
                sequence_name = match.group(4)
                frame_number = match.group(5)

            if frame_number is None:
                continue

            frame_number_length = len(frame_number)
            sequence_key = (sequence_name, frame_number_length)

            if sequence_key not in sequences:
                sequences[sequence_key] = []

            sequences[sequence_key].append(file)

    # Сортируем файлы в каждой секвенции по номерам кадров
    for key in sequences:
        sequences[key].sort()

    return sequences


# Функция для создания видео из секвенции
def create_video_from_sequence(sequence_files, output_file, frame_number_length):
    basename = os.path.basename(sequence_files[0])
    name_parts = re.split(r'(\d+)\.jpg$', basename)

    if len(name_parts) < 2:
        return

    sequence_name = name_parts[0]
    frame_number = name_parts[1]

    if frame_number.startswith('0'):
        frame_number_length = len(frame_number)  #
        input_pattern = os.path.join(os.path.dirname(sequence_files[0]), f'{sequence_name}%0{frame_number_length}d.jpg')
    else:
        input_pattern = os.path.join(os.path.dirname(sequence_files[0]), f'{sequence_name}%d.jpg')

    ffmpeg_cmd = [
        'ffmpeg',
        '-r', str(FRAME_RATE),  # Частота кадров
        '-start_number', str(frame_number),  # Начальный номер кадра
        '-i', input_pattern,  # Шаблон для последовательности кадров
        '-c:v', CODEC,  # Кодек для видео
        '-r', str(FRAME_RATE),
        output_file
    ]

    subprocess.run(ffmpeg_cmd, check=True)

