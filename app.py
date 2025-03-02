from flask import Flask, send_from_directory, render_template_string, request
import os

app = Flask(__name__)

# Paths to the folders containing images and GIFs
TEMP_FOLDER = os.path.join('public', 'temp')
HL_FOLDER = os.path.join('public', 'HL')
NORTHEAST_FOLDER = os.path.join('public', 'RS', 'Northeast')
USA_FOLDER = os.path.join('public', 'RS', 'USA')

@app.route('/', methods=['GET'])
def index():
    # Get list of image and GIF files from all folders
    temp_files = [f for f in os.listdir(TEMP_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    hl_files = [f for f in os.listdir(HL_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    northeast_files = [f for f in os.listdir(NORTHEAST_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    usa_files = [f for f in os.listdir(USA_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Get selected folder and file from the dropdown (default to first file in 'temp' folder)
    selected_folder = request.args.get('folder', 'temp')
    selected_file = request.args.get('selected', temp_files[0] if selected_folder == 'temp' else
                                    hl_files[0] if selected_folder == 'HL' else
                                    northeast_files[0] if selected_folder == 'Northeast' else
                                    usa_files[0] if selected_folder == 'USA' else '')

    # Choose the appropriate folder and file list based on selection
    if selected_folder == 'temp':
        files = temp_files
        folder_path = TEMP_FOLDER
    elif selected_folder == 'HL':
        files = hl_files
        folder_path = HL_FOLDER
    elif selected_folder == 'Northeast':
        files = northeast_files
        folder_path = NORTHEAST_FOLDER
    else:
        files = usa_files
        folder_path = USA_FOLDER

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Gallery</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 0;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                background-color: #f0f0f0;
            }
            select {
                padding: 10px;
                font-size: 18px;
                margin-bottom: 20px;
            }
            img {
                max-width: 100%;
                max-height: 90vh;
                object-fit: contain;
                border-radius: 10px;
            }
            h1 {
                margin-bottom: 20px;
                font-size: 2em;
            }
        </style>
        <script>
            function updateImage() {
                var selectedFile = document.getElementById("imageSelector").value;
                var selectedFolder = document.getElementById("folderSelector").value;
                window.location.href = "/?folder=" + selectedFolder + "&selected=" + selectedFile;
            }
        </script>
    </head>
    <body>
        <h1>Image & GIF Viewer</h1>

        <!-- Folder Selector -->
        <label for="folderSelector">Select folder:</label>
        <select id="folderSelector" onchange="updateImage()">
            <option value="temp" {% if selected_folder == 'temp' %}selected{% endif %}>Temp Folder</option>
            <option value="HL" {% if selected_folder == 'HL' %}selected{% endif %}>HL Folder</option>
            <option value="Northeast" {% if selected_folder == 'Northeast' %}selected{% endif %}>Northeast Folder</option>
            <option value="USA" {% if selected_folder == 'USA' %}selected{% endif %}>USA Folder</option>
        </select>
        <br><br>

        <!-- Image Selector -->
        <label for="imageSelector">Select an image:</label>
        <select id="imageSelector" onchange="updateImage()">
            {% for file in files %}
                <option value="{{ file }}" {% if file == selected_file %}selected{% endif %}>{{ file }}</option>
            {% endfor %}
        </select>

        <br><br>
        {% if selected_file %}
            <img src="{{ url_for('get_image', folder=selected_folder, filename=selected_file) }}" alt="{{ selected_file }}">
        {% else %}
            <p>No images found in the selected folder.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_content, files=files, selected_file=selected_file, selected_folder=selected_folder)

@app.route('/images/<folder>/<filename>')
def get_image(folder, filename):
    # Serve image from the selected folder
    if folder == 'temp':
        return send_from_directory(TEMP_FOLDER, filename)
    elif folder == 'HL':
        return send_from_directory(HL_FOLDER, filename)
    elif folder == 'Northeast':
        return send_from_directory(NORTHEAST_FOLDER, filename)
    elif folder == 'USA':
        return send_from_directory(USA_FOLDER, filename)
    return "Folder not found", 404

if __name__ == '__main__':
    app.run(debug=True)
