import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

class PWAOfflineSupport:
    def __init__(self, db_path: str = "study_helper.db"):
        self.db_path = db_path
        self.cache_dir = "offline_cache"
        self.init_offline_tables()
        self.ensure_cache_directory()
    
    def ensure_cache_directory(self):
        """Ensure the offline cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def init_offline_tables(self):
        """Initialize offline-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Offline content cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_content (
                id INTEGER PRIMARY KEY,
                content_hash TEXT UNIQUE,
                content_type TEXT,
                content_data TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Offline study sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_study_sessions (
                id INTEGER PRIMARY KEY,
                session_id TEXT UNIQUE,
                user_id INTEGER,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE,
                sync_timestamp TIMESTAMP
            )
 ''')
        
        # Offline quiz results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_quiz_results (
                id INTEGER PRIMARY KEY,
                quiz_id TEXT UNIQUE,
                user_id INTEGER,
                quiz_data TEXT,
                results_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE,
                sync_timestamp TIMESTAMP
            )
        ''')
        
        # Offline flashcard progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_flashcard_progress (
                id INTEGER PRIMARY KEY,
                flashcard_id TEXT UNIQUE,
                user_id INTEGER,
                progress_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE,
                sync_timestamp TIMESTAMP
            )
        ''')
        
        # Offline user preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_user_preferences (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                preference_key TEXT,
                preference_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key)
            )
        ''')
        
        # Offline sync queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_sync_queue (
                id INTEGER PRIMARY KEY,
                sync_type TEXT,
                sync_data TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                last_attempt TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cache_content(self, content: str, content_type: str, metadata: Dict = None) -> str:
        """Cache content for offline access"""
        try:
            # Generate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if content already exists
            cursor.execute('''
                SELECT id FROM offline_content WHERE content_hash = ?
            ''', (content_hash,))
            
            if cursor.fetchone():
                # Update access info
                cursor.execute('''
                    UPDATE offline_content 
                    SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                    WHERE content_hash = ?
                ''', (content_hash,))
            else:
                # Insert new content
                cursor.execute('''
                    INSERT INTO offline_content (content_hash, content_type, content_data, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (content_hash, content_type, content, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
            return content_hash
            
        except Exception as e:
            print(f"Error caching content: {e}")
            return None
    
    def get_cached_content(self, content_hash: str) -> Optional[Dict]:
        """Retrieve cached content by hash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT content_type, content_data, metadata, last_accessed, access_count
                FROM offline_content WHERE content_hash = ?
            ''', (content_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                content_type, content_data, metadata, last_accessed, access_count = result
                return {
                    "content_type": content_type,
                    "content_data": content_data,
                    "metadata": json.loads(metadata) if metadata else None,
                    "last_accessed": last_accessed,
                    "access_count": access_count
                }
            
            return None
            
        except Exception as e:
            print(f"Error retrieving cached content: {e}")
            return None
    
    def search_cached_content(self, query: str, content_type: str = None) -> List[Dict]:
        """Search cached content by query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if content_type:
                cursor.execute('''
                    SELECT content_hash, content_type, content_data, metadata, last_accessed, access_count
                    FROM offline_content 
                    WHERE content_type = ? AND content_data LIKE ?
                    ORDER BY last_accessed DESC
                ''', (content_type, f"%{query}%"))
            else:
                cursor.execute('''
                    SELECT content_hash, content_type, content_data, metadata, last_accessed, access_count
                    FROM offline_content 
                    WHERE content_data LIKE ?
                    ORDER BY last_accessed DESC
                ''', (f"%{query}%",))
            
            results = []
            for row in cursor.fetchall():
                content_hash, content_type, content_data, metadata, last_accessed, access_count = row
                results.append({
                    "content_hash": content_hash,
                    "content_type": content_type,
                    "content_data": content_data,
                    "metadata": json.loads(metadata) if metadata else None,
                    "last_accessed": last_accessed,
                    "access_count": access_count
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error searching cached content: {e}")
            return []
    
    def store_offline_study_session(self, user_id: int, session_data: Dict) -> str:
        """Store a study session for offline access"""
        try:
            session_id = f"offline_{user_id}_{int(datetime.now().timestamp())}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_study_sessions (session_id, user_id, session_data)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, json.dumps(session_data)))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            print(f"Error storing offline study session: {e}")
            return None
    
    def store_offline_quiz_result(self, user_id: int, quiz_data: Dict, results_data: Dict) -> str:
        """Store quiz results for offline access"""
        try:
            quiz_id = f"offline_quiz_{user_id}_{int(datetime.now().timestamp())}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_quiz_results (quiz_id, user_id, quiz_data, results_data)
                VALUES (?, ?, ?, ?)
            ''', (quiz_id, user_id, json.dumps(quiz_data), json.dumps(results_data)))
            
            conn.commit()
            conn.close()
            
            return quiz_id
            
        except Exception as e:
            print(f"Error storing offline quiz result: {e}")
            return None
    
    def store_offline_flashcard_progress(self, user_id: int, progress_data: Dict) -> str:
        """Store flashcard progress for offline access"""
        try:
            flashcard_id = f"offline_flashcard_{user_id}_{int(datetime.now().timestamp())}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_flashcard_progress (flashcard_id, user_id, progress_data)
                VALUES (?, ?, ?)
            ''', (flashcard_id, user_id, json.dumps(progress_data)))
            
            conn.commit()
            conn.close()
            
            return flashcard_id
            
        except Exception as e:
            print(f"Error storing offline flashcard progress: {e}")
            return None
    
    def get_offline_study_sessions(self, user_id: int) -> List[Dict]:
        """Get offline study sessions for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, session_data, created_at, synced
                FROM offline_study_sessions 
                WHERE user_id = ? AND synced = FALSE
                ORDER BY created_at DESC
            ''', (user_id,))
            
            sessions = []
            for row in cursor.fetchall():
                session_id, session_data, created_at, synced = row
                sessions.append({
                    "session_id": session_id,
                    "session_data": json.loads(session_data),
                    "created_at": created_at,
                    "synced": bool(synced)
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Error getting offline study sessions: {e}")
            return []
    
    def get_offline_quiz_results(self, user_id: int) -> List[Dict]:
        """Get offline quiz results for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT quiz_id, quiz_data, results_data, created_at, synced
                FROM offline_quiz_results 
                WHERE user_id = ? AND synced = FALSE
                ORDER BY created_at DESC
            ''', (user_id,))
            
            results = []
            for row in cursor.fetchall():
                quiz_id, quiz_data, results_data, created_at, synced = row
                results.append({
                    "quiz_id": quiz_id,
                    "quiz_data": json.loads(quiz_data),
                    "results_data": json.loads(results_data),
                    "created_at": created_at,
                    "synced": bool(synced)
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting offline quiz results: {e}")
            return []
    
    def get_offline_flashcard_progress(self, user_id: int) -> List[Dict]:
        """Get offline flashcard progress for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT flashcard_id, progress_data, created_at, synced
                FROM offline_flashcard_progress 
                WHERE user_id = ? AND synced = FALSE
                ORDER BY created_at DESC
            ''', (user_id,))
            
            progress = []
            for row in cursor.fetchall():
                flashcard_id, progress_data, created_at, synced = row
                progress.append({
                    "flashcard_id": flashcard_id,
                    "progress_data": json.loads(progress_data),
                    "created_at": created_at,
                    "synced": bool(synced)
                })
            
            conn.close()
            return progress
            
        except Exception as e:
            print(f"Error getting offline flashcard progress: {e}")
            return []
    
    def set_user_preference(self, user_id: int, key: str, value: Any) -> bool:
        """Set a user preference for offline access"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO offline_user_preferences (user_id, preference_key, preference_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error setting user preference: {e}")
            return False
    
    def get_user_preference(self, user_id: int, key: str, default_value: Any = None) -> Any:
        """Get a user preference for offline access"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preference_value FROM offline_user_preferences 
                WHERE user_id = ? AND preference_key = ?
            ''', (user_id, key))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            
            return default_value
            
        except Exception as e:
            print(f"Error getting user preference: {e}")
            return default_value
    
    def add_to_sync_queue(self, sync_type: str, sync_data: Dict, priority: int = 1) -> bool:
        """Add an item to the offline sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_sync_queue (sync_type, sync_data, priority)
                VALUES (?, ?, ?)
            ''', (sync_type, json.dumps(sync_data), priority))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding to sync queue: {e}")
            return False
    
    def get_sync_queue(self, limit: int = 50) -> List[Dict]:
        """Get items from the sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, sync_type, sync_data, priority, created_at, attempts, max_attempts
                FROM offline_sync_queue 
                WHERE attempts < max_attempts
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            ''', (limit,))
            
            queue = []
            for row in cursor.fetchall():
                id, sync_type, sync_data, priority, created_at, attempts, max_attempts = row
                queue.append({
                    "id": id,
                    "sync_type": sync_type,
                    "sync_data": json.loads(sync_data),
                    "priority": priority,
                    "created_at": created_at,
                    "attempts": attempts,
                    "max_attempts": max_attempts
                })
            
            conn.close()
            return queue
            
        except Exception as e:
            print(f"Error getting sync queue: {e}")
            return []
    
    def mark_sync_attempt(self, sync_id: int, success: bool = False) -> bool:
        """Mark a sync attempt as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if success:
                # Remove from queue if successful
                cursor.execute('DELETE FROM offline_sync_queue WHERE id = ?', (sync_id,))
            else:
                # Increment attempt counter
                cursor.execute('''
                    UPDATE offline_sync_queue 
                    SET attempts = attempts + 1, last_attempt = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (sync_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error marking sync attempt: {e}")
            return False
    
    def cleanup_old_cache(self, days_old: int = 30) -> int:
        """Clean up old cached content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('''
                DELETE FROM offline_content 
                WHERE last_accessed < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the offline cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total cached items
            cursor.execute('SELECT COUNT(*) FROM offline_content')
            total_items = cursor.fetchone()[0]
            
            # Cache size by type
            cursor.execute('''
                SELECT content_type, COUNT(*) 
                FROM offline_content 
                GROUP BY content_type
            ''')
            type_counts = dict(cursor.fetchall())
            
            # Total cache size in bytes
            cursor.execute('''
                SELECT SUM(LENGTH(content_data)) FROM offline_content
            ''')
            total_size_bytes = cursor.fetchone()[0] or 0
            
            # Sync queue stats
            cursor.execute('SELECT COUNT(*) FROM offline_sync_queue')
            sync_queue_size = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_items": total_items,
                "type_counts": type_counts,
                "total_size_bytes": total_size_bytes,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
                "sync_queue_size": sync_queue_size
            }
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {}
    
    def export_offline_data(self, user_id: int) -> Dict:
        """Export all offline data for a user"""
        try:
            export_data = {
                "user_id": user_id,
                "export_timestamp": datetime.now().isoformat(),
                "study_sessions": self.get_offline_study_sessions(user_id),
                "quiz_results": self.get_offline_quiz_results(user_id),
                "flashcard_progress": self.get_offline_flashcard_progress(user_id),
                "preferences": {}
            }
            
            # Get user preferences
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preference_key, preference_value 
                FROM offline_user_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            
            for key, value in cursor.fetchall():
                export_data["preferences"][key] = json.loads(value)
            
            conn.close()
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting offline data: {e}")
            return {}
    
    def import_offline_data(self, user_id: int, import_data: Dict) -> bool:
        """Import offline data for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Import study sessions
            for session in import_data.get("study_sessions", []):
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_study_sessions 
                    (session_id, user_id, session_data, synced)
                    VALUES (?, ?, ?, FALSE)
                ''', (session["session_id"], user_id, json.dumps(session["session_data"])))
            
            # Import quiz results
            for quiz in import_data.get("quiz_results", []):
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_quiz_results 
                    (quiz_id, user_id, quiz_data, results_data, synced)
                    VALUES (?, ?, ?, ?, FALSE)
                ''', (quiz["quiz_id"], user_id, json.dumps(quiz["quiz_data"]), json.dumps(quiz["results_data"])))
            
            # Import flashcard progress
            for flashcard in import_data.get("flashcard_progress", []):
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_flashcard_progress 
                    (flashcard_id, user_id, progress_data, synced)
                    VALUES (?, ?, ?, FALSE)
                ''', (flashcard["flashcard_id"], user_id, json.dumps(flashcard["progress_data"])))
            
            # Import preferences
            for key, value in import_data.get("preferences", {}).items():
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_user_preferences 
                    (user_id, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error importing offline data: {e}")
            return False



