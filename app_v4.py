"""
AI Study Helper - Phase 4 Flask Application
Integrates OCR, AI Content Generation, and Quiz/Flashcard System
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
from ai_content_generator import AIContentGenerator
from quiz_flashcard_generator import QuizFlashcardGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_study_helper_phase4_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
ocr_pipeline = OCRPipeline()
ai_generator = AIContentGenerator(use_gpu=False)
quiz_generator = QuizFlashcardGenerator()

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ocr_result_id) REFERENCES ocr_results (id)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized with all phases")

def store_ocr_result(result: Dict[str, Any]):
    """Store OCR result in database"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ocr_results (filename, extracted_text, processing_time, file_size)
        VALUES (?, ?, ?, ?)
    ''', (result['filename'], result['extracted_text'], result['processing_time'], result['file_size']))
    
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return result_id

def store_ai_content(ocr_result_id: int, content: Dict[str, Any]):
    """Store AI generated content in database"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Store summary
    if 'summary' in content:
        cursor.execute('''
            INSERT INTO ai_generated_content 
            (ocr_result_id, content_type, generated_content, model_used, processing_time, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ocr_result_id, 'summary', content['summary']['text'], 'BART', 
              content['summary'].get('processing_time', 0), content['summary']['confidence']))
    
    # Store explanation
    if 'explanation' in content:
        cursor.execute('''
            INSERT INTO ai_generated_content 
            (ocr_result_id, content_type, generated_content, model_used, processing_time, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ocr_result_id, 'explanation', content['explanation']['text'], 'T5', 
              content['explanation'].get('processing_time', 0), content['explanation']['confidence']))
    
    # Store keywords
    if 'keywords' in content:
        cursor.execute('''
            INSERT INTO ai_generated_content 
            (ocr_result_id, content_type, generated_content, model_used, processing_time, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ocr_result_id, 'keywords', json.dumps(content['keywords']['text']), 'DistilBERT', 
              content['keywords'].get('processing_time', 0), content['keywords']['confidence']))
    
    conn.commit()
    conn.close()

# Routes

@app.route('/')
def index():
    """Main page - Phase 4 with Quiz & Flashcard system"""
    return render_template('index_v4.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'phase': 4,
        'features': ['OCR', 'AI Content Generation', 'Quiz System', 'Flashcard System'],
        'timestamp': datetime.now().isoformat()
    })

# Phase 1: OCR endpoints
@app.route('/api/ocr/upload', methods=['POST'])
def upload_and_process():
    """Upload and process image with OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)

        # Process with OCR
        start_time = datetime.now()
        result = ocr_pipeline.extract_text(filepath, preprocess=True)
        processing_time = (datetime.now() - start_time).total_seconds()

        result['filename'] = safe_filename
        result['processing_time'] = processing_time
        result['file_size'] = os.path.getsize(filepath)

        if result['success']:
            # Store OCR result
            ocr_result_id = store_ocr_result(result)
            
            # Generate AI content
            try:
                ai_content = ai_generator.generate_content(
                    result['extracted_text'],
                    content_types=['summary', 'explanation', 'keywords']
                )
                if ai_content['success']:
                    store_ai_content(ocr_result_id, ai_content['content'])
                    result['ai_content'] = ai_content['content']
            except Exception as e:
                logger.warning(f"AI content generation failed: {e}")
                result['ai_content'] = None
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(result)
        else:
            os.remove(filepath)
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in upload and processing: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'details': str(e)
        }), 500

@app.route('/api/ocr/info')
def ocr_info():
    """Get OCR system information"""
    try:
        info = ocr_pipeline.get_system_info()
        return jsonify({'success': True, 'ocr_info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ocr/results')
def get_ocr_results():
    """Get OCR processing history"""
    try:
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ocr_results ORDER BY created_at DESC LIMIT 50
        ''')
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            results.append({
                'id': row[0],
                'filename': row[1],
                'extracted_text': row[2],
                'processing_time': row[3],
                'file_size': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Phase 2: AI Content Generation endpoints
@app.route('/api/ai/generate', methods=['POST'])
def generate_ai_content():
    """Generate AI content from text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        content_types = data.get('content_types', ['summary', 'explanation', 'keywords'])
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        # Generate content
        result = ai_generator.generate_content(text, content_types)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating AI content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'AI generation failed',
            'details': str(e)
        }), 500

@app.route('/api/ai/models')
def get_ai_models():
    """Get AI model status"""
    try:
        models = ai_generator.get_model_info()
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Phase 3: Quiz & Flashcard endpoints
@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions from content"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        question_count = data.get('question_count', 5)
        question_types = data.get('question_types', ['multiple_choice', 'short_answer', 'true_false'])
        
        if not content:
            return jsonify({'success': False, 'error': 'No content provided'}), 400
        
        # Generate quiz questions
        questions = quiz_generator.generate_quiz_from_content(
            content, subject, question_types, difficulty, question_count
        )
        
        # Convert to serializable format
        quiz_data = []
        for q in questions:
            quiz_data.append({
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'correct_answer': q.correct_answer,
                'options': q.options,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'subject': q.subject,
                'tags': q.tags
            })
        
        return jsonify({
            'success': True,
            'quiz': quiz_data,
            'total_questions': len(quiz_data)
        })
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Quiz generation failed',
            'details': str(e)
        }), 500

