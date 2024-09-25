from flask import Flask, request
import os
from main import find_jpg_files, group_files_by_sequence, create_video_from_sequence

app = Flask(__name__)


@app.route('/')
def index():
    return '''
        <h1>Конвертация JPG в видео</h1>
        <form method="POST" action="/process" onsubmit="showLoadingMessage()">
            <label for="input_dir">Директория с изображениями:</label>
            <input type="text" id="input_dir" name="input_dir" placeholder="Введите путь к директории с изображениями">
            <br><br>
            <label for="output_dir">Директория для сохранения видео:</label>
            <input type="text" id="output_dir" name="output_dir" placeholder="Введите путь к выходной директории">
            <br><br>
            <input type="submit" value="Создать видео">
        </form>

        <!-- Сообщение о начале обработки -->
        <div id="loading" style="display:none;">
            <h2>Создание видео, пожалуйста, подождите...</h2>
        </div>

        <script>
            function showLoadingMessage() {
                document.getElementById('loading').style.display = 'block';
            }
        </script>
    '''


@app.route('/process', methods=['POST'])
def process():
    input_dir = request.form['input_dir']
    output_dir = request.form['output_dir']

    jpg_files = find_jpg_files(input_dir)

    if not jpg_files:
        return "<h2>Не найдено ни одного .jpg файла!</h2>"

    sequences = group_files_by_sequence(jpg_files)
    if not sequences:
        return "<h2>Не найдено ни одной секвенции!</h2>"

    # Проходим по секвенциям и создаем видео
    for (sequence_name, frame_number_length), sequence_files in sequences.items():
        output_file = os.path.join(output_dir, f'{sequence_name.strip()}.mov')
        create_video_from_sequence(sequence_files, output_file, frame_number_length)

    return f"<h2>Видео успешно создано и сохранено в {output_dir}!</h2>"

if __name__ == '__main__':
    app.run(debug=True)


