from flask import Flask, render_template, send_from_directory, jsonify
import os
import subprocess

app = Flask(__name__, static_folder='public', template_folder='templates')

# Path to the static directory where images will be stored
images_folder = os.path.join(app.static_folder, 'RS')

# Ensure that the images directory exists
if not os.path.exists(images_folder):
    os.makedirs(images_folder)

@app.route('/')
def index():
    # Get the list of available images and gifs in the images folder
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.png', '.gif'))]
    return render_template('index.html', image_files=image_files)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(images_folder, filename)

@app.route('/run-gfs-script', methods=['POST'])
def run_gfs_script():
    try:
        script_path = os.path.join(os.getcwd(), 'rainsnow', 'gfsrainandsnow.py')  # Adjusted to relative path
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        
        # Get updated list of images after script execution
        image_files = [f for f in os.listdir(images_folder) if f.endswith(('.png', '.gif'))]
        return jsonify({"message": "Script executed successfully!", "images": image_files})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": "Error running script.", "error": e.stderr}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)  # For Render deployment
