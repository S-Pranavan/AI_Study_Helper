"""
AI Study Helper - Phase 4: AI Tutor Module
Implements chat-based learning assistance using free resources
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message in the AI Tutor system"""
    id: Optional[int]
    session_id: str
    user_message: str
    ai_response: str
    message_type: str  # 'question', 'explanation', 'example', 'guidance'
    subject: str
    difficulty: str
    timestamp: datetime
    context: Dict[str, str]  # Additional context like previous messages, content references

@dataclass
class MindMapNode:
    """Represents a node in the mind map"""
    id: str
    label: str
    content: str
    node_type: str  # 'concept', 'example', 'definition', 'relationship'
    x: float
    y: float
    connections: List[str]  # IDs of connected nodes

@dataclass
class MindMap:
    """Represents a complete mind map"""
    id: str
    title: str
    subject: str
    nodes: List[MindMapNode]
    created_at: datetime
    last_updated: datetime

class AITutor:
    """AI Tutor system providing chat-based learning assistance"""
    
    def __init__(self, db_path: str = "study_helper.db"):
        self.db_path = db_path
        self.init_database()
        
        # Educational response patterns
        self.response_patterns = {
            'explanation': [
                "Let me explain this concept step by step:",
                "Here's a clear breakdown of this topic:",
                "Let me break this down for you:"
            ],
            'example': [
                "Here's a practical example:",
                "Let me show you with an example:",
                "Consider this real-world scenario:"
            ],
            'guidance': [
                "Here's how you can approach this:",
                "My recommendation is to:",
                "Try this strategy:"
            ],
            'question': [
                "Let me ask you a question to help you think:",
                "Here's something to consider:",
                "Think about this:"
            ]
        }
        
        # Subject-specific knowledge bases
        self.subject_knowledge = {
            'Mathematics': {
                'concepts': ['algebra', 'calculus', 'geometry', 'statistics', 'trigonometry'],
                'examples': ['equations', 'proofs', 'formulas', 'theorems'],
                'difficulty_levels': ['basic', 'intermediate', 'advanced']
            },
            'Science': {
                'concepts': ['physics', 'chemistry', 'biology', 'astronomy', 'geology'],
                'examples': ['experiments', 'observations', 'hypotheses', 'theories'],
                'difficulty_levels': ['fundamental', 'applied', 'research']
            },
            'Language': {
                'concepts': ['grammar', 'vocabulary', 'literature', 'composition', 'rhetoric'],
                'examples': ['sentences', 'paragraphs', 'essays', 'poems'],
                'difficulty_levels': ['beginner', 'intermediate', 'advanced']
            },
            'History': {
                'concepts': ['events', 'people', 'periods', 'movements', 'civilizations'],
                'examples': ['battles', 'treaties', 'revolutions', 'discoveries'],
                'difficulty_levels': ['ancient', 'medieval', 'modern']
            }
        }
    
    def init_database(self):
        """Initialize database tables for AI Tutor and Mind Maps"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                subject TEXT,
                difficulty TEXT,
                user_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                message_type TEXT NOT NULL,
                subject TEXT,
                difficulty TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT,  -- JSON string for additional context
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # Mind maps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mind_maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                nodes TEXT NOT NULL,  -- JSON string for nodes
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("AI Tutor database initialized successfully")
    
    def create_chat_session(self, subject: str = "General", difficulty: str = "medium", user_level: str = "intermediate") -> str:
        """Create a new chat session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{subject.lower()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (session_id, subject, difficulty, user_level)
            VALUES (?, ?, ?, ?)
        ''', (session_id, subject, difficulty, user_level))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created chat session: {session_id}")
        return session_id
    
    def get_chat_response(self, session_id: str, user_message: str, subject: str = "General", difficulty: str = "medium") -> Dict[str, str]:
        """Generate AI tutor response to user message"""
        try:
            # Analyze user message to determine response type
            response_type = self._analyze_message_type(user_message)
            
            # Generate contextual response
            ai_response = self._generate_educational_response(user_message, response_type, subject, difficulty)
            
            # Save message to database
            self._save_chat_message(session_id, user_message, ai_response, response_type, subject, difficulty)
            
            return {
                'response': ai_response,
                'type': response_type,
                'subject': subject,
                'difficulty': difficulty,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                'response': "I'm having trouble processing your request right now. Please try again or rephrase your question.",
                'type': 'error',
                'subject': subject,
                'difficulty': difficulty,
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_message_type(self, message: str) -> str:
        """Analyze user message to determine appropriate response type"""
        message_lower = message.lower()
        
        # Check for question patterns
        if any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', '?']):
            return 'explanation'
        
        # Check for example requests
        if any(word in message_lower for word in ['example', 'instance', 'show me', 'demonstrate']):
            return 'example'
        
        # Check for guidance requests
        if any(word in message_lower for word in ['help', 'guide', 'advice', 'suggest', 'recommend']):
            return 'guidance'
        
        # Check for clarification requests
        if any(word in message_lower for word in ['clarify', 'explain', 'understand', 'confused']):
            return 'explanation'
        
        # Default to explanation
        return 'explanation'
    
    def _generate_educational_response(self, user_message: str, response_type: str, subject: str, difficulty: str) -> str:
        """Generate educational response based on message type and subject"""
        
        # Get response pattern
        pattern = self.response_patterns.get(response_type, self.response_patterns['explanation'])[0]
        
        if response_type == 'explanation':
            return self._generate_explanation_response(user_message, subject, difficulty, pattern)
        elif response_type == 'example':
            return self._generate_example_response(user_message, subject, difficulty, pattern)
        elif response_type == 'guidance':
            return self._generate_guidance_response(user_message, subject, difficulty, pattern)
        else:
            return self._generate_explanation_response(user_message, subject, difficulty, pattern)
    
    def _generate_explanation_response(self, user_message: str, subject: str, difficulty: str, pattern: str) -> str:
        """Generate explanation response"""
        # Extract key concepts from user message
        concepts = self._extract_concepts(user_message)
        
        if subject in self.subject_knowledge:
            subject_info = self.subject_knowledge[subject]
            relevant_concepts = [c for c in concepts if c.lower() in [s.lower() for s in subject_info['concepts']]]
            
            if relevant_concepts:
                return f"{pattern} {subject} involves understanding {', '.join(relevant_concepts)}. These concepts form the foundation of {subject.lower()} and are essential for building more advanced knowledge. Would you like me to explain any specific concept in more detail?"
            else:
                return f"{pattern} {subject} is a fascinating field that covers many important topics. Based on your question, I can help you understand the fundamental principles and how they apply to your specific area of interest. What aspect would you like to explore further?"
        else:
            return f"{pattern} This is an interesting topic that can be approached from multiple angles. Let me help you understand the key concepts and how they relate to each other. What specific aspect would you like me to clarify?"
    
    def _generate_example_response(self, user_message: str, subject: str, difficulty: str, pattern: str) -> str:
        """Generate example response"""
        if subject == 'Mathematics':
            return f"{pattern} In mathematics, we often use concrete examples to illustrate abstract concepts. For instance, if you're learning about equations, we might use a simple problem like 'If you have 5 apples and add 3 more, how many do you have?' This helps visualize the mathematical concept of addition. Would you like me to provide more specific examples for your topic?"
        elif subject == 'Science':
            return f"{pattern} Science is all about observation and experimentation. A great example would be how we learn about gravity by dropping objects and observing how they fall. This hands-on approach helps us understand complex scientific principles. What specific scientific concept would you like me to illustrate with examples?"
        else:
            return f"{pattern} Examples are powerful tools for learning because they make abstract concepts concrete and relatable. They help us see how theoretical knowledge applies to real-world situations. What specific concept would you like me to demonstrate with examples?"
    
    def _generate_guidance_response(self, user_message: str, subject: str, difficulty: str, pattern: str) -> str:
        """Generate guidance response"""
        if difficulty == 'beginner':
            return f"{pattern} Start with the fundamentals and build your knowledge step by step. Don't rush - take time to understand each concept before moving to the next. Practice regularly and don't be afraid to ask questions. What specific area would you like to focus on first?"
        elif difficulty == 'intermediate':
            return f"{pattern} You're ready to explore more complex applications and connections between concepts. Try to see how different ideas relate to each other and practice applying your knowledge to new situations. What challenging aspect would you like to tackle?"
        else:  # advanced
            return f"{pattern} At this level, you're ready to explore advanced topics and original research. Consider how you can contribute new insights or applications. What frontier area interests you most?"
    
    def _extract_concepts(self, message: str) -> List[str]:
        """Extract key concepts from user message"""
        # Simple concept extraction - in a real system, this would use NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', message.lower())
        # Filter out common words
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        concepts = [word for word in words if word not in common_words]
        return concepts[:5]  # Return top 5 concepts
    
    def _save_chat_message(self, session_id: str, user_message: str, ai_response: str, message_type: str, subject: str, difficulty: str):
        """Save chat message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context = json.dumps({
            'session_id': session_id,
            'subject': subject,
            'difficulty': difficulty
        })
        
        cursor.execute('''
            INSERT INTO chat_messages (session_id, user_message, ai_response, message_type, subject, difficulty, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_message, ai_response, message_type, subject, difficulty, context))
        
        # Update last activity in chat session
        cursor.execute('''
            UPDATE chat_sessions 
            SET last_activity = CURRENT_TIMESTAMP 
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, user_message, ai_response, message_type, subject, difficulty, timestamp, context
            FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            context = json.loads(row[8]) if row[8] else {}
            message = ChatMessage(
                id=row[0],
                session_id=row[1],
                user_message=row[2],
                ai_response=row[3],
                message_type=row[4],
                subject=row[5],
                difficulty=row[6],
                timestamp=datetime.fromisoformat(row[7]),
                context=context
            )
            messages.append(message)
        
        conn.close()
        return messages
    
    def create_mind_map(self, title: str, subject: str, content: str) -> MindMap:
        """Create a mind map from content"""
        map_id = f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{subject.lower()}"
        
        # Generate nodes from content
        nodes = self._generate_mind_map_nodes(content, subject)
        
        mind_map = MindMap(
            id=map_id,
            title=title,
            subject=subject,
            nodes=nodes,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Save to database
        self._save_mind_map(mind_map)
        
        return mind_map
    
    def _generate_mind_map_nodes(self, content: str, subject: str) -> List[MindMapNode]:
        """Generate mind map nodes from content"""
        nodes = []
        
        # Extract sentences and create concept nodes
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:10]):  # Limit to 10 nodes
            # Extract key concepts from sentence
            concepts = self._extract_concepts(sentence)
            if concepts:
                main_concept = concepts[0]
                
                node = MindMapNode(
                    id=f"node_{i}",
                    label=main_concept.title(),
                    content=sentence,
                    node_type='concept',
                    x=0.0,  # Will be calculated by frontend
                    y=0.0,  # Will be calculated by frontend
                    connections=[]
                )
                nodes.append(node)
        
        # Add subject node as central node
        central_node = MindMapNode(
            id="central",
            label=subject.title(),
            content=f"Main topic: {subject}",
            node_type='concept',
            x=0.0,
            y=0.0,
            connections=[node.id for node in nodes]
        )
        nodes.insert(0, central_node)
        
        return nodes
    
    def _save_mind_map(self, mind_map: MindMap):
        """Save mind map to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        nodes_json = json.dumps([{
            'id': node.id,
            'label': node.label,
            'content': node.content,
            'node_type': node.node_type,
            'x': node.x,
            'y': node.y,
            'connections': node.connections
        } for node in mind_map.nodes])
        
        cursor.execute('''
            INSERT OR REPLACE INTO mind_maps (map_id, title, subject, nodes, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (mind_map.id, mind_map.title, mind_map.subject, nodes_json, mind_map.last_updated.isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_mind_map(self, map_id: str) -> Optional[MindMap]:
        """Retrieve mind map by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT map_id, title, subject, nodes, created_at, last_updated
            FROM mind_maps 
            WHERE map_id = ?
        ''', (map_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            nodes_data = json.loads(row[3])
            nodes = []
            for node_data in nodes_data:
                node = MindMapNode(
                    id=node_data['id'],
                    label=node_data['label'],
                    content=node_data['content'],
                    node_type=node_data['node_type'],
                    x=node_data['x'],
                    y=node_data['y'],
                    connections=node_data['connections']
                )
                nodes.append(node)
            
            return MindMap(
                id=row[0],
                title=row[1],
                subject=row[2],
                nodes=nodes,
                created_at=datetime.fromisoformat(row[4]),
                last_updated=datetime.fromisoformat(row[5])
            )
        
        return None
    
    def get_all_mind_maps(self, subject: str = None) -> List[MindMap]:
        """Get all mind maps, optionally filtered by subject"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if subject:
            cursor.execute('''
                SELECT map_id, title, subject, nodes, created_at, last_updated
                FROM mind_maps 
                WHERE subject = ?
                ORDER BY last_updated DESC
            ''', (subject,))
        else:
            cursor.execute('''
                SELECT map_id, title, subject, nodes, created_at, last_updated
                FROM mind_maps 
                ORDER BY last_updated DESC
            ''')
        
        mind_maps = []
        for row in cursor.fetchall():
            nodes_data = json.loads(row[3])
            nodes = []
            for node_data in nodes_data:
                node = MindMapNode(
                    id=node_data['id'],
                    label=node_data['label'],
                    content=node_data['content'],
                    node_type=node_data['node_type'],
                    x=node_data['x'],
                    y=node_data['y'],
                    connections=node_data['connections']
                )
                nodes.append(node)
            
            mind_map = MindMap(
                id=row[0],
                title=row[1],
                subject=row[2],
                nodes=nodes,
                created_at=datetime.fromisoformat(row[4]),
                last_updated=datetime.fromisoformat(row[5])
            )
            mind_maps.append(mind_map)
        
        conn.close()
        return mind_maps
    
    def get_chat_statistics(self) -> Dict[str, any]:
        """Get statistics about chat usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        total_messages = cursor.fetchone()[0]
        
        # Messages by type
        cursor.execute('SELECT message_type, COUNT(*) FROM chat_messages GROUP BY message_type')
        messages_by_type = dict(cursor.fetchall())
        
        # Messages by subject
        cursor.execute('SELECT subject, COUNT(*) FROM chat_messages GROUP BY subject')
        messages_by_subject = dict(cursor.fetchall())
        
        # Total mind maps
        cursor.execute('SELECT COUNT(*) FROM mind_maps')
        total_mind_maps = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'messages_by_type': messages_by_type,
            'messages_by_subject': messages_by_subject,
            'total_mind_maps': total_mind_maps
        }
