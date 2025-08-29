"""
AI Study Helper - Phase 5 Flask Application
Integrates OCR, AI Content Generation, Quiz/Flashcard System, and AI Tutor & Mind Maps
"""

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
import logging
import json
from typing import Dict, Any, List

# Import our modules
from ocr_pipeline import OCRPipeline
from quiz_flashcard_generator import QuizFlashcardGenerator
from ai_tutor import AITutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_study_helper_phase5_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
ocr_pipeline = OCRPipeline()
quiz_generator = QuizFlashcardGenerator()
ai_tutor = AITutor()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize database with all phases"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()

    # Phase 1 tables (ocr_results)
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

    # Phase 3 tables are initialized by QuizFlashcardGenerator
    # Phase 4 tables are initialized by AITutor
    # But we'll create a summary table for quick access
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ocr_result_id INTEGER,
            subject TEXT,
            summary TEXT,
            explanation TEXT,
            keywords TEXT,
            quiz_count INTEGER DEFAULT 0,
            flashcard_count INTEGER DEFAULT 0,
            mind_map_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    """Main page with Phase 5 features"""
    return render_template('index_v5.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'phase': 5,
        'features': ['OCR', 'Quiz Generation', 'Flashcard System', 'AI Tutor', 'Mind Maps'],
        'timestamp': datetime.now().isoformat()
    })

