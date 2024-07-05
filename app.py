import os
import requests
import boto3
from flask import Flask, request, jsonify
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)

# Initialize the S3 client using environment variables
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_region = os.environ.get('AWS_REGION')
bucket_name = os.environ.get('S3_BUCKET_NAME')

# Check if any of the environment variables are not set
if not all([aws_access_key_id, aws_secret_access_key, aws_region, bucket_name]):
    raise ValueError("One or more AWS environment variables are not set")

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

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
        # Download the image
        response = requests.get(image_url)
        with open(image_file, 'wb') as file:
            file.write(response.content)

        # Download the audio
        response = requests.get(mp3_url)
        with open(mp3_file, 'wb') as file:
            file.write(response.content)

        # Create the video using ffmpeg
        os.system(f"ffmpeg -loop 1 -i {image_file} -i {mp3_file} -c:v libx264 -c:a aac -b:a 192k -shortest {output_file}")

        # Upload the video to S3
        s3_client.upload_file(output_file, bucket_name, output_file, ExtraArgs={'ACL': 'public-read'})

        # Generate the URL
        s3_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{output_file}"

        # Clean up local files
        os.remove(image_file)
        os.remove(mp3_file)
        os.remove(output_file)

        return jsonify({'message': 'Video created successfully', 'url': s3_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