@app.route('/api/flashcards/generate', methods=['POST'])
def generate_flashcards():
    """Generate flashcards from content"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        card_count = data.get('card_count', 5)
        
        if not content:
            return jsonify({'success': False, 'error': 'No content provided'}), 400
        
        # Generate flashcards
        flashcards = quiz_generator.generate_flashcards_from_content(
            content, subject, difficulty, card_count
        )
        
        # Convert to serializable format
        flashcard_data = []
        for f in flashcards:
            flashcard_data.append({
                'id': f.id,
                'front_content': f.front_content,
                'back_content': f.back_content,
                'subject': f.subject,
                'difficulty': f.difficulty,
                'tags': f.tags
            })
        
        return jsonify({
            'success': True,
            'flashcards': flashcard_data,
            'total_cards': len(flashcard_data)
        })
        
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Flashcard generation failed',
            'details': str(e)
        }), 500

@app.route('/api/quiz/questions')
def get_quiz_questions():
    """Get quiz questions with filters"""
    try:
        subject = request.args.get('subject')
        difficulty = request.args.get('difficulty')
        question_type = request.args.get('question_type')
        limit = int(request.args.get('limit', 10))
        
        questions = quiz_generator.get_quiz_questions(
            subject, difficulty, question_type, limit
        )
        
        # Convert to serializable format
        quiz_data = []
        for q in questions:
            quiz_data.append({
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'correct_answer': q.correct_answer,
                'options': q.options,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'subject': q.subject,
                'tags': q.tags
            })
        
        return jsonify({
            'success': True,
            'questions': quiz_data,
            'total': len(quiz_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting quiz questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get quiz questions',
            'details': str(e)
        }), 500

@app.route('/api/flashcards/review')
def get_flashcards_for_review():
    """Get flashcards due for review"""
    try:
        subject = request.args.get('subject')
        limit = int(request.args.get('limit', 20))
        
        flashcards = quiz_generator.get_flashcards_for_review(subject, limit)
        
        # Convert to serializable format
        flashcard_data = []
        for f in flashcards:
            flashcard_data.append({
                'id': f.id,
                'front_content': f.front_content,
                'back_content': f.back_content,
                'subject': f.subject,
                'difficulty': f.difficulty,
                'tags': f.tags,
                'review_count': f.review_count,
                'next_review': f.next_review.isoformat()
            })
        
        return jsonify({
            'success': True,
            'flashcards': flashcard_data,
            'total': len(flashcard_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting flashcards: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get flashcards',
            'details': str(e)
        }), 500

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz results and record session"""
    try:
        data = request.get_json()
        session_name = data.get('session_name', 'Quiz Session')
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        duration_minutes = data.get('duration_minutes')
        
        # Record quiz result
        quiz_generator.record_quiz_result(
            session_name, subject, difficulty, score, total_questions, duration_minutes
        )
        
        return jsonify({
            'success': True,
            'message': 'Quiz results recorded successfully',
            'score': score,
            'total': total_questions,
            'percentage': round((score / total_questions) * 100, 2) if total_questions > 0 else 0
        })
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to record quiz results',
            'details': str(e)
        }), 500

@app.route('/api/flashcards/review', methods=['POST'])
def record_flashcard_review():
    """Record flashcard review with spaced repetition"""
    try:
        data = request.get_json()
        flashcard_id = data.get('flashcard_id')
        quality = data.get('quality')  # 0-5 scale
        
        if flashcard_id is None or quality is None:
            return jsonify({'success': False, 'error': 'Missing flashcard_id or quality'}), 400
        
        if not 0 <= quality <= 5:
            return jsonify({'success': False, 'error': 'Quality must be between 0 and 5'}), 400
        
        # Record review
        quiz_generator.record_flashcard_review(flashcard_id, quality)
        
        return jsonify({
            'success': True,
            'message': 'Flashcard review recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error recording flashcard review: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to record flashcard review',
            'details': str(e)
        }), 500

@app.route('/api/quiz/statistics')
def get_quiz_statistics():
    """Get quiz performance statistics"""
    try:
        subject = request.args.get('subject')
        stats = quiz_generator.get_quiz_statistics(subject)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting quiz statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get quiz statistics',
            'details': str(e)
        }), 500

@app.route('/api/flashcards/statistics')
def get_flashcard_statistics():
    """Get flashcard performance statistics"""
    try:
        subject = request.args.get('subject')
        stats = quiz_generator.get_flashcard_statistics(subject)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting flashcard statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get flashcard statistics',
            'details': str(e)
        }), 500

# Study sessions endpoint (Phase 2)
@app.route('/api/study-sessions', methods=['GET', 'POST'])
def study_sessions():
    """Handle study sessions"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            session_name = data.get('session_name')
            duration_minutes = data.get('duration_minutes', 30)
            notes = data.get('notes', '')
            content_summary = data.get('content_summary', '')
            
            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400
            
            conn = sqlite3.connect('study_helper.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO study_sessions (session_name, content_summary, duration_minutes, notes)
                VALUES (?, ?, ?, ?)
            ''', (session_name, content_summary, duration_minutes, notes))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Study session created successfully'
            })
            
        except Exception as e:
            logger.error(f"Error creating study session: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to create study session',
                'details': str(e)
            }), 500
    
    else:  # GET request
        try:
            conn = sqlite3.connect('study_helper.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM study_sessions ORDER BY created_at DESC LIMIT 20
            ''')
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                sessions.append({
                    'id': row[0],
                    'session_name': row[1],
                    'content_summary': row[2],
                    'duration_minutes': row[3],
                    'notes': row[4],
                    'created_at': row[5]
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

if __name__ == '__main__':
    init_db()
    logger.info("Starting AI Study Helper Phase 4...")
    app.run(debug=True, host='0.0.0.0', port=5000)
