import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GamificationSystem:
    def __init__(self, db_path: str = "study_helper.db"):
        self.db_path = db_path
        self.init_gamification_tables()
    
    def init_gamification_tables(self):
        """Initialize gamification-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # XP and leveling system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                total_study_time INTEGER DEFAULT 0,
                quizzes_taken INTEGER DEFAULT 0,
                flashcards_reviewed INTEGER DEFAULT 0,
                content_processed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Badge system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                description TEXT,
                icon TEXT,
                xp_requirement INTEGER,
                category TEXT
            )
        ''')
        
        # User badges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                badge_id INTEGER,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_progress (user_id),
                FOREIGN KEY (badge_id) REFERENCES badges (id)
            )
        ''')
        
        # Study sessions with XP tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions_xp (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                session_type TEXT,
                duration_minutes INTEGER,
                xp_earned INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
            )
        ''')
        
        # Achievement tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                description TEXT,
                xp_reward INTEGER,
                requirement_type TEXT,
                requirement_value INTEGER,
                category TEXT
            )
 ''')
        
        # User achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                achievement_id INTEGER,
                progress_current INTEGER DEFAULT 0,
                progress_required INTEGER,
                completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_progress (user_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default badges and achievements
        self.initialize_default_content()
    
    def initialize_default_content(self):
        """Initialize default badges and achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if badges already exist
        cursor.execute("SELECT COUNT(*) FROM badges")
        if cursor.fetchone()[0] == 0:
            # Insert default badges
            default_badges = [
                ("First Steps", "Complete your first study session", "🌟", 0, "beginner"),
                ("Quick Learner", "Complete 5 study sessions", "📚", 100, "learning"),
                ("Quiz Master", "Take 10 quizzes", "🎯", 250, "quiz"),
                ("Flashcard Pro", "Review 50 flashcards", "💡", 300, "flashcard"),
                ("Content Creator", "Process 20 images", "📷", 400, "content"),
                ("Study Streak", "Study for 7 consecutive days", "🔥", 500, "streak"),
                ("XP Collector", "Earn 1000 XP", "💎", 1000, "milestone"),
                ("Level Up", "Reach level 10", "⭐", 1500, "level"),
                ("Dedicated Student", "Study for 100 hours total", "🏆", 2000, "dedication"),
                ("AI Explorer", "Use all AI features", "🤖", 800, "ai")
            ]
            
            cursor.executemany('''
                INSERT INTO badges (name, description, icon, xp_requirement, category)
                VALUES (?, ?, ?, ?, ?)
            ''', default_badges)
        
        # Check if achievements already exist
        cursor.execute("SELECT COUNT(*) FROM achievements")
        if cursor.fetchone()[0] == 0:
            # Insert default achievements
            default_achievements = [
                ("Study Beginner", "Complete your first study session", 50, "study_sessions", 1, "beginner"),
                ("Study Enthusiast", "Complete 10 study sessions", 200, "study_sessions", 10, "learning"),
                ("Quiz Novice", "Take your first quiz", 75, "quizzes_taken", 1, "quiz"),
                ("Quiz Expert", "Take 25 quizzes", 300, "quizzes_taken", 25, "quiz"),
                ("Flashcard Learner", "Review 10 flashcards", 100, "flashcards_reviewed", 10, "flashcard"),
                ("Flashcard Master", "Review 100 flashcards", 400, "flashcards_reviewed", 100, "flashcard"),
                ("Content Processor", "Process 5 images", 150, "content_processed", 5, "content"),
                ("Content Expert", "Process 50 images", 600, "content_processed", 50, "content"),
                ("Time Dedication", "Study for 10 hours total", 300, "total_study_time", 600, "dedication"),
                ("Time Master", "Study for 100 hours total", 1000, "total_study_time", 6000, "dedication")
            ]
            
            cursor.executemany('''
                INSERT INTO achievements (name, description, xp_reward, requirement_type, requirement_value, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', default_achievements)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str) -> bool:
        """Create a new user in the gamification system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create user progress entry
            cursor.execute('''
                INSERT INTO user_progress (username, xp, level)
                VALUES (?, 0, 1)
            ''', (username,))
            
            user_id = cursor.lastrowid
            
            # Initialize achievements for the user
            cursor.execute("SELECT id, requirement_value FROM achievements")
            achievements = cursor.fetchall()
            
            for achievement_id, requirement_value in achievements:
                cursor.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, progress_required)
                    VALUES (?, ?, ?)
                ''', (user_id, achievement_id, requirement_value))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def award_xp(self, username: str, xp_amount: int, activity_type: str, duration_minutes: int = 0) -> Dict:
        """Award XP to a user and check for level ups and achievements"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current user progress
            cursor.execute('''
                SELECT user_id, xp, level FROM user_progress WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if not result:
                # Create user if doesn't exist
                self.create_user(username)
                cursor.execute('''
                    SELECT user_id, xp, level FROM user_progress WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
            
            user_id, current_xp, current_level = result
            
            # Calculate new XP and level
            new_xp = current_xp + xp_amount
            new_level = self.calculate_level(new_xp)
            
            # Update user progress
            cursor.execute('''
                UPDATE user_progress 
                SET xp = ?, level = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_xp, new_level, user_id))
            
            # Record study session
            if duration_minutes > 0:
                cursor.execute('''
                    INSERT INTO study_sessions_xp (user_id, session_type, duration_minutes, xp_earned)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, activity_type, duration_minutes, xp_amount))
            
            # Update activity counters
            if activity_type == "quiz":
                cursor.execute('''
                    UPDATE user_progress SET quizzes_taken = quizzes_taken + 1 WHERE user_id = ?
                ''', (user_id,))
            elif activity_type == "flashcard":
                cursor.execute('''
                    UPDATE user_progress SET flashcards_reviewed = flashcards_reviewed + 1 WHERE user_id = ?
                ''', (user_id,))
            elif activity_type == "content":
                cursor.execute('''
                    UPDATE user_progress SET content_processed = content_processed + 1 WHERE user_id = ?
                ''', (user_id,))
            
            # Update total study time
            if duration_minutes > 0:
                cursor.execute('''
                    UPDATE user_progress SET total_study_time = total_study_time + ? WHERE user_id = ?
                ''', (duration_minutes, user_id))
            
            # Check for achievements
            achievements_earned = self.check_achievements(user_id)
            
            # Check for badges
            badges_earned = self.check_badges(user_id, new_xp)
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "new_xp": new_xp,
                "xp_gained": xp_amount,
                "old_level": current_level,
                "new_level": new_level,
                "leveled_up": new_level > current_level,
                "achievements_earned": achievements_earned,
                "badges_earned": badges_earned
            }
            
        except Exception as e:
            print(f"Error awarding XP: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_level(self, xp: int) -> int:
        """Calculate level based on XP using a logarithmic scale"""
        if xp < 100:
            return 1
        elif xp < 300:
            return 2
        elif xp < 600:
            return 3
        elif xp < 1000:
            return 4
        elif xp < 1500:
            return 5
        elif xp < 2100:
            return 6
        elif xp < 2800:
            return 7
        elif xp < 3600:
            return 8
        elif xp < 4500:
            return 9
        elif xp < 5500:
            return 10
        else:
            # After level 10, each level requires 1000 more XP
            return 10 + ((xp - 5500) // 1000) + 1
    
    def check_achievements(self, user_id: int) -> List[Dict]:
        """Check if user has earned any new achievements"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user's current progress
            cursor.execute('''
                SELECT total_study_time, quizzes_taken, flashcards_reviewed, content_processed
                FROM user_progress WHERE user_id = ?
            ''', (user_id,))
            
            progress = cursor.fetchone()
            if not progress:
                return []
            
            total_study_time, quizzes_taken, flashcards_reviewed, content_processed = progress
            
            # Check each achievement type
            achievements_earned = []
            
            # Study sessions achievement
            cursor.execute('''
                SELECT COUNT(*) FROM study_sessions_xp WHERE user_id = ?
            ''', (user_id,))
            study_sessions = cursor.fetchone()[0]
            
            # Check achievements for each category
            achievement_categories = [
                ("study_sessions", study_sessions),
                ("quizzes_taken", quizzes_taken),
                ("flashcards_reviewed", flashcards_reviewed),
                ("content_processed", content_processed),
                ("total_study_time", total_study_time)
            ]
            
            for category, current_value in achievement_categories:
                cursor.execute('''
                    SELECT ua.achievement_id, a.name, a.description, a.xp_reward, ua.progress_required
                    FROM user_achievements ua
                    JOIN achievements a ON ua.achievement_id = a.id
                    WHERE ua.user_id = ? AND a.requirement_type = ? AND ua.completed = FALSE
                ''', (user_id, category))
                
                for achievement in cursor.fetchall():
                    achievement_id, name, description, xp_reward, required = achievement
                    
                    if current_value >= required:
                        # Mark achievement as completed
                        cursor.execute('''
                            UPDATE user_achievements 
                            SET completed = TRUE, completed_at = CURRENT_TIMESTAMP, progress_current = ?
                            WHERE user_id = ? AND achievement_id = ?
                        ''', (current_value, user_id, achievement_id))
                        
                        # Award XP for achievement
                        cursor.execute('''
                            UPDATE user_progress SET xp = xp + ? WHERE user_id = ?
                        ''', (xp_reward, user_id))
                        
                        achievements_earned.append({
                            "name": name,
                            "description": description,
                            "xp_reward": xp_reward,
                            "category": category
                        })
            
            conn.commit()
            conn.close()
            return achievements_earned
            
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return []
    
    def check_badges(self, user_id: int, current_xp: int) -> List[Dict]:
        """Check if user has earned any new badges"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get badges user doesn't have yet
            cursor.execute('''
                SELECT b.id, b.name, b.description, b.icon, b.category
                FROM badges b
                WHERE b.id NOT IN (
                    SELECT ub.badge_id FROM user_badges ub WHERE ub.user_id = ?
                )
                AND b.xp_requirement <= ?
            ''', (user_id, current_xp))
            
            eligible_badges = cursor.fetchall()
            badges_earned = []
            
            for badge in eligible_badges:
                badge_id, name, description, icon, category = badge
                
                # Award badge to user
                cursor.execute('''
                    INSERT INTO user_badges (user_id, badge_id)
                    VALUES (?, ?)
                ''', (user_id, badge_id))
                
                badges_earned.append({
                    "name": name,
                    "description": description,
                    "icon": icon,
                    "category": category
                })
            
            conn.commit()
            conn.close()
            return badges_earned
            
        except Exception as e:
            print(f"Error checking badges: {e}")
            return []
    
    def get_user_progress(self, username: str) -> Dict:
        """Get comprehensive user progress information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user progress
            cursor.execute('''
                SELECT xp, level, total_study_time, quizzes_taken, flashcards_reviewed, content_processed
                FROM user_progress WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if not result:
                return {"error": "User not found"}
            
            xp, level, total_study_time, quizzes_taken, flashcards_reviewed, content_processed = result
            
            # Get user badges
            cursor.execute('''
                SELECT b.name, b.description, b.icon, b.category, ub.earned_at
                FROM user_badges ub
                JOIN badges b ON ub.badge_id = b.id
                WHERE ub.user_id = (SELECT user_id FROM user_progress WHERE username = ?)
                ORDER BY ub.earned_at DESC
            ''', (username,))
            
            badges = [{"name": row[0], "description": row[1], "icon": row[2], "category": row[3], "earned_at": row[4]} 
                     for row in cursor.fetchall()]
            
            # Get user achievements
            cursor.execute('''
                SELECT a.name, a.description, a.xp_reward, a.category, ua.completed, ua.progress_current, ua.progress_required
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = (SELECT user_id FROM user_progress WHERE username = ?)
                ORDER BY a.category, a.xp_reward
            ''', (username,))
            
            achievements = [{"name": row[0], "description": row[1], "xp_reward": row[2], "category": row[3], 
                           "completed": bool(row[4]), "progress_current": row[5], "progress_required": row[6]} 
                          for row in cursor.fetchall()]
            
            # Calculate XP to next level
            xp_to_next = self.calculate_xp_to_next_level(xp, level)
            
            conn.close()
            
            return {
                "username": username,
                "xp": xp,
                "level": level,
                "xp_to_next_level": xp_to_next,
                "total_study_time_minutes": total_study_time,
                "total_study_time_hours": round(total_study_time / 60, 1),
                "quizzes_taken": quizzes_taken,
                "flashcards_reviewed": flashcards_reviewed,
                "content_processed": content_processed,
                "badges": badges,
                "achievements": achievements,
                "badges_count": len(badges),
                "achievements_count": len([a for a in achievements if a["completed"]]),
                "total_achievements": len(achievements)
            }
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {"error": str(e)}
    
    def calculate_xp_to_next_level(self, current_xp: int, current_level: int) -> int:
        """Calculate XP needed to reach next level"""
        if current_level == 1:
            if current_xp < 100:
                return 100 - current_xp
            else:
                return 300 - current_xp
        elif current_level == 2:
            return 600 - current_xp
        elif current_level == 3:
            return 1000 - current_xp
        elif current_level == 4:
            return 1500 - current_xp
        elif current_level == 5:
            return 2100 - current_xp
        elif current_level == 6:
            return 2800 - current_xp
        elif current_level == 7:
            return 3600 - current_xp
        elif current_level == 8:
            return 4500 - current_xp
        elif current_level == 9:
            return 5500 - current_xp
        else:
            # After level 10, each level requires 1000 more XP
            level_10_xp = 5500
            additional_levels = current_level - 10
            next_level_xp = level_10_xp + (additional_levels + 1) * 1000
            return next_level_xp - current_xp
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by XP for leaderboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, xp, level, total_study_time, quizzes_taken
                FROM user_progress
                ORDER BY xp DESC
                LIMIT ?
            ''', (limit,))
            
            leaderboard = []
            for i, row in enumerate(cursor.fetchall()):
                username, xp, level, total_study_time, quizzes_taken = row
                leaderboard.append({
                    "rank": i + 1,
                    "username": username,
                    "xp": xp,
                    "level": level,
                    "total_study_time_hours": round(total_study_time / 60, 1),
                    "quizzes_taken": quizzes_taken
                })
            
            conn.close()
            return leaderboard
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def get_recent_activity(self, username: str, limit: int = 10) -> List[Dict]:
        """Get recent activity for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_type, duration_minutes, xp_earned, created_at
                FROM study_sessions_xp
                WHERE user_id = (SELECT user_id FROM user_progress WHERE username = ?)
                ORDER BY created_at DESC
                LIMIT ?
            ''', (username, limit))
            
            activities = []
            for row in cursor.fetchall():
                session_type, duration_minutes, xp_earned, created_at = row
                activities.append({
                    "type": session_type,
                    "duration_minutes": duration_minutes,
                    "xp_earned": xp_earned,
                    "created_at": created_at
                })
            
            conn.close()
            return activities
            
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
