"""
Web Interface for PeopleCounter
Flask application for uploading videos and processing them
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import sys
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle video file upload"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'message': 'File uploaded successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_video():
    """Process uploaded video"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Copy file to data folder for processing
        import shutil
        data_folder = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        target_path = os.path.join(data_folder, 'mall_entry.mp4')
        shutil.copy(filepath, target_path)
        # Remove old report if present so status reflects the new run
        report_path = os.path.join(os.path.dirname(__file__), 'people_counter_report.html')
        try:
            if os.path.exists(report_path):
                os.remove(report_path)
        except Exception:
            pass

        # Run main.py in subprocess and pass the original uploaded filepath so
        # the processing script can delete it after finishing.
        python_exe = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'python.exe')
        if not os.path.exists(python_exe):
            # Fallback to system python
            python_exe = sys.executable

        # Start processing in background and pass the uploaded file path
        main_py = os.path.join(os.path.dirname(__file__), 'main.py')
        try:
            subprocess.Popen([python_exe, main_py, filepath], cwd=os.path.dirname(__file__))
        except Exception:
            # Fallback to running without argument if something goes wrong
            subprocess.Popen([python_exe, main_py], cwd=os.path.dirname(__file__))
        
        return jsonify({
            'success': True,
            'message': 'Video processing started. The application will open in a moment.',
            'status': 'processing'
        }), 200
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in process_video: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500


@app.route('/status')
def status():
    """Check if processing is complete"""
    report_path = 'people_counter_report.html'
    report_exists = os.path.exists(report_path)
    
    return jsonify({
        'report_generated': report_exists,
        'report_path': report_path if report_exists else None
    }), 200


@app.route('/report')
def get_report():
    """Serve the generated report"""
    report_path = 'people_counter_report.html'
    if os.path.exists(report_path):
        return send_file(report_path, mimetype='text/html')
    else:
        return jsonify({'error': 'Report not generated yet'}), 404


if __name__ == '__main__':
    print("Starting PeopleCounter Web Interface...")
    print("Navigate to http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
