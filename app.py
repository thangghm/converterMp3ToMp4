import os
import requests
from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

# Cấu hình AWS
AWS_ACCESS_KEY_ID = 'your_access_key_id'
AWS_SECRET_ACCESS_KEY = 'your_secret_access_key'
AWS_BUCKET_NAME = 'your_bucket_name'
AWS_REGION = 'your_region'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/create_video', methods=['POST'])
def create_video():
    data = request.json
    image_url = data.get('image_url')
    mp3_url = data.get('mp3_url')

    if not image_url or not mp3_url:
        return jsonify({'error': 'Missing image_url or mp3_url'}), 400

    # Tên file tạm thời để lưu trữ ảnh và mp3
    image_file = "image.jpg"
    mp3_file = "audio.mp3"
    output_file = "output_video.mp4"

    try:
        # Tải ảnh
        response = requests.get(image_url)
        with open(image_file, 'wb') as file:
            file.write(response.content)

        # Tải mp3
        response = requests.get(mp3_url)
        with open(mp3_file, 'wb') as file:
            file.write(response.content)

        # Sử dụng FFmpeg để tạo video
        os.system(f"ffmpeg -loop 1 -i {image_file} -i {mp3_file} -c:v libx264 -c:a aac -b:a 192k -shortest {output_file}")

        # Upload file MP4 lên S3
        s3_client.upload_file(output_file, AWS_BUCKET_NAME, output_file)
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{output_file}"

        # Xóa file tạm thời
        os.remove(image_file)
        os.remove(mp3_file)
        os.remove(output_file)

        return jsonify({'message': 'Video created and uploaded successfully', 'video_url': s3_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
