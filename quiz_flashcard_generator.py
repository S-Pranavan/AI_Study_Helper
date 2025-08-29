"""
Quiz & Flashcard Generator for AI Study Helper - Phase 3
Generates quizzes and flashcards from AI-generated content
"""

import re
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QuizQuestion:
    """Represents a single quiz question"""
    id: Optional[int]
    question_text: str
    question_type: str  # 'multiple_choice', 'short_answer', 'true_false'
    correct_answer: str
    options: List[str]  # For multiple choice
    explanation: str
    difficulty: str  # 'easy', 'medium', 'hard'
    subject: str
    tags: List[str]
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int

@dataclass
class Flashcard:
    """Represents a single flashcard"""
    id: Optional[int]
    front_content: str
    back_content: str
    subject: str
    difficulty: str
    tags: List[str]
    created_at: datetime
    last_reviewed: Optional[datetime]
    next_review: datetime
    review_count: int
    ease_factor: float  # Spaced repetition ease factor
    interval: int  # Days until next review

class QuizFlashcardGenerator:
    """Generates quizzes and flashcards from AI-generated content"""
    
    def __init__(self, db_path: str = "study_helper.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables for Phase 3"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Quiz questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                options TEXT,  -- JSON string for multiple choice
                explanation TEXT,
                difficulty TEXT NOT NULL,
                subject TEXT NOT NULL,
                tags TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Flashcards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                front_content TEXT NOT NULL,
                back_content TEXT NOT NULL,
                subject TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                tags TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                review_count INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 1
            )
        ''')
        
        # Quiz sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_count INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                duration_minutes INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Flashcard review sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcard_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flashcard_id INTEGER NOT NULL,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality INTEGER NOT NULL,  -- 0-5 scale for spaced repetition
                ease_factor REAL,
                interval INTEGER,
                next_review TIMESTAMP,
                FOREIGN KEY (flashcard_id) REFERENCES flashcards (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Phase 3 database tables initialized successfully")
    
    def generate_quiz_from_content(self, content: str, subject: str, 
                                 question_types: List[str] = None, 
                                 difficulty: str = "medium",
                                 question_count: int = 5) -> List[QuizQuestion]:
        """
        Generate quiz questions from AI-generated content
        
        Args:
            content: The text content to generate questions from
            subject: Subject area for the questions
            question_types: Types of questions to generate
            difficulty: Difficulty level
            question_count: Number of questions to generate
            
        Returns:
            List of generated quiz questions
        """
        if question_types is None:
            question_types = ['multiple_choice', 'short_answer', 'true_false']
        
        questions = []
        
        # Split content into sentences for question generation
        sentences = self._split_into_sentences(content)
        
        # Generate questions based on content
        for i, sentence in enumerate(sentences[:question_count]):
            if not sentence.strip():
                continue
                
            # Determine question type for this sentence
            question_type = random.choice(question_types)
            
            try:
                if question_type == 'multiple_choice':
                    question = self._generate_multiple_choice(sentence, subject, difficulty)
                elif question_type == 'short_answer':
                    question = self._generate_short_answer(sentence, subject, difficulty)
                elif question_type == 'true_false':
                    question = self._generate_true_false(sentence, subject, difficulty)
                else:
                    continue
                
                if question:
                    questions.append(question)
                    
            except Exception as e:
                logger.error(f"Error generating {question_type} question: {e}")
                continue
        
        # Save questions to database
        self._save_questions(questions)
        
        return questions
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for question generation"""
        # Simple sentence splitting - can be improved with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    def _generate_multiple_choice(self, sentence: str, subject: str, difficulty: str) -> QuizQuestion:
        """Generate a multiple choice question from a sentence"""
        # Extract key concepts from the sentence
        key_concepts = self._extract_key_concepts(sentence)
        
        if not key_concepts:
            return None
        
        # Create question by removing key concept
        main_concept = random.choice(key_concepts)
        question_text = sentence.replace(main_concept, "_____")
        
        # Generate distractors (wrong answers)
        distractors = self._generate_distractors(main_concept, subject, difficulty)
        
        # Ensure we have enough options
        while len(distractors) < 3:
            distractors.append(f"Option {len(distractors) + 1}")
        
        # Create options list
        options = [main_concept] + distractors[:3]
        random.shuffle(options)
        
        # Find correct answer index
        correct_answer_index = options.index(main_concept)
        
        # Create explanation
        explanation = f"The correct answer is '{main_concept}' because it fits the context of the sentence."
        
        # Generate tags
        tags = [subject, difficulty, "multiple_choice"] + key_concepts[:3]
        
        return QuizQuestion(
            id=None,
            question_text=question_text,
            question_type="multiple_choice",
            correct_answer=main_concept,
            options=options,
            explanation=explanation,
            difficulty=difficulty,
            subject=subject,
            tags=tags,
            created_at=datetime.now(),
            last_used=None,
            usage_count=0
        )
    
    def _generate_short_answer(self, sentence: str, subject: str, difficulty: str) -> QuizQuestion:
        """Generate a short answer question from a sentence"""
        # Extract key concepts
        key_concepts = self._extract_key_concepts(sentence)
        
        if not key_concepts:
            return None
        
        # Create question by asking about a key concept
        main_concept = random.choice(key_concepts)
        question_text = f"What is the main concept described in: '{sentence}'?"
        
        # Create explanation
        explanation = f"The main concept is '{main_concept}' as described in the given text."
        
        # Generate tags
        tags = [subject, difficulty, "short_answer"] + key_concepts[:3]
        
        return QuizQuestion(
            id=None,
            question_text=question_text,
            question_type="short_answer",
            correct_answer=main_concept,
            options=[],
            explanation=explanation,
            difficulty=difficulty,
            subject=subject,
            tags=tags,
            created_at=datetime.now(),
            last_used=None,
            usage_count=0
        )
    
    def _generate_true_false(self, sentence: str, subject: str, difficulty: str) -> QuizQuestion:
        """Generate a true/false question from a sentence"""
        # Create a statement based on the sentence
        statement = sentence
        
        # Randomly decide if it's true or false
        is_true = random.choice([True, False])
        
        if is_true:
            correct_answer = "True"
            explanation = "This statement is correct based on the given information."
        else:
            # Create a false statement by modifying the original
            statement = self._create_false_statement(sentence)
            correct_answer = "False"
            explanation = "This statement is incorrect. The original text states otherwise."
        
        # Generate tags
        tags = [subject, difficulty, "true_false"]
        
        return QuizQuestion(
            id=None,
            question_text=f"True or False: {statement}",
            question_type="true_false",
            correct_answer=correct_answer,
            options=["True", "False"],
            explanation=explanation,
            difficulty=difficulty,
            subject=subject,
            tags=tags,
            created_at=datetime.now(),
            last_used=None,
            usage_count=0
        )
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified version)"""
        # Simple keyword extraction - can be improved with NLP
        words = re.findall(r'\b[A-Za-z]{3,}\b', text)
        
        # Filter out common words
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        key_concepts = [word for word in words if word.lower() not in common_words]
        
        # Return unique concepts, limited to reasonable number
        return list(set(key_concepts))[:5]
    
    def _generate_distractors(self, correct_answer: str, subject: str, difficulty: str) -> List[str]:
        """Generate distractors (wrong answers) for multiple choice questions"""
        # This is a simplified version - in practice, you'd use more sophisticated methods
        
        # Generate some plausible distractors
        distractors = []
        
        # Add some variations
        if len(correct_answer) > 3:
            # Remove last letter
            distractors.append(correct_answer[:-1])
            # Change last letter
            distractors.append(correct_answer[:-1] + 'x')
        
        # Add some generic distractors
        generic_distractors = ["None of the above", "All of the above", "Cannot be determined"]
        distractors.extend(generic_distractors)
        
        # Shuffle and return
        random.shuffle(distractors)
        return distractors[:3]
    
    def _create_false_statement(self, original_sentence: str) -> str:
        """Create a false statement based on the original sentence"""
        # Simple negation strategy
        if "is" in original_sentence.lower():
            return original_sentence.replace("is", "is not")
        elif "are" in original_sentence.lower():
            return original_sentence.replace("are", "are not")
        elif "can" in original_sentence.lower():
            return original_sentence.replace("can", "cannot")
        else:
            # Add "not" to make it false
            return original_sentence.replace(".", " not.")
    
    def generate_flashcards_from_content(self, content: str, subject: str, 
                                       difficulty: str = "medium",
                                       card_count: int = 5) -> List[Flashcard]:
        """
        Generate flashcards from AI-generated content
        
        Args:
            content: The text content to generate flashcards from
            subject: Subject area for the flashcards
            difficulty: Difficulty level
            card_count: Number of flashcards to generate
            
        Returns:
            List of generated flashcards
        """
        flashcards = []
        
        # Split content into manageable chunks
        chunks = self._split_into_chunks(content, card_count)
        
        for chunk in chunks:
            try:
                flashcard = self._create_flashcard_from_chunk(chunk, subject, difficulty)
                if flashcard:
                    flashcards.append(flashcard)
            except Exception as e:
                logger.error(f"Error generating flashcard: {e}")
                continue
        
        # Save flashcards to database
        self._save_flashcards(flashcards)
        
        return flashcards
    
    def _split_into_chunks(self, text: str, chunk_count: int) -> List[str]:
        """Split text into chunks for flashcard generation"""
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= chunk_count:
            return sentences
        
        # Group sentences into chunks
        chunk_size = len(sentences) // chunk_count
        chunks = []
        
        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i + chunk_size]
            if chunk:
                chunks.append(" ".join(chunk))
            if len(chunks) >= chunk_count:
                break
        
        return chunks
    
    def _create_flashcard_from_chunk(self, chunk: str, subject: str, difficulty: str) -> Flashcard:
        """Create a flashcard from a text chunk"""
        # Extract key concepts for the front
        key_concepts = self._extract_key_concepts(chunk)
        
        if not key_concepts:
            return None
        
        # Front: Key concept or question
        front_content = f"What is the main concept in: '{chunk[:100]}...'?"
        
        # Back: The chunk content
        back_content = chunk
        
        # Generate tags
        tags = [subject, difficulty] + key_concepts[:3]
        
        # Calculate next review date (spaced repetition)
        next_review = datetime.now() + timedelta(days=1)
        
        return Flashcard(
            id=None,
            front_content=front_content,
            back_content=back_content,
            subject=subject,
            difficulty=difficulty,
            tags=tags,
            created_at=datetime.now(),
            last_reviewed=None,
            next_review=next_review,
            review_count=0,
            ease_factor=2.5,
            interval=1
        )
    
    def _save_questions(self, questions: List[QuizQuestion]):
        """Save quiz questions to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for question in questions:
            cursor.execute('''
                INSERT INTO quiz_questions 
                (question_text, question_type, correct_answer, options, explanation, 
                 difficulty, subject, tags, created_at, last_used, usage_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question.question_text,
                question.question_type,
                question.correct_answer,
                json.dumps(question.options) if question.options else None,
                question.explanation,
                question.difficulty,
                question.subject,
                json.dumps(question.tags),
                question.created_at.isoformat(),
                question.last_used.isoformat() if question.last_used else None,
                question.usage_count
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(questions)} quiz questions to database")
    
    def _save_flashcards(self, flashcards: List[Flashcard]):
        """Save flashcards to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for flashcard in flashcards:
            cursor.execute('''
                INSERT INTO flashcards 
                (front_content, back_content, subject, difficulty, tags, created_at, 
                 last_reviewed, next_review, review_count, ease_factor, interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flashcard.front_content,
                flashcard.back_content,
                flashcard.subject,
                flashcard.difficulty,
                json.dumps(flashcard.tags),
                flashcard.created_at.isoformat(),
                flashcard.last_reviewed.isoformat() if flashcard.last_reviewed else None,
                flashcard.next_review.isoformat(),
                flashcard.review_count,
                flashcard.ease_factor,
                flashcard.interval
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(flashcards)} flashcards to database")
    
    def get_quiz_questions(self, subject: str = None, difficulty: str = None, 
                          question_type: str = None, limit: int = 10) -> List[QuizQuestion]:
        """Retrieve quiz questions from database with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM quiz_questions WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        if question_type:
            query += " AND question_type = ?"
            params.append(question_type)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        questions = []
        for row in cursor.fetchall():
            question = self._row_to_question(row)
            if question:
                questions.append(question)
        
        conn.close()
        return questions
    
    def get_flashcards_for_review(self, subject: str = None, limit: int = 20) -> List[Flashcard]:
        """Get flashcards that are due for review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM flashcards WHERE next_review <= ?"
        params = [datetime.now().isoformat()]
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        
        query += " ORDER BY next_review ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        flashcards = []
        for row in rows:
            flashcard = self._row_to_flashcard(row)
            if flashcard:
                flashcards.append(flashcard)
        
        conn.close()
        return flashcards
    
    def _row_to_question(self, row) -> QuizQuestion:
        """Convert database row to QuizQuestion object"""
        try:
            return QuizQuestion(
                id=row[0],
                question_text=row[1],
                question_type=row[2],
                correct_answer=row[3],
                options=json.loads(row[4]) if row[4] else [],
                explanation=row[5],
                difficulty=row[6],
                subject=row[7],
                tags=json.loads(row[8]) if row[8] else [],
                created_at=datetime.fromisoformat(row[9]),
                last_used=datetime.fromisoformat(row[10]) if row[10] else None,
                usage_count=row[11]
            )
        except Exception as e:
            logger.error(f"Error converting row to question: {e}")
            return None
    
    def _row_to_flashcard(self, row) -> Flashcard:
        """Convert database row to Flashcard object"""
        try:
            return Flashcard(
                id=row[0],
                front_content=row[1],
                back_content=row[2],
                subject=row[3],
                difficulty=row[4],
                tags=json.loads(row[5]) if row[5] else [],
                created_at=datetime.fromisoformat(row[6]),
                last_reviewed=datetime.fromisoformat(row[7]) if row[7] else None,
                next_review=datetime.fromisoformat(row[8]),
                review_count=row[9],
                ease_factor=row[10],
                interval=row[11]
            )
        except Exception as e:
            logger.error(f"Error converting row to flashcard: {e}")
            return None
    
    def record_quiz_result(self, session_name: str, subject: str, difficulty: str,
                          score: int, total_questions: int, duration_minutes: int = None):
        """Record the results of a quiz session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quiz_sessions 
            (session_name, subject, difficulty, question_count, score, total_questions, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_name, subject, difficulty, total_questions, score, total_questions, duration_minutes))
        
        conn.commit()
        conn.close()
        logger.info(f"Recorded quiz session: {session_name} - Score: {score}/{total_questions}")
    
    def record_flashcard_review(self, flashcard_id: int, quality: int):
        """
        Record a flashcard review with spaced repetition algorithm
        
        Args:
            flashcard_id: ID of the reviewed flashcard
            quality: Quality of the review (0-5 scale)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current flashcard data
        cursor.execute('SELECT * FROM flashcards WHERE id = ?', (flashcard_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return
        
        # Calculate new interval and ease factor using spaced repetition
        current_ease_factor = row[10]
        current_interval = row[11]
        
        # SuperMemo 2 algorithm (simplified)
        if quality >= 3:  # Good response
            if current_interval == 1:
                new_interval = 6
            else:
                new_interval = int(current_interval * current_ease_factor)
            
            new_ease_factor = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:  # Poor response
            new_interval = 1
            new_ease_factor = max(1.3, current_ease_factor - 0.2)
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=new_interval)
        
        # Update flashcard
        cursor.execute('''
            UPDATE flashcards 
            SET last_reviewed = ?, next_review = ?, review_count = review_count + 1,
                ease_factor = ?, interval = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), next_review.isoformat(), new_ease_factor, new_interval, flashcard_id))
        
        # Record review session
        cursor.execute('''
            INSERT INTO flashcard_reviews 
            (flashcard_id, review_date, quality, ease_factor, interval, next_review)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (flashcard_id, datetime.now().isoformat(), quality, new_ease_factor, new_interval, next_review.isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Recorded flashcard review for ID {flashcard_id} with quality {quality}")
    
    def get_quiz_statistics(self, subject: str = None) -> Dict[str, Any]:
        """Get statistics about quiz performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM quiz_sessions"
        params = []
        
        if subject:
            query += " WHERE subject = ?"
            params.append(subject)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return {
                'total_sessions': 0,
                'average_score': 0,
                'total_questions': 0,
                'subjects': [],
                'difficulty_distribution': {}
            }
        
        total_sessions = len(rows)
        total_score = sum(row[5] for row in rows)
        total_questions = sum(row[6] for row in rows)
        average_score = total_score / total_questions if total_questions > 0 else 0
        
        # Get subjects
        subjects = list(set(row[2] for row in rows))
        
        # Get difficulty distribution
        difficulty_distribution = {}
        for row in rows:
            difficulty = row[3]
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'average_score': round(average_score * 100, 2),  # Convert to percentage
            'total_questions': total_questions,
            'subjects': subjects,
            'difficulty_distribution': difficulty_distribution
        }
    
    def get_flashcard_statistics(self, subject: str = None) -> Dict[str, Any]:
        """Get statistics about flashcard performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM flashcards"
        params = []
        
        if subject:
            query += " WHERE subject = ?"
            params.append(subject)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return {
                'total_cards': 0,
                'cards_due_review': 0,
                'average_ease_factor': 0,
                'subjects': [],
                'difficulty_distribution': {}
            }
        
        total_cards = len(rows)
        cards_due_review = len([row for row in rows if datetime.fromisoformat(row[8]) <= datetime.now()])
        average_ease_factor = sum(row[10] for row in rows) / total_cards
        
        # Get subjects
        subjects = list(set(row[3] for row in rows))
        
        # Get difficulty distribution
        difficulty_distribution = {}
        for row in rows:
            difficulty = row[4]
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        conn.close()
        
        return {
            'total_cards': total_cards,
            'cards_due_review': cards_due_review,
            'average_ease_factor': round(average_ease_factor, 2),
            'subjects': subjects,
            'difficulty_distribution': difficulty_distribution
        }
