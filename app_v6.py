from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
from datetime import datetime
import json
import uuid

# Import all previous phase modules
from ocr_pipeline import OCRPipeline
from ai_content_generator import AIContentGenerator
from quiz_flashcard_generator import QuizFlashcardGenerator
from ai_tutor import AITutor

# Import Phase 5 modules
from gamification_system import GamificationSystem
from pwa_offline_support import PWAOfflineSupport
from multilingual_support import MultilingualSupport

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize all systems
ocr_pipeline = OCRPipeline()
ai_generator = AIContentGenerator()
quiz_generator = QuizFlashcardGenerator()
ai_tutor = AITutor()
gamification = GamificationSystem()
pwa_support = PWAOfflineSupport()
multilingual = MultilingualSupport()

def init_db():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Create basic tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            content TEXT,
            session_type TEXT,
            duration_minutes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Main dashboard with gamification features"""
    # Get current user (simplified - in real app would use proper auth)
    current_user = session.get('username', 'demo_user')
    
    # Get user progress and gamification data
    user_progress = gamification.get_user_progress(current_user)
    leaderboard = gamification.get_leaderboard(5)
    recent_activity = gamification.get_recent_activity(current_user, 5)
    
    # Get offline cache stats
    cache_stats = pwa_support.get_cache_stats()
    
    # Get language stats
    language_stats = multilingual.get_language_stats()
    
    return render_template('index_v6.html', 
                         user_progress=user_progress,
                         leaderboard=leaderboard,
                         recent_activity=recent_activity,
                         cache_stats=cache_stats,
                         language_stats=language_stats)

@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    """OCR functionality with gamification rewards"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file:
            # Process OCR
            try:
                # Save file temporarily
                filename = f"upload_{uuid.uuid4().hex}.jpg"
                filepath = os.path.join('uploads', filename)
                os.makedirs('uploads', exist_ok=True)
                file.save(filepath)
                
                # Extract text using OCR
                extracted_text = ocr_pipeline.extract_text(filepath)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                if extracted_text:
                    # Award XP for content processing
                    current_user = session.get('username', 'demo_user')
                    xp_result = gamification.award_xp(current_user, 50, "content", 5)
                    
                    # Cache content for offline access
                    content_hash = pwa_support.cache_content(
                        extracted_text, 
                        "ocr_text", 
                        {"filename": file.filename, "timestamp": datetime.now().isoformat()}
                    )
                    
                    # Create multilingual content entry
                    detected_language = multilingual.get_primary_language(extracted_text)
                    content_id = f"ocr_{uuid.uuid4().hex}"
                    multilingual.create_multilingual_content(
                        content_id, "ocr", extracted_text, detected_language
                    )
                    
                    return render_template('ocr_result.html', 
                                        text=extracted_text,
                                        xp_result=xp_result,
                                        content_hash=content_hash,
                                        detected_language=detected_language)
                else:
                    flash('No text could be extracted from the image')
                    return redirect(request.url)
                    
            except Exception as e:
                flash(f'Error processing image: {str(e)}')
                return redirect(request.url)
    
    return render_template('ocr.html')

