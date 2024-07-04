import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/create_video', methods=['POST'])
def create_video():
    data = request.json
    image_url = data.get('image_url')
    mp3_url = data.get('mp3_url')

    if not image_url or not mp3_url:
        return jsonify({'error': 'Missing image_url or mp3_url'}), 400

    image_file = "image.jpg"
    mp3_file = "audio.mp3"
    output_file = "output_video.mp4"

    try:
        response = requests.get(image_url)
        with open(image_file, 'wb') as file:
            file.write(response.content)

        response = requests.get(mp3_url)
        with open(mp3_file, 'wb') as file:
            file.write(response.content)

        os.system(f"ffmpeg -loop 1 -i {image_file} -i {mp3_file} -c:v libx264 -c:a aac -b:a 192k -shortest {output_file}")

        os.remove(image_file)
        os.remove(mp3_file)

        return jsonify({'message': 'Video created successfully', 'output_file': output_file})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
