import os
import subprocess
import schedule
import time
import threading
from datetime import datetime
from flask import Flask, render_template, send_from_directory, abort, jsonify

app = Flask(__name__)

# Define the folder path for RS images
rs_folder = os.path.join(os.getcwd(), 'public', 'RS')

def run_gfs_script():
    """Function to run the gfsrainandsnow.py script."""
    print(f"Running gfsrainandsnow.py at {datetime.now()}...")
    script_path = os.path.join(os.getcwd(), 'rainsnow', 'gfsrainandsnow.py')  # Path to the script
    try:
        # Run the script with a timeout of 5 minutes (300 seconds)
        result = subprocess.run(
            ['python', script_path],
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=300  # Timeout after 5 minutes
        )
        print(f"Script finished: {result.stdout}")  # Print script output
    except subprocess.CalledProcessError as e:
        print(f"Error running gfsrainandsnow.py: {e.stderr}")  # Log error
    except subprocess.TimeoutExpired:
        print("gfsrainandsnow.py timed out after 5 minutes.")  # Log timeout error

# Schedule the task to run at 12:10 AM, 6:10 AM, 12:10 PM, and 6:10 PM
schedule.every().day.at("00:10").do(run_gfs_script)  # 12:10 AM
schedule.every().day.at("06:10").do(run_gfs_script)  # 6:10 AM
schedule.every().day.at("12:10").do(run_gfs_script)  # 12:10 PM
schedule.every().day.at("18:10").do(run_gfs_script)  # 6:10 PM

def run_scheduler():
    """Run the scheduler in a separate thread to allow Flask to run."""
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True  # Make sure the thread ends when the main program ends
scheduler_thread.start()

@app.route('/')
def index():
    if not os.path.exists(rs_folder):
        return "Image directory not found", 404

    image_files = [f for f in os.listdir(rs_folder) if f.lower().endswith(('.png', '.gif'))]

    if not image_files:
        return "No images found", 404

    return render_template('index.html', image_files=image_files)

@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory(rs_folder, filename)
    except Exception:
        abort(404)

@app.route('/run-script')
def run_script():
    """Manually run the gfsrainandsnow.py script and return output."""
    script_path = os.path.join(os.getcwd(), 'rainsnow', 'gfsrainandsnow.py')  # Path to the script
    print(f"Running {script_path}...")  # Terminal message when script starts

    try:
        # Run the script with a timeout of 5 minutes (300 seconds)
        result = subprocess.run(
            ['python', script_path],
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=300  # Timeout after 5 minutes
        )

        print("gfsrainandsnow.py finished running.")  # Terminal message after script completes

        # Check if the GIF file is created (optional check to ensure successful execution)
        gif_files = [f for f in os.listdir(rs_folder) if f.lower().endswith('.gif')]
        if gif_files:
            print(f"GIF file created: {gif_files[0]}")
        else:
            print("No GIF file created.")

        return jsonify({"output": result.stdout, "error": result.stderr})
    except subprocess.CalledProcessError as e:
        print(f"Error running gfsrainandsnow.py: {e.stderr}")  # Log the detailed error
        return jsonify({"error": str(e), "output": e.stderr})
    except subprocess.TimeoutExpired:
        print("gfsrainandsnow.py timed out after 5 minutes.")  # Log timeout error
        return jsonify({"error": "gfsrainandsnow.py timed out", "output": ""})

if __name__ == '__main__':
    print("Flask app is running! Visit http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)  # Disable reloader if using scheduling in a thread
