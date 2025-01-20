from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Define the folder path for RS images
rs_folder = os.path.join(os.getcwd(), 'public', 'RS')

@app.route('/')
def index():
    # Get a list of all image files (png, gif) in the RS folder
    image_files = [f for f in os.listdir(rs_folder) if f.endswith(('.png', '.gif'))]
    
    # Pass the list of image files to the template
    return render_template('index.html', image_files=image_files)

@app.route('/images/<filename>')
def serve_image(filename):
    # Dynamically serve images and GIF from the 'RS' folder
    return send_from_directory(rs_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
