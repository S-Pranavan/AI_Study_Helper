from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from ocr_pipeline import OCRPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# OCR configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR pipeline
ocr_pipeline = OCRPipeline()

# Database initialization
def init_db():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            duration_minutes INTEGER,
            notes TEXT,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # Add OCR results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            confidence REAL,
            processing_time REAL,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def store_ocr_result(result):
    """Store OCR result in database."""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ocr_results (filename, extracted_text, confidence, processing_time, file_size)
        VALUES (?, ?, ?, ?, ?)
    ''', (result['filename'], result['text'], result['confidence'], 
          result['processing_time'], result['file_size']))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ocr')
def ocr_page():
    """OCR processing page."""
    return render_template('index.html')

@app.route('/api/ocr/upload', methods=['POST'])
def upload_and_process():
    """
    Handle image upload and OCR processing.
    Implements image preprocessing and text extraction.
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {safe_filename}")
        
        # Process with OCR
        start_time = datetime.now()
        result = ocr_pipeline.extract_text(filepath, preprocess=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Add processing metadata
        result['filename'] = safe_filename
        result['processing_time'] = processing_time
        result['file_size'] = os.path.getsize(filepath)
        
        # Store result in database
        if result['success']:
            store_ocr_result(result)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        logger.info(f"OCR processing completed for {safe_filename}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in upload and processing: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'details': str(e)
        }), 500

@app.route('/api/ocr/batch', methods=['POST'])
def batch_ocr():
    """
    Handle batch OCR processing for multiple images.
    """
    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Save files temporarily
        temp_files = []
        for file in files:
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
                file.save(filepath)
                temp_files.append(filepath)
        
        if not temp_files:
            return jsonify({'error': 'No valid files found'}), 400
        
        # Process batch
        start_time = datetime.now()
        results = ocr_pipeline.batch_process(temp_files, preprocess=True)
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Clean up temporary files
        for filepath in temp_files:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Add batch metadata
        batch_result = {
            'success': True,
            'total_files': len(results),
            'total_processing_time': total_time,
            'average_processing_time': total_time / len(results),
            'results': results
        }
        
        logger.info(f"Batch OCR completed: {len(results)} files in {total_time:.2f}s")
        return jsonify(batch_result)
        
    except Exception as e:
        logger.error(f"Error in batch OCR: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Batch processing failed',
            'details': str(e)
        }), 500

@app.route('/api/ocr/info')
def get_ocr_info():
    """Get OCR system information."""
    try:
        info = ocr_pipeline.get_ocr_info()
        return jsonify({
            'success': True,
            'ocr_info': info
        })
    except Exception as e:
        logger.error(f"Error getting OCR info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr/results')
def get_ocr_results():
    """Get OCR processing history."""
    try:
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ocr_results 
            ORDER BY created_at DESC 
            LIMIT 50
        ''')
        results = cursor.fetchall()
        conn.close()
        
        # Format results
        formatted_results = []
        for row in results:
            formatted_results.append({
                'id': row[0],
                'filename': row[1],
                'extracted_text': row[2],
                'confidence': row[3],
                'processing_time': row[4],
                'file_size': row[5],
                'created_at': row[6]
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results
        })
        
    except Exception as e:
        logger.error(f"Error getting OCR results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/subjects')
def subjects():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO subjects (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            flash('Subject added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Subject with this name already exists!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('subjects'))
    
    return render_template('add_subject.html')

@app.route('/study_session', methods=['GET', 'POST'])
def study_session():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        duration = request.form['duration']
        notes = request.form['notes']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO study_sessions (subject_id, duration_minutes, notes) VALUES (?, ?, ?)', 
                      (subject_id, duration, notes))
        conn.commit()
        conn.close()
        
        flash('Study session recorded!', 'success')
        return redirect(url_for('study_session'))
    
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('study_session.html', subjects=subjects)

@app.route('/flashcards')
def flashcards():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, s.name as subject_name 
        FROM flashcards f 
        JOIN subjects s ON f.subject_id = s.id 
        ORDER BY s.name, f.created_at DESC
    ''')
    flashcards = cursor.fetchall()
    conn.close()
    return render_template('flashcards.html', flashcards=flashcards)

@app.route('/add_flashcard', methods=['GET', 'POST'])
def add_flashcard():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        question = request.form['question']
        answer = request.form['answer']
        difficulty = request.form['difficulty']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO flashcards (subject_id, question, answer, difficulty) VALUES (?, ?, ?, ?)', 
                      (subject_id, question, answer, difficulty))
        conn.commit()
        conn.close()
        
        flash('Flashcard added successfully!', 'success')
        return redirect(url_for('flashcards'))
    
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('add_flashcard.html', subjects=subjects)

@app.route('/api/subjects')
def api_subjects():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    subjects_list = []
    for subject in subjects:
        subjects_list.append({
            'id': subject[0],
            'name': subject[1],
            'description': subject[2],
            'created_at': subject[3]
        })
    
    return jsonify(subjects_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
