# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return 'Hello, world!'

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# import requests
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route('/create_video', methods=['POST'])
# def create_video():
#     data = request.json
#     image_url = data.get('image_url')
#     mp3_url = data.get('mp3_url')

#     if not image_url or not mp3_url:
#         return jsonify({'error': 'Missing image_url or mp3_url'}), 400

#     image_file = "image.jpg"
#     mp3_file = "audio.mp3"
#     output_file = "output_video.mp4"

#     try:
#         response = requests.get(image_url)
#         with open(image_file, 'wb') as file:
#             file.write(response.content)

#         response = requests.get(mp3_url)
#         with open(mp3_file, 'wb') as file:
#             file.write(response.content)

#         os.system(f"ffmpeg -loop 1 -i {image_file} -i {mp3_file} -c:v libx264 -c:a aac -b:a 192k -shortest {output_file}")

#         os.remove(image_file)
#         os.remove(mp3_file)

#         return jsonify({'message': 'Video created successfully', 'output_file': output_file})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import requests
import boto3
from flask import Flask, request, jsonify
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)

# Initialize the S3 client using environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)

# S3 bucket name from environment variable
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

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
        # Download image
        response = requests.get(image_url)
        with open(image_file, 'wb') as file:
            file.write(response.content)

        # Download mp3
        response = requests.get(mp3_url)
        with open(mp3_file, 'wb') as file:
            file.write(response.content)

        # Create video with ffmpeg
        os.system(f"ffmpeg -loop 1 -i {image_file} -i {mp3_file} -c:v libx264 -c:a aac -b:a 192k -shortest {output_file}")

        # Clean up local files
        os.remove(image_file)
        os.remove(mp3_file)

        # Upload video to S3
        try:
            s3_client.upload_file(output_file, BUCKET_NAME, output_file)
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{output_file}"
        except (NoCredentialsError, PartialCredentialsError):
            return jsonify({'error': 'Credentials not available'}), 500

        # Clean up the local output video file
        os.remove(output_file)

        return jsonify({'message': 'Video created and uploaded successfully', 's3_url': s3_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
