from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from yolov4 import detect_cars
from algo import optimize_traffic

app = Flask(__name__)
CORS(app)

# Ensure the upload directory exists
UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        files = request.files.getlist('videos')
        if len(files) != 4:
            return jsonify({'error': 'Please upload exactly 4 videos'}), 400

        video_paths = []
        for i, file in enumerate(files):
            if not file.filename.endswith(('.mp4', '.avi', '.mov')):  # Validate file type
                return jsonify({'error': f'File {file.filename} is not a valid video format'}), 400
            
            video_path = os.path.join(UPLOAD_DIR, f'video_{i}.mp4')
            file.save(video_path)
            video_paths.append(video_path)

        num_cars_list = []
        for video_file in video_paths:
            try:
                num_cars = detect_cars(video_file)
                num_cars_list.append(num_cars)
            except Exception as e:
                return jsonify({'error': f'Error processing video {video_file}: {str(e)}'}), 500

        try:
            result = optimize_traffic(num_cars_list)
        except Exception as e:
            return jsonify({'error': f'Error optimizing traffic: {str(e)}'}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
