import sqlite3
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

class MultilingualSupport:
    def __init__(self, db_path: str = "study_helper.db"):
        self.db_path = db_path
        self.init_multilingual_tables()
        self.initialize_languages()
        self.initialize_translations()
    
    def init_multilingual_tables(self):
        """Initialize multilingual-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Supported languages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supported_languages (
                id INTEGER PRIMARY KEY,
                language_code TEXT UNIQUE,
                language_name TEXT,
                native_name TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Language detection patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_patterns (
                id INTEGER PRIMARY KEY,
                language_code TEXT,
                pattern_type TEXT,
                pattern TEXT,
                confidence REAL,
                FOREIGN KEY (language_code) REFERENCES supported_languages (language_code)
            )
        ''')
        
        # Translation cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_cache (
                id INTEGER PRIMARY KEY,
                source_text_hash TEXT UNIQUE,
                source_text TEXT,
                source_language TEXT,
                target_language TEXT,
                translated_text TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Multilingual content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS multilingual_content (
                id INTEGER PRIMARY KEY,
                content_id TEXT UNIQUE,
                content_type TEXT,
                original_language TEXT,
                original_text TEXT,
                translations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User language preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_language_preferences (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                primary_language TEXT,
                secondary_languages TEXT,
                interface_language TEXT,
                content_language TEXT,
                auto_translate BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (primary_language) REFERENCES supported_languages (language_code)
            )
        ''')
        
        # Language learning progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_learning_progress (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                language_code TEXT,
                proficiency_level TEXT,
                words_learned INTEGER DEFAULT 0,
                study_time_minutes INTEGER DEFAULT 0,
                last_study_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (language_code) REFERENCES supported_languages (language_code)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_languages(self):
        """Initialize supported languages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if languages already exist
        cursor.execute("SELECT COUNT(*) FROM supported_languages")
        if cursor.fetchone()[0] == 0:
            # Insert default languages
            default_languages = [
                ("en", "English", "English", True),
                ("es", "Spanish", "Español", True),
                ("fr", "French", "Français", True),
                ("de", "German", "Deutsch", True),
                ("it", "Italian", "Italiano", True),
                ("pt", "Portuguese", "Português", True),
                ("ru", "Russian", "Русский", True),
                ("zh", "Chinese", "中文", True),
                ("ja", "Japanese", "日本語", True),
                ("ko", "Korean", "한국어", True),
                ("ar", "Arabic", "العربية", True),
                ("hi", "Hindi", "हिन्दी", True),
                ("nl", "Dutch", "Nederlands", True),
                ("sv", "Swedish", "Svenska", True),
                ("no", "Norwegian", "Norsk", True),
                ("da", "Danish", "Dansk", True),
                ("fi", "Finnish", "Suomi", True),
                ("pl", "Polish", "Polski", True),
                ("tr", "Turkish", "Türkçe", True),
                ("he", "Hebrew", "עברית", True)
            ]
            
            cursor.executemany('''
                INSERT INTO supported_languages (language_code, language_name, native_name, is_active)
                VALUES (?, ?, ?, ?)
            ''', default_languages)
        
        conn.commit()
        conn.close()
    
    def initialize_translations(self):
        """Initialize common translations and language patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if patterns already exist
        cursor.execute("SELECT COUNT(*) FROM language_patterns")
        if cursor.fetchone()[0] == 0:
            # Insert language detection patterns
            patterns = [
                # English patterns
                ("en", "common_words", "the|and|or|but|in|on|at|to|for|of|with|by", 0.9),
                ("en", "common_words", "is|are|was|were|be|been|have|has|had|do|does|did", 0.8),
                ("en", "common_words", "you|he|she|it|we|they|me|him|her|us|them", 0.7),
                
                # Spanish patterns
                ("es", "common_words", "el|la|los|las|de|que|y|en|un|es|se|no|te|le|lo", 0.9),
                ("es", "common_words", "es|son|era|eran|está|están|tiene|tienen", 0.8),
                ("es", "common_words", "yo|tú|él|ella|nosotros|vosotros|ellos|ellas", 0.7),
                
                # French patterns
                ("fr", "common_words", "le|la|les|de|du|des|et|ou|que|qui|dans|sur|avec", 0.9),
                ("fr", "common_words", "est|sont|était|étaient|a|ont|peut|peuvent", 0.8),
                ("fr", "common_words", "je|tu|il|elle|nous|vous|ils|elles", 0.7),
                
                # German patterns
                ("de", "common_words", "der|die|das|den|dem|des|und|oder|dass|was|wer|wo", 0.9),
                ("de", "common_words", "ist|sind|war|waren|hat|haben|kann|können", 0.8),
                ("de", "common_words", "ich|du|er|sie|es|wir|ihr|Sie", 0.7),
                
                # Chinese patterns
                ("zh", "characters", "的|是|在|有|和|了|不|我|你|他|她|它|我们|你们|他们", 0.9),
                ("zh", "characters", "这|那|什么|怎么|为什么|哪里|什么时候", 0.8),
                
                # Japanese patterns
                ("ja", "characters", "の|は|が|を|に|へ|で|と|や|も|から|まで", 0.9),
                ("ja", "characters", "です|ます|だ|である|いる|ある|する|なる", 0.8),
                ("ja", "characters", "私|あなた|彼|彼女|私たち|あなたたち|彼ら", 0.7),
                
                # Korean patterns
                ("ko", "characters", "은|는|이|가|을|를|의|에|에서|로|와|과", 0.9),
                ("ko", "characters", "이다|있다|없다|하다|되다|가다|오다", 0.8),
                ("ko", "characters", "나|너|그|그녀|우리|너희|그들", 0.7),
                
                # Arabic patterns
                ("ar", "characters", "ال|في|من|إلى|على|عن|مع|ب|ل|ك|ه|هي|هما|هم|هن", 0.9),
                ("ar", "characters", "كان|يكون|كانت|تكون|هناك|ليس|نعم", 0.8),
                
                # Hindi patterns
                ("hi", "characters", "का|की|के|में|पर|से|तक|के|लिए|साथ|बिना|बारे", 0.9),
                ("hi", "characters", "है|हैं|था|थे|था|थीं|हो|होए|होई", 0.8),
                ("hi", "characters", "मैं|तू|तुम|आप|वह|वे|हम|यह|ये", 0.7)
            ]
            
            cursor.executemany('''
                INSERT INTO language_patterns (language_code, pattern_type, pattern, confidence)
                VALUES (?, ?, ?, ?)
            ''', patterns)
        
        conn.commit()
        conn.close()
    
    def detect_language(self, text: str) -> List[Tuple[str, float]]:
        """Detect the language of given text using pattern matching"""
        try:
            if not text or len(text.strip()) < 10:
                return [("en", 0.5)]  # Default to English for short text
            
            text = text.lower().strip()
            detected_languages = {}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all language patterns
            cursor.execute('''
                SELECT language_code, pattern_type, pattern, confidence
                FROM language_patterns
                ORDER BY confidence DESC
            ''')
            
            patterns = cursor.fetchall()
            conn.close()
            
            for lang_code, pattern_type, pattern, confidence in patterns:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = 0.0
                
                # Count pattern matches
                matches = len(re.findall(pattern, text))
                if matches > 0:
                    # Calculate score based on matches and confidence
                    score = min(1.0, (matches / len(text.split())) * confidence * 10)
                    detected_languages[lang_code] += score
            
            # Normalize scores and sort by confidence
            total_score = sum(detected_languages.values())
            if total_score > 0:
                normalized_scores = [(lang, score / total_score) for lang, score in detected_languages.items()]
                normalized_scores.sort(key=lambda x: x[1], reverse=True)
                return normalized_scores
            
            return [("en", 0.5)]  # Default fallback
            
        except Exception as e:
            print(f"Error detecting language: {e}")
            return [("en", 0.5)]
    
    def get_primary_language(self, text: str) -> str:
        """Get the primary detected language"""
        detected = self.detect_language(text)
        return detected[0][0] if detected else "en"
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """Translate text to target language (simplified rule-based translation)"""
        try:
            if not source_language:
                source_language = self.get_primary_language(text)
            
            if source_language == target_language:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 1.0
                }
            
            # Check translation cache first
            cache_result = self.get_cached_translation(text, source_language, target_language)
            if cache_result:
                return cache_result
            
            # Simple rule-based translations for common phrases
            translated_text = self.simple_translate(text, source_language, target_language)
            
            if translated_text != text:
                # Cache the translation
                self.cache_translation(text, source_language, target_language, translated_text, 0.7)
                
                return {
                    "success": True,
                    "translated_text": translated_text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 0.7
                }
            else:
                # No translation available
                return {
                    "success": False,
                    "error": "Translation not available",
                    "source_language": source_language,
                    "target_language": target_language
                }
                
        except Exception as e:
            print(f"Error translating text: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_language": source_language,
                "target_language": target_language
            }
    
    def simple_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simple rule-based translation for common phrases"""
        # This is a simplified translation system
        # In a real implementation, you would use a proper translation API
        
        common_translations = {
            ("en", "es"): {
                "hello": "hola",
                "goodbye": "adiós",
                "thank you": "gracias",
                "please": "por favor",
                "yes": "sí",
                "no": "no",
                "good": "bueno",
                "bad": "malo",
                "big": "grande",
                "small": "pequeño"
            },
            ("en", "fr"): {
                "hello": "bonjour",
                "goodbye": "au revoir",
                "thank you": "merci",
                "please": "s'il vous plaît",
                "yes": "oui",
                "no": "non",
                "good": "bon",
                "bad": "mauvais",
                "big": "grand",
                "small": "petit"
            },
            ("en", "de"): {
                "hello": "hallo",
                "goodbye": "auf wiedersehen",
                "thank you": "danke",
                "please": "bitte",
                "yes": "ja",
                "no": "nein",
                "good": "gut",
                "bad": "schlecht",
                "big": "groß",
                "small": "klein"
            }
        }
        
        translation_key = (source_lang, target_lang)
        if translation_key in common_translations:
            translations = common_translations[translation_key]
            translated_text = text.lower()
            
            for english, translated in translations.items():
                translated_text = translated_text.replace(english, translated)
            
            return translated_text
        
        return text  # No translation available
    
    def cache_translation(self, source_text: str, source_lang: str, target_lang: str, translated_text: str, confidence: float):
        """Cache a translation for future use"""
        try:
            source_hash = hashlib.md5(source_text.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO translation_cache 
                (source_text_hash, source_text, source_language, target_language, translated_text, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source_hash, source_text, source_lang, target_lang, translated_text, confidence))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error caching translation: {e}")
    
    def get_cached_translation(self, source_text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Get cached translation if available"""
        try:
            source_hash = hashlib.md5(source_text.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT translated_text, confidence, created_at
                FROM translation_cache 
                WHERE source_text_hash = ? AND source_language = ? AND target_language = ?
            ''', (source_hash, source_lang, target_lang))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                translated_text, confidence, created_at = result
                return {
                    "success": True,
                    "translated_text": translated_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": confidence,
                    "cached": True,
                    "cached_at": created_at
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting cached translation: {e}")
            return None
    
    def set_user_language_preferences(self, user_id: int, primary_language: str, secondary_languages: List[str] = None, 
                                    interface_language: str = None, content_language: str = None, auto_translate: bool = True) -> bool:
        """Set user language preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            secondary_langs = json.dumps(secondary_languages) if secondary_languages else json.dumps([])
            interface_lang = interface_language or primary_language
            content_lang = content_language or primary_language
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_language_preferences 
                (user_id, primary_language, secondary_languages, interface_language, content_language, auto_translate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, primary_language, secondary_langs, interface_lang, content_lang, auto_translate))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error setting user language preferences: {e}")
            return False
    
    def get_user_language_preferences(self, user_id: int) -> Dict:
        """Get user language preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT primary_language, secondary_languages, interface_language, content_language, auto_translate
                FROM user_language_preferences WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                primary_lang, secondary_langs, interface_lang, content_lang, auto_translate = result
                return {
                    "primary_language": primary_lang,
                    "secondary_languages": json.loads(secondary_langs) if secondary_langs else [],
                    "interface_language": interface_lang,
                    "content_language": content_lang,
                    "auto_translate": bool(auto_translate)
                }
            
            return {}
            
        except Exception as e:
            print(f"Error getting user language preferences: {e}")
            return {}
    
    def create_multilingual_content(self, content_id: str, content_type: str, original_text: str, 
                                  original_language: str, translations: Dict[str, str] = None) -> bool:
        """Create multilingual content entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            translations_json = json.dumps(translations) if translations else json.dumps({})
            
            cursor.execute('''
                INSERT OR REPLACE INTO multilingual_content 
                (content_id, content_type, original_language, original_text, translations, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (content_id, content_type, original_language, original_text, translations_json))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating multilingual content: {e}")
            return False
    
    def get_multilingual_content(self, content_id: str, target_language: str = None) -> Optional[Dict]:
        """Get multilingual content in specified language"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT content_type, original_language, original_text, translations
                FROM multilingual_content WHERE content_id = ?
            ''', (content_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                content_type, original_language, original_text, translations = result
                translations_dict = json.loads(translations) if translations else {}
                
                if target_language and target_language in translations_dict:
                    return {
                        "content_id": content_id,
                        "content_type": content_type,
                        "language": target_language,
                        "text": translations_dict[target_language],
                        "original_language": original_language,
                        "translated": True
                    }
                else:
                    return {
                        "content_id": content_id,
                        "content_type": content_type,
                        "language": original_language,
                        "text": original_text,
                        "translated": False
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting multilingual content: {e}")
            return None
    
    def add_translation(self, content_id: str, target_language: str, translated_text: str) -> bool:
        """Add a translation to existing multilingual content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing translations
            cursor.execute('SELECT translations FROM multilingual_content WHERE content_id = ?', (content_id,))
            result = cursor.fetchone()
            
            if result:
                translations = json.loads(result[0]) if result[0] else {}
                translations[target_language] = translated_text
                
                cursor.execute('''
                    UPDATE multilingual_content 
                    SET translations = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE content_id = ?
                ''', (json.dumps(translations), content_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"Error adding translation: {e}")
            return False
    
    def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT language_code, language_name, native_name, is_active
                FROM supported_languages 
                WHERE is_active = TRUE
                ORDER BY language_name
            ''')
            
            languages = []
            for row in cursor.fetchall():
                language_code, language_name, native_name, is_active = row
                languages.append({
                    "code": language_code,
                    "name": language_name,
                    "native_name": native_name,
                    "active": bool(is_active)
                })
            
            conn.close()
            return languages
            
        except Exception as e:
            print(f"Error getting supported languages: {e}")
            return []
    
    def get_language_stats(self) -> Dict:
        """Get statistics about language usage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count content by language
            cursor.execute('''
                SELECT original_language, COUNT(*) 
                FROM multilingual_content 
                GROUP BY original_language
            ''')
            content_by_language = dict(cursor.fetchall())
            
            # Count translations by target language
            cursor.execute('''
                SELECT target_language, COUNT(*) 
                FROM translation_cache 
                GROUP BY target_language
            ''')
            translations_by_language = dict(cursor.fetchall())
            
            # Count user preferences by language
            cursor.execute('''
                SELECT primary_language, COUNT(*) 
                FROM user_language_preferences 
                GROUP BY primary_language
            ''')
            users_by_language = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "content_by_language": content_by_language,
                "translations_by_language": translations_by_language,
                "users_by_language": users_by_language,
                "total_languages": len(content_by_language),
                "total_translations": sum(translations_by_language.values()),
                "total_users": sum(users_by_language.values())
            }
            
        except Exception as e:
            print(f"Error getting language stats: {e}")
            return {}
    
    def cleanup_old_translations(self, days_old: int = 90) -> int:
        """Clean up old translation cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # This would require a proper date field in translation_cache
            # For now, we'll just return 0
            conn.close()
            return 0
            
        except Exception as e:
            print(f"Error cleaning up old translations: {e}")
            return 0



