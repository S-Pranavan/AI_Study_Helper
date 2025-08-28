#!/usr/bin/env python3
"""
AI Study Helper - Phase 2: AI Content Generation
Flask application with OCR and AI-powered content generation
"""

import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import json

# Import our modules
from ocr_pipeline import OCRPipeline
from ai_content_generator import AIContentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-study-helper-phase2-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR and AI components
ocr_pipeline = None
ai_generator = None

def init_components():
    """Initialize OCR and AI components"""
    global ocr_pipeline, ai_generator
    
    try:
        # Initialize OCR pipeline
        logger.info("Initializing OCR pipeline...")
        ocr_pipeline = OCRPipeline()
        
        # Initialize AI content generator
        logger.info("Initializing AI content generator...")
        ai_generator = AIContentGenerator(use_gpu=False)
        
        logger.info("All components initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        # Continue without AI if there's an error
        ai_generator = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize database with Phase 2 tables"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Phase 1 tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            processing_time REAL,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Phase 2 tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ocr_result_id INTEGER,
            content_type TEXT NOT NULL,
            generated_content TEXT NOT NULL,
            model_used TEXT NOT NULL,
            processing_time REAL,
            confidence_score REAL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ocr_result_id) REFERENCES ocr_results (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT NOT NULL,
            content_summary TEXT,
            keywords TEXT,
            explanation TEXT,
            duration_minutes INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def store_ocr_result(result):
    """Store OCR result in database"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ocr_results (filename, extracted_text, processing_time, file_size)
        VALUES (?, ?, ?, ?)
    ''', (
        result.get('filename', ''),
        result.get('extracted_text', ''),
        result.get('processing_time', 0),
        result.get('file_size', 0)
    ))
    
    conn.commit()
    conn.close()

def store_ai_content(ocr_result_id, content_type, result):
    """Store AI-generated content in database"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    metadata = json.dumps(result.metadata) if result.metadata else None
    
    cursor.execute('''
        INSERT INTO ai_generated_content 
        (ocr_result_id, content_type, generated_content, model_used, processing_time, confidence_score, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ocr_result_id,
        content_type,
        result.content,
        result.model_used,
        result.processing_time,
        result.confidence_score,
        metadata
    ))
    
    conn.commit()
    conn.close()

def get_ocr_result_id(filename):
    """Get OCR result ID by filename"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM ocr_results WHERE filename = ? ORDER BY created_at DESC LIMIT 1', (filename,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None

@app.route('/')
def index():
    """Main page with Phase 2 features"""
    return render_template('index_v3.html')

@app.route('/api/ocr/upload', methods=['POST'])
def upload_and_process():
    """Upload image, perform OCR, and generate AI content"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(filepath)

        # Perform OCR
        start_time = datetime.now()
        ocr_result = ocr_pipeline.extract_text(filepath, preprocess=True)
        ocr_time = (datetime.now() - start_time).total_seconds()

        # Add OCR metadata
        ocr_result['filename'] = safe_filename
        ocr_result['processing_time'] = ocr_time
        ocr_result['file_size'] = os.path.getsize(filepath)

        # Store OCR result
        if ocr_result['success']:
            store_ocr_result(ocr_result)
            ocr_result_id = get_ocr_result_id(safe_filename)
            
            # Generate AI content if OCR was successful and AI is available
            ai_results = {}
            if ai_generator and ocr_result_id:
                try:
                    extracted_text = ocr_result['extracted_text']
                    
                    # Generate AI content
                    ai_start_time = datetime.now()
                    ai_results = ai_generator.generate_study_materials(extracted_text)
                    ai_time = (datetime.now() - ai_start_time).total_seconds()
                    
                    # Store AI results
                    for content_type, result in ai_results.items():
                        if result.success:
                            store_ai_content(ocr_result_id, content_type, result)
                    
                    # Add AI results to response
                    ocr_result['ai_content'] = {
                        'summary': ai_results.get('summary', {}),
                        'explanation': ai_results.get('explanation', {}),
                        'keywords': ai_results.get('keywords', {}),
                        'total_ai_time': ai_time
                    }
                    
                except Exception as e:
                    logger.error(f"Error generating AI content: {str(e)}")
                    ocr_result['ai_content'] = {
                        'error': 'AI content generation failed',
                        'details': str(e)
                    }

        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(ocr_result)
        
    except Exception as e:
        logger.error(f"Error in upload and processing: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'details': str(e)
        }), 500

@app.route('/api/ai/generate', methods=['POST'])
def generate_ai_content():
    """Generate AI content from text input"""
    try:
        if not ai_generator:
            return jsonify({'error': 'AI generator not available'}), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text input required'}), 400
        
        text = data['text']
        content_types = data.get('content_types', ['summary', 'explanation', 'keywords'])
        
        results = {}
        
        if 'summary' in content_types:
            results['summary'] = ai_generator.generate_summary(text)
        
        if 'explanation' in content_types:
            style = data.get('explanation_style', 'simple')
            results['explanation'] = ai_generator.generate_explanation(text, style)
        
        if 'keywords' in content_types:
            max_keywords = data.get('max_keywords', 10)
            results['keywords'] = ai_generator.extract_keywords(text, max_keywords)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error generating AI content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'AI content generation failed',
            'details': str(e)
        }), 500

@app.route('/api/ai/models', methods=['GET'])
def get_ai_models():
    """Get information about available AI models"""
    if not ai_generator:
        return jsonify({'error': 'AI generator not available'}), 503
    
    try:
        model_info = ai_generator.get_model_info()
        return jsonify({
            'success': True,
            'models': model_info
        })
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get model information',
            'details': str(e)
        }), 500

@app.route('/api/study-sessions', methods=['POST'])
def create_study_session():
    """Create a new study session with AI-generated content"""
    try:
        data = request.get_json()
        if not data or 'session_name' not in data:
            return jsonify({'error': 'Session name required'}), 400
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO study_sessions 
            (session_name, content_summary, keywords, explanation, duration_minutes, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['session_name'],
            data.get('content_summary', ''),
            data.get('keywords', ''),
            data.get('explanation', ''),
            data.get('duration_minutes', 0),
            data.get('notes', '')
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Study session created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating study session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create study session',
            'details': str(e)
        }), 500

@app.route('/api/study-sessions', methods=['GET'])
def get_study_sessions():
    """Get all study sessions"""
    try:
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_name, content_summary, keywords, explanation, 
                   duration_minutes, notes, created_at
            FROM study_sessions 
            ORDER BY created_at DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'session_name': row[1],
                'content_summary': row[2],
                'keywords': row[3],
                'explanation': row[4],
                'duration_minutes': row[5],
                'notes': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
        
    except Exception as e:
        logger.error(f"Error getting study sessions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get study sessions',
            'details': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'phase': 'Phase 2: AI Content Generation',
        'components': {
            'ocr_pipeline': ocr_pipeline is not None,
            'ai_generator': ai_generator is not None
        }
    })

@app.route('/api/ocr/info', methods=['GET'])
def ocr_info():
    """Get OCR system information"""
    if not ocr_pipeline:
        return jsonify({'error': 'OCR pipeline not available'}), 503
    
    try:
        info = ocr_pipeline.get_system_info()
        return jsonify({
            'success': True,
            'ocr_info': info
        })
    except Exception as e:
        logger.error(f"Error getting OCR info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get OCR information',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Initialize components
    init_components()
    
    # Start Flask app
    print("🚀 Starting AI Study Helper - Phase 2...")
    print("📚 AI Content Generation with OCR Pipeline")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