@app.route('/ai_generate', methods=['POST'])
def ai_generate():
    """AI content generation with gamification"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate AI content
        summary = ai_generator.generate_summary(text)
        explanation = ai_generator.generate_explanation(text)
        keywords = ai_generator.extract_keywords(text)
        
        # Award XP for AI usage
        current_user = session.get('username', 'demo_user')
        xp_result = gamification.award_xp(current_user, 75, "ai_content", 10)
        
        # Cache AI-generated content
        ai_content = {
            'summary': summary,
            'explanation': explanation,
            'keywords': keywords
        }
        content_hash = pwa_support.cache_content(
            json.dumps(ai_content), 
            "ai_generated", 
            {"source_text": text[:100], "timestamp": datetime.now().isoformat()}
        )
        
        return jsonify({
            'summary': summary,
            'explanation': explanation,
            'keywords': keywords,
            'xp_result': xp_result,
            'content_hash': content_hash
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Quiz system with gamification"""
    if request.method == 'POST':
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        try:
            # Generate quiz questions
            quiz_questions = quiz_generator.generate_quiz_from_content(content, 5)
            
            # Award XP for quiz generation
            current_user = session.get('username', 'demo_user')
            xp_result = gamification.award_xp(current_user, 25, "quiz_generation", 5)
            
            return jsonify({
                'questions': quiz_questions,
                'xp_result': xp_result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and award XP"""
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        quiz_data = data.get('quiz_data', {})
        
        # Calculate score
        correct_answers = 0
        total_questions = len(answers)
        
        for question_id, user_answer in answers.items():
            # This is simplified - in real app would check against correct answers
            if user_answer:  # Assume any answer is correct for demo
                correct_answers += 1
        
        score_percentage = (correct_answers / total_questions) * 100
        
        # Award XP based on performance
        current_user = session.get('username', 'demo_user')
        base_xp = 50
        bonus_xp = int(score_percentage / 10) * 10  # Bonus for high scores
        total_xp = base_xp + bonus_xp
        
        xp_result = gamification.award_xp(current_user, total_xp, "quiz", 15)
        
        # Store offline quiz result
        quiz_id = f"quiz_{uuid.uuid4().hex}"
        pwa_support.store_offline_quiz_result(
            user_id=1,  # Simplified user ID
            quiz_data=quiz_data,
            results_data={
                'score': score_percentage,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'answers': answers
            }
        )
        
        return jsonify({
            'score': score_percentage,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'xp_result': xp_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flashcards')
def flashcards():
    """Flashcard system with gamification"""
    try:
        # Get flashcards for current user
        current_user = session.get('username', 'demo_user')
        
        # Generate sample flashcards (in real app would get from database)
        sample_flashcards = [
            {'question': 'What is the capital of France?', 'answer': 'Paris'},
            {'question': 'What is 2 + 2?', 'answer': '4'},
            {'question': 'What is the largest planet?', 'answer': 'Jupiter'}
        ]
        
        return render_template('flashcards.html', flashcards=sample_flashcards)
        
    except Exception as e:
        flash(f'Error loading flashcards: {str(e)}')
        return redirect(url_for('index'))

@app.route('/review_flashcard', methods=['POST'])
def review_flashcard():
    """Review flashcard and award XP"""
    try:
        data = request.get_json()
        flashcard_id = data.get('flashcard_id')
        difficulty = data.get('difficulty', 1)  # 1-5 scale
        
        # Award XP based on difficulty
        current_user = session.get('username', 'demo_user')
        xp_amount = difficulty * 10  # More XP for harder cards
        xp_result = gamification.award_xp(current_user, xp_amount, "flashcard", 5)
        
        # Store offline progress
        pwa_support.store_offline_flashcard_progress(
            user_id=1,  # Simplified user ID
            progress_data={
                'flashcard_id': flashcard_id,
                'difficulty': difficulty,
                'reviewed_at': datetime.now().isoformat()
            }
        )
        
        return jsonify({
            'success': True,
            'xp_result': xp_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai_tutor')
def ai_tutor():
    """AI Tutor interface"""
    return render_template('ai_tutor.html')

@app.route('/chat', methods=['POST'])
def chat():
    """AI Tutor chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get AI response
        response = ai_tutor.get_chat_response(session_id, message)
        
        # Award XP for using AI tutor
        current_user = session.get('username', 'demo_user')
        xp_result = gamification.award_xp(current_user, 30, "ai_tutor", 8)
        
        return jsonify({
            'response': response,
            'xp_result': xp_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mind_map')
def mind_map():
    """Mind map generation"""
    return render_template('mind_map.html')

@app.route('/generate_mind_map', methods=['POST'])
def generate_mind_map():
    """Generate mind map from content"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Generate mind map
        mind_map_data = ai_tutor.create_mind_map(content)
        
        # Award XP for mind map creation
        current_user = session.get('username', 'demo_user')
        xp_result = gamification.award_xp(current_user, 40, "mind_map", 12)
        
        return jsonify({
            'mind_map': mind_map_data,
            'xp_result': xp_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gamification')
def gamification_dashboard():
    """Gamification dashboard"""
    current_user = session.get('username', 'demo_user')
    
    user_progress = gamification.get_user_progress(current_user)
    leaderboard = gamification.get_leaderboard(20)
    recent_activity = gamification.get_recent_activity(current_user, 20)
    
    return render_template('gamification.html',
                         user_progress=user_progress,
                         leaderboard=leaderboard,
                         recent_activity=recent_activity)

@app.route('/offline')
def offline_dashboard():
    """Offline support dashboard"""
    current_user = session.get('username', 'demo_user')
    
    cache_stats = pwa_support.get_cache_stats()
    offline_sessions = pwa_support.get_offline_study_sessions(1)  # Simplified user ID
    offline_quizzes = pwa_support.get_offline_quiz_results(1)
    offline_flashcards = pwa_support.get_offline_flashcard_progress(1)
    
    return render_template('offline.html',
                         cache_stats=cache_stats,
                         offline_sessions=offline_sessions,
                         offline_quizzes=offline_quizzes,
                         offline_flashcards=offline_flashcards)

@app.route('/multilingual')
def multilingual_dashboard():
    """Multilingual support dashboard"""
    supported_languages = multilingual.get_supported_languages()
    language_stats = multilingual.get_language_stats()
    
    return render_template('multilingual.html',
                         supported_languages=supported_languages,
                         language_stats=language_stats)

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translate text endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Translate text
        translation_result = multilingual.translate_text(text, target_language)
        
        return jsonify(translation_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_progress')
def api_user_progress():
    """Get user progress API endpoint"""
    current_user = session.get('username', 'demo_user')
    user_progress = gamification.get_user_progress(current_user)
    return jsonify(user_progress)

@app.route('/api/leaderboard')
def api_leaderboard():
    """Get leaderboard API endpoint"""
    limit = request.args.get('limit', 10, type=int)
    leaderboard = gamification.get_leaderboard(limit)
    return jsonify(leaderboard)

@app.route('/api/recent_activity')
def api_recent_activity():
    """Get recent activity API endpoint"""
    current_user = session.get('username', 'demo_user')
    limit = request.args.get('limit', 10, type=int)
    recent_activity = gamification.get_recent_activity(current_user, limit)
    return jsonify(recent_activity)

@app.route('/api/cache_stats')
def api_cache_stats():
    """Get cache statistics API endpoint"""
    cache_stats = pwa_support.get_cache_stats()
    return jsonify(cache_stats)

@app.route('/api/language_stats')
def api_language_stats():
    """Get language statistics API endpoint"""
    language_stats = multilingual.get_language_stats()
    return jsonify(language_stats)

@app.route('/api/supported_languages')
def api_supported_languages():
    """Get supported languages API endpoint"""
    languages = multilingual.get_supported_languages()
    return jsonify(languages)

@app.route('/api/detect_language', methods=['POST'])
def api_detect_language():
    """Language detection API endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        detected_languages = multilingual.detect_language(text)
        primary_language = multilingual.get_primary_language(text)
        
        return jsonify({
            'detected_languages': detected_languages,
            'primary_language': primary_language
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offline_content', methods=['POST'])
def api_offline_content():
    """Store content for offline access"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        content_type = data.get('content_type', 'text')
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        content_hash = pwa_support.cache_content(content, content_type, metadata)
        
        if content_hash:
            return jsonify({
                'success': True,
                'content_hash': content_hash
            })
        else:
            return jsonify({'error': 'Failed to cache content'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offline_content/<content_hash>')
def api_get_offline_content(content_hash):
    """Get cached content by hash"""
    try:
        content = pwa_support.get_cached_content(content_hash)
        
        if content:
            return jsonify(content)
        else:
            return jsonify({'error': 'Content not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_offline', methods=['POST'])
def api_search_offline():
    """Search offline cached content"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        content_type = data.get('content_type')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = pwa_support.search_cached_content(query, content_type)
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_offline_data')
def api_export_offline_data():
    """Export offline data for user"""
    try:
        current_user = session.get('username', 'demo_user')
        export_data = pwa_support.export_offline_data(1)  # Simplified user ID
        
        return jsonify(export_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import_offline_data', methods=['POST'])
def api_import_offline_data():
    """Import offline data for user"""
    try:
        data = request.get_json()
        current_user = session.get('username', 'demo_user')
        
        success = pwa_support.import_offline_data(1, data)  # Simplified user ID
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to import data'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_preferences', methods=['GET', 'POST'])
def api_user_preferences():
    """User preferences API endpoint"""
    current_user = session.get('username', 'demo_user')
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            key = data.get('key')
            value = data.get('value')
            
            if not key:
                return jsonify({'error': 'No key provided'}), 400
            
            success = pwa_support.set_user_preference(1, key, value)  # Simplified user ID
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to set preference'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    else:
        # GET request
        try:
            key = request.args.get('key')
            
            if key:
                value = pwa_support.get_user_preference(1, key)  # Simplified user ID
                return jsonify({key: value})
            else:
                # Get all preferences
                preferences = {}
                common_keys = ['theme', 'language', 'notifications', 'auto_save']
                for pref_key in common_keys:
                    value = pwa_support.get_user_preference(1, pref_key)
                    if value is not None:
                        preferences[pref_key] = value
                
                return jsonify(preferences)
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/sync_queue')
def api_sync_queue():
    """Get sync queue API endpoint"""
    try:
        limit = request.args.get('limit', 50, type=int)
        sync_queue = pwa_support.get_sync_queue(limit)
        return jsonify({'sync_queue': sync_queue})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mark_sync', methods=['POST'])
def api_mark_sync():
    """Mark sync attempt as completed"""
    try:
        data = request.get_json()
        sync_id = data.get('sync_id')
        success = data.get('success', False)
        
        if sync_id is None:
            return jsonify({'error': 'No sync ID provided'}), 400
        
        success_result = pwa_support.mark_sync_attempt(sync_id, success)
        
        if success_result:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to mark sync attempt'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup_cache', methods=['POST'])
def api_cleanup_cache():
    """Clean up old cached content"""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 30)
        
        deleted_count = pwa_support.cleanup_old_cache(days_old)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multilingual_content', methods=['POST'])
def api_multilingual_content():
    """Create multilingual content"""
    try:
        data = request.get_json()
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        original_text = data.get('original_text')
        original_language = data.get('original_language')
        translations = data.get('translations', {})
        
        if not all([content_id, content_type, original_text, original_language]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = multilingual.create_multilingual_content(
            content_id, content_type, original_text, original_language, translations
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to create multilingual content'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multilingual_content/<content_id>')
def api_get_multilingual_content(content_id):
    """Get multilingual content by ID"""
    try:
        target_language = request.args.get('language')
        content = multilingual.get_multilingual_content(content_id, target_language)
        
        if content:
            return jsonify(content)
        else:
            return jsonify({'error': 'Content not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_translation', methods=['POST'])
def api_add_translation():
    """Add translation to existing content"""
    try:
        data = request.get_json()
        content_id = data.get('content_id')
        target_language = data.get('target_language')
        translated_text = data.get('translated_text')
        
        if not all([content_id, target_language, translated_text]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = multilingual.add_translation(content_id, target_language, translated_text)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to add translation'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_language_preferences', methods=['GET', 'POST'])
def api_user_language_preferences():
    """User language preferences API endpoint"""
    current_user = session.get('username', 'demo_user')
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            primary_language = data.get('primary_language')
            secondary_languages = data.get('secondary_languages', [])
            interface_language = data.get('interface_language')
            content_language = data.get('content_language')
            auto_translate = data.get('auto_translate', True)
            
            if not primary_language:
                return jsonify({'error': 'Primary language is required'}), 400
            
            success = multilingual.set_user_language_preferences(
                1,  # Simplified user ID
                primary_language,
                secondary_languages,
                interface_language,
                content_language,
                auto_translate
            )
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to set language preferences'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    else:
        # GET request
        try:
            preferences = multilingual.get_user_language_preferences(1)  # Simplified user ID
            return jsonify(preferences)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)



