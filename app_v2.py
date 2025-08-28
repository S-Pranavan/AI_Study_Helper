"""
AI Study Helper - Enhanced Flask Application
Phase 1 Implementation: Foundation & OCR Setup
"""

from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
import sqlite3
import tempfile
from ocr_pipeline import OCRPipeline
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'ai-study-helper-phase1-secret-key'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR pipeline
ocr_pipeline = OCRPipeline()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Create OCR results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_text TEXT,
            processed_text TEXT,
            confidence REAL,
            word_count INTEGER,
            char_count INTEGER,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create subjects table (for future use)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create study sessions table (for future use)
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
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

@app.route('/')
def index():
    """Main page with OCR functionality."""
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
            SELECT filename, original_text, processed_text, confidence, 
                   word_count, char_count, processing_time, created_at
            FROM ocr_results 
            ORDER BY created_at DESC 
            LIMIT 50
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'filename': row[0],
                'original_text': row[1],
                'processed_text': row[2],
                'confidence': row[3],
                'word_count': row[4],
                'char_count': row[5],
                'processing_time': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error getting OCR results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def store_ocr_result(result):
    """Store OCR result in database."""
    try:
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ocr_results 
            (filename, original_text, processed_text, confidence, word_count, char_count, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['filename'],
            result.get('text', ''),
            result.get('text', ''),
            result.get('confidence', 0.0),
            result.get('word_count', 0),
            result.get('char_count', 0),
            result.get('processing_time', 0.0)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"OCR result stored for {result['filename']}")
        
    except Exception as e:
        logger.error(f"Error storing OCR result: {str(e)}")

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check OCR pipeline
        ocr_info = ocr_pipeline.get_ocr_info()
        
        # Check database
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM ocr_results')
        result_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'ocr_system': ocr_info.get('tesseract_version', 'Unknown'),
            'database': 'connected',
            'total_ocr_results': result_count,
            'version': 'Phase 1 - OCR Foundation'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start Flask application
    logger.info("Starting AI Study Helper - Phase 1 (OCR Foundation)")
    logger.info("OCR Pipeline initialized")
    logger.info("Database initialized")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