# Phase 1: OCR Endpoints
@app.route('/api/ocr/upload', methods=['POST'])
def upload_image():
    """Upload and process image with OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process with OCR
        start_time = datetime.now()
        extracted_text = ocr_pipeline.extract_text(filepath)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Save to database
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ocr_results (filename, extracted_text, processing_time, file_size)
            VALUES (?, ?, ?, ?)
        ''', (filename, extracted_text, processing_time, os.path.getsize(filepath)))
        ocr_result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Generate simple content (without AI models)
        summary = f"Extracted {len(extracted_text)} characters from {filename}"
        keywords = "OCR, Text Extraction, Image Processing"
        explanation = f"Successfully processed image {filename} using OCR technology."
        
        return jsonify({
            'success': True,
            'ocr_result_id': ocr_result_id,
            'extracted_text': extracted_text,
            'summary': summary,
            'keywords': keywords,
            'explanation': explanation,
            'processing_time': processing_time,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

# Phase 3: Quiz & Flashcard Endpoints
@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz from content"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        question_count = data.get('question_count', 5)
        
        if not content or len(content) < 50:
            return jsonify({'error': 'Content too short for quiz generation'}), 400
        
        # Generate quiz using our generator
        quiz_questions = quiz_generator.generate_quiz_from_content(
            content, subject, difficulty, question_count
        )
        
        return jsonify({
            'success': True,
            'quiz_questions': [q.__dict__ for q in quiz_questions],
            'subject': subject,
            'difficulty': difficulty,
            'question_count': len(quiz_questions)
        })
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashcards/generate', methods=['POST'])
def generate_flashcards():
    """Generate flashcards from content"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'easy')
        card_count = data.get('card_count', 5)
        
        if not content or len(content) < 50:
            return jsonify({'error': 'Content too short for flashcard generation'}), 400
        
        # Generate flashcards using our generator
        flashcards = quiz_generator.generate_flashcards_from_content(
            content, subject, difficulty, card_count
        )
        
        return jsonify({
            'success': True,
            'flashcards': [f.__dict__ for f in flashcards],
            'subject': subject,
            'difficulty': difficulty,
            'card_count': len(flashcards)
        })
        
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/questions')
def get_quiz_questions():
    """Get available quiz questions"""
    try:
        questions = quiz_generator.get_all_quiz_questions()
        return jsonify({
            'success': True,
            'questions': [q.__dict__ for q in questions],
            'total_count': len(questions)
        })
    except Exception as e:
        logger.error(f"Error retrieving quiz questions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashcards/review')
def get_flashcards_for_review():
    """Get flashcards due for review"""
    try:
        flashcards = quiz_generator.get_flashcards_for_review()
        return jsonify({
            'success': True,
            'flashcards': [f.__dict__ for f in flashcards],
            'total_count': len(flashcards)
        })
    except Exception as e:
        logger.error(f"Error retrieving flashcards: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz results"""
    try:
        data = request.get_json()
        session_name = data.get('session_name', f'Quiz Session {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        duration_minutes = data.get('duration_minutes', 0)
        
        # Record quiz result
        quiz_generator.record_quiz_result(session_name, subject, difficulty, score, total_questions)
        
        return jsonify({
            'success': True,
            'message': 'Quiz results recorded successfully',
            'session_name': session_name,
            'score': score,
            'total_questions': total_questions
        })
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashcards/review', methods=['POST'])
def record_flashcard_review():
    """Record flashcard review with spaced repetition"""
    try:
        data = request.get_json()
        flashcard_id = data.get('flashcard_id')
        quality = data.get('quality', 3)
        
        if not flashcard_id:
            return jsonify({'error': 'Flashcard ID required'}), 400
        
        # Record review
        quiz_generator.record_flashcard_review(flashcard_id, quality)
        
        return jsonify({
            'success': True,
            'message': 'Flashcard review recorded successfully',
            'flashcard_id': flashcard_id,
            'quality': quality
        })
        
    except Exception as e:
        logger.error(f"Error recording flashcard review: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/statistics')
def get_quiz_statistics():
    """Get quiz performance statistics"""
    try:
        stats = quiz_generator.get_quiz_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error retrieving quiz statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashcards/statistics')
def get_flashcard_statistics():
    """Get flashcard performance statistics"""
    try:
        stats = quiz_generator.get_flashcard_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error retrieving flashcard statistics: {e}")
        return jsonify({'error': str(e)}), 500

# Phase 4: AI Tutor Endpoints
@app.route('/api/tutor/chat/session', methods=['POST'])
def create_chat_session():
    """Create a new AI Tutor chat session"""
    try:
        data = request.get_json()
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        user_level = data.get('user_level', 'intermediate')
        
        session_id = ai_tutor.create_chat_session(subject, difficulty, user_level)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'subject': subject,
            'difficulty': difficulty,
            'user_level': user_level
        })
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tutor/chat/message', methods=['POST'])
def send_chat_message():
    """Send a message to the AI Tutor and get response"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '')
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Get AI response
        response = ai_tutor.get_chat_response(session_id, message, subject, difficulty)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tutor/chat/history/<session_id>')
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        limit = request.args.get('limit', 10, type=int)
        messages = ai_tutor.get_chat_history(session_id, limit)
        
        return jsonify({
            'success': True,
            'messages': [m.__dict__ for m in messages],
            'session_id': session_id,
            'total_count': len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return jsonify({'error': str(e)}), 500

# Phase 4: Mind Maps Endpoints
@app.route('/api/mindmaps/create', methods=['POST'])
def create_mind_map():
    """Create a mind map from content"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        subject = data.get('subject', 'General')
        content = data.get('content', '')
        
        if not title or not content:
            return jsonify({'error': 'Title and content required'}), 400
        
        # Create mind map
        mind_map = ai_tutor.create_mind_map(title, subject, content)
        
        return jsonify({
            'success': True,
            'mind_map': {
                'id': mind_map.id,
                'title': mind_map.title,
                'subject': mind_map.subject,
                'nodes': [n.__dict__ for n in mind_map.nodes],
                'created_at': mind_map.created_at.isoformat(),
                'last_updated': mind_map.last_updated.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating mind map: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mindmaps/<map_id>')
def get_mind_map(map_id):
    """Get a specific mind map by ID"""
    try:
        mind_map = ai_tutor.get_mind_map(map_id)
        
        if not mind_map:
            return jsonify({'error': 'Mind map not found'}), 404
        
        return jsonify({
            'success': True,
            'mind_map': {
                'id': mind_map.id,
                'title': mind_map.title,
                'subject': mind_map.subject,
                'nodes': [n.__dict__ for n in mind_map.nodes],
                'created_at': mind_map.created_at.isoformat(),
                'last_updated': mind_map.last_updated.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving mind map: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mindmaps')
def get_all_mind_maps():
    """Get all mind maps, optionally filtered by subject"""
    try:
        subject = request.args.get('subject')
        mind_maps = ai_tutor.get_all_mind_maps(subject)
        
        return jsonify({
            'success': True,
            'mind_maps': [{
                'id': m.id,
                'title': m.title,
                'subject': m.subject,
                'node_count': len(m.nodes),
                'created_at': m.created_at.isoformat(),
                'last_updated': m.last_updated.isoformat()
            } for m in mind_maps],
            'total_count': len(mind_maps)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving mind maps: {e}")
        return jsonify({'error': str(e)}), 500

# Statistics Endpoints
@app.route('/api/tutor/statistics')
def get_tutor_statistics():
    """Get AI Tutor usage statistics"""
    try:
        stats = ai_tutor.get_chat_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error retrieving tutor statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/overview/statistics')
def get_overview_statistics():
    """Get comprehensive overview statistics for all phases"""
    try:
        # Get statistics from all components
        quiz_stats = quiz_generator.get_quiz_statistics()
        flashcard_stats = quiz_generator.get_flashcard_statistics()
        tutor_stats = ai_tutor.get_chat_statistics()
        
        # Get OCR statistics
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM ocr_results')
        total_ocr_results = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM ai_generated_content')
        total_ai_content = cursor.fetchone()[0]
        
        conn.close()
        
        overview = {
            'phase': 5,
            'features': ['OCR', 'AI Content', 'Quiz System', 'Flashcards', 'AI Tutor', 'Mind Maps'],
            'ocr': {
                'total_results': total_ocr_results
            },
            'ai_content': {
                'total_generated': total_ai_content
            },
            'quiz_system': quiz_stats,
            'flashcards': flashcard_stats,
            'ai_tutor': tutor_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'overview': overview
        })
        
    except Exception as e:
        logger.error(f"Error retrieving overview statistics: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting AI Study Helper - Phase 5")
    print("📚 Features: OCR + AI Content + Quiz + Flashcards + AI Tutor + Mind Maps")
    print("🌐 Server will be available at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
