import openai
import json
import re
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Avg
from textblob import TextBlob
import numpy as np
import requests

from .models import (
    ChatSession, ChatMessage, TutorPersonality, 
    ConversationAnalytics, KnowledgeBase, StudentQuestionPattern
)
from apps.users.models import User
from apps.courses.models import Course, Subject
from apps.progress.models import StudentProgress
from apps.recommendations.models import LearningPattern

logger = logging.getLogger(__name__)

class IntelligentTutor:
    """
    Advanced AI Tutor powered by GPT with educational intelligence
    Real-world implementation with production-ready features
    """
    
    def __init__(self):
        # Configure OpenAI
        self.openai_client = openai.OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        # Educational models and settings
        self.primary_model = "deepseek/deepseek-chat"
        self.fallback_model = "meta-llama/llama-3.1-70b-instruct"
        
        # Initialize educational knowledge
        self.educational_context = self._load_educational_context()
        self.subject_experts = self._initialize_subject_experts()
        
        # Analytics and learning tracking
        self.conversation_analyzer = ConversationAnalyzer()
        self.learning_tracker = LearningProgressTracker()
    
    def _load_educational_context(self) -> Dict:
        """Load educational context and curriculum standards"""
        return {
            "teaching_principles": [
                "Use Socratic method to encourage critical thinking",
                "Provide step-by-step explanations",
                "Use analogies and real-world examples",
                "Adapt difficulty to student level",
                "Encourage and motivate students",
                "Check for understanding before proceeding",
                "Connect new concepts to prior knowledge"
            ],
            "learning_objectives": {
                "mathematics": ["Problem solving", "Logical reasoning", "Pattern recognition"],
                "science": ["Scientific method", "Critical analysis", "Evidence-based thinking"],
                "language_arts": ["Communication", "Reading comprehension", "Writing skills"],
                "history": ["Historical analysis", "Cause and effect", "Cultural understanding"],
                "computer_science": ["Algorithmic thinking", "Debugging", "System design"]
            },
            "common_misconceptions": {
                "mathematics": [
                    "Believing that correlation implies causation",
                    "Thinking that larger numbers are always greater (decimals)",
                    "Confusion between area and perimeter"
                ],
                "science": [
                    "Thinking heavier objects fall faster",
                    "Believing that heat and temperature are the same",
                    "Misconception about evolution being 'just a theory'"
                ]
            }
        }
    
    def _initialize_subject_experts(self) -> Dict:
        """Initialize subject-specific AI personalities"""
        return {
            "mathematics": {
                "personality": "analytical",
                "approach": "step_by_step",
                "specialties": ["algebra", "geometry", "calculus", "statistics"]
            },
            "science": {
                "personality": "curious",
                "approach": "experimental", 
                "specialties": ["physics", "chemistry", "biology", "earth_science"]
            },
            "programming": {
                "personality": "logical",
                "approach": "problem_solving",
                "specialties": ["python", "javascript", "algorithms", "data_structures"]
            },
            "language_arts": {
                "personality": "creative",
                "approach": "expressive",
                "specialties": ["writing", "literature", "grammar", "communication"]
            }
        }
    
    async def start_conversation(self, user: User, session_type: str = "tutoring", 
                                subject: str = "", topic: str = "") -> ChatSession:
        """Start a new tutoring conversation"""
        try:
            # Create new chat session
            session = ChatSession.objects.create(
                user=user,
                session_type=session_type,
                subject=subject.lower() if subject else "",
                topic=topic,
                status='active'
            )
            
            # Get user's learning pattern
            learning_pattern = getattr(user, 'learning_pattern', None)
            
            # Select appropriate tutor personality
            personality = self._select_tutor_personality(subject, learning_pattern)
            
            # Generate personalized greeting
            greeting = await self._generate_greeting(user, session, personality)
            
            # Create greeting message
            ChatMessage.objects.create(
                session=session,
                message_type='ai_tutor',
                content_type='text',
                content=greeting,
                order=0,
                model_used=self.primary_model
            )
            
            # Initialize analytics
            ConversationAnalytics.objects.create(
                session=session,
                engagement_score=1.0,  # High initial engagement
                coherence_score=1.0
            )
            
            logger.info(f"Started conversation session {session.id} for user {user.id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise
    
    def _select_tutor_personality(self, subject: str, learning_pattern = None) -> TutorPersonality:
        """Select the most appropriate tutor personality"""
        try:
            # Get available personalities
            personalities = TutorPersonality.objects.filter(is_active=True)
            
            if subject and subject in self.subject_experts:
                # Filter by subject specialization
                subject_personalities = personalities.filter(
                    specialized_subjects__contains=[subject]
                )
                if subject_personalities.exists():
                    personalities = subject_personalities
            
            # Consider learning pattern if available
            if learning_pattern:
                if learning_pattern.learning_style == 'visual':
                    personalities = personalities.filter(use_examples=True)
                elif learning_pattern.difficulty_preference == 'slow':
                    personalities = personalities.filter(patience_level__gte=4)
                elif learning_pattern.difficulty_preference == 'fast':
                    personalities = personalities.filter(teaching_style='analytical')
            
            # Select the most suitable personality
            selected = personalities.first()
            
            # Fallback to default if none found
            if not selected:
                selected, created = TutorPersonality.objects.get_or_create(
                    name="Default Tutor",
                    defaults={
                        'description': "Friendly and adaptive AI tutor",
                        'personality_type': 'friendly',
                        'teaching_style': 'adaptive',
                        'formality_level': 3,
                        'patience_level': 4,
                        'use_examples': True,
                        'use_analogies': True
                    }
                )
            
            return selected
            
        except Exception as e:
            logger.error(f"Error selecting personality: {e}")
            # Return minimal default
            return TutorPersonality(
                name="Emergency Tutor",
                personality_type='friendly',
                teaching_style='adaptive'
            )
    
    async def _generate_greeting(self, user: User, session: ChatSession, 
                               personality: TutorPersonality) -> str:
        """Generate personalized greeting message"""
        try:
            # Get user context
            user_name = user.first_name or "there"
            subject = session.subject or "learning"
            
            # Build context for AI
            context = {
                "user_name": user_name,
                "subject": subject,
                "personality_type": personality.personality_type,
                "teaching_style": personality.teaching_style,
                "session_type": session.session_type
            }
            
            # Get recent performance if available
            recent_progress = StudentProgress.objects.filter(
                student=user
            ).order_by('-created_at')[:3]
            
            performance_context = ""
            if recent_progress:
                avg_score = sum(p.completion_percentage for p in recent_progress) / len(recent_progress)
                if avg_score > 80:
                    performance_context = "I see you've been doing excellent work lately! "
                elif avg_score > 60:
                    performance_context = "You've been making good progress in your studies. "
                else:
                    performance_context = "I'm here to help you succeed in your learning journey. "
            
            # Generate greeting using AI
            system_prompt = f"""You are an AI tutor with a {personality.personality_type} personality and {personality.teaching_style} teaching style.
            Generate a warm, encouraging greeting for a student named {user_name} who is starting a {session.session_type} session about {subject}.
            
            Keep it concise (2-3 sentences), personalied, and motivating. {performance_context}
            
            Ask an engaging question to understand what they need help with today."""
            
            response = await self._call_ai_model(
                system_prompt=system_prompt,
                user_message="Generate a greeting message",
                max_tokens=150,
                temperature=0.7
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            # Fallback greeting
            user_name = user.first_name or "there"
            return f"Hi {user_name}! I'm your AI tutor and I'm here to help you learn. What would you like to work on today?"
    
    async def process_message(self, session: ChatSession, user_message: str) -> ChatMessage:
        """Process user message and generate intelligent response"""
        start_time = time.time()
        
        try:
            # Create user message record
            user_msg = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content_type='text',
                content=user_message,
                order=session.message_count,
            )
            
            # Increment message count
            session.message_count += 1
            session.save()
            
            # Analyze user message
            message_analysis = await self._analyze_user_message(user_message, session)
            
            # Get conversation context
            context = await self._build_conversation_context(session)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(
                user_message, context, message_analysis, session
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Create AI response message
            ai_msg = ChatMessage.objects.create(
                session=session,
                message_type='ai_tutor',
                content_type=message_analysis.get('content_type', 'text'),
                content=ai_response['content'],
                order=session.message_count,
                model_used=ai_response['model_used'],
                response_time=response_time,
                confidence_score=ai_response.get('confidence', 0.8),
                tokens_used=ai_response.get('tokens_used', 0),
                concepts_mentioned=message_analysis.get('concepts', []),
                educational_value=message_analysis.get('educational_value', 0.5)
            )
            
            # Update session
            session.message_count += 1
            session.last_activity = timezone.now()
            if message_analysis.get('subject'):
                session.subject = message_analysis['subject']
            if message_analysis.get('topic'):
                session.topic = message_analysis['topic']
            session.save()
            
            # Update analytics
            await self._update_conversation_analytics(session, message_analysis)
            
            # Track learning progress
            await self.learning_tracker.update_progress(session.user, message_analysis)
            
            # Store question pattern for future improvement
            await self._store_question_pattern(user_message, message_analysis, ai_response)
            
            logger.info(f"Processed message in session {session.id} in {response_time:.2f}s")
            return ai_msg
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Generate fallback response
            fallback_msg = ChatMessage.objects.create(
                session=session,
                message_type='ai_tutor',
                content_type='text',
                content="I apologize, but I'm having trouble processing your message right now. Could you please rephrase your question?",
                order=session.message_count,
                model_used="fallback",
                response_time=time.time() - start_time
            )
            
            session.message_count += 1
            session.save()
            
            return fallback_msg
    
    async def _analyze_user_message(self, message: str, session: ChatSession) -> Dict:
        """Analyze user message for intent, subject, difficulty, etc."""
        try:
            analysis = {
                'content_type': 'text',
                'concepts': [],
                'subject': '',
                'topic': '',
                'difficulty_level': 'medium',
                'question_type': 'general',
                'educational_value': 0.5,
                'sentiment': 'neutral',
                'urgency': 'normal'
            }
            
            # Basic content type detection
            if any(keyword in message.lower() for keyword in ['code', 'program', 'function', 'algorithm']):
                analysis['content_type'] = 'code'
            elif any(keyword in message.lower() for keyword in ['formula', 'equation', 'calculate']):
                analysis['content_type'] = 'math'
            
            # Subject detection
            subjects = {
                'math': ['math', 'algebra', 'geometry', 'calculus', 'statistics', 'equation', 'formula'],
                'science': ['physics', 'chemistry', 'biology', 'experiment', 'atom', 'molecule'],
                'programming': ['code', 'python', 'javascript', 'programming', 'function', 'variable'],
                'english': ['grammar', 'writing', 'essay', 'literature', 'poem', 'story'],
                'history': ['history', 'historical', 'war', 'ancient', 'medieval', 'revolution']
            }
            
            message_lower = message.lower()
            for subject, keywords in subjects.items():
                if any(keyword in message_lower for keyword in keywords):
                    analysis['subject'] = subject
                    break
            
            # If no subject detected from session
            if not analysis['subject'] and session.subject:
                analysis['subject'] = session.subject
            
            # Question type classification
            if '?' in message:
                if any(word in message_lower for word in ['what', 'define', 'explain', 'meaning']):
                    analysis['question_type'] = 'definition'
                elif any(word in message_lower for word in ['how', 'steps', 'process']):
                    analysis['question_type'] = 'procedure'
                elif any(word in message_lower for word in ['why', 'because', 'reason']):
                    analysis['question_type'] = 'explanation'
                elif any(word in message_lower for word in ['solve', 'answer', 'calculate']):
                    analysis['question_type'] = 'problem_solving'
            
            # Sentiment analysis using TextBlob
            try:
                blob = TextBlob(message)
                sentiment_score = blob.sentiment.polarity
                if sentiment_score > 0.1:
                    analysis['sentiment'] = 'positive'
                elif sentiment_score < -0.1:
                    analysis['sentiment'] = 'negative'
                else:
                    analysis['sentiment'] = 'neutral'
            except:
                analysis['sentiment'] = 'neutral'
            
            # Difficulty assessment
            complex_indicators = ['complex', 'advanced', 'difficult', 'challenging', 'sophisticated']
            simple_indicators = ['basic', 'simple', 'easy', 'beginner', 'introduction']
            
            if any(word in message_lower for word in complex_indicators):
                analysis['difficulty_level'] = 'hard'
            elif any(word in message_lower for word in simple_indicators):
                analysis['difficulty_level'] = 'easy'
            
            # Urgency detection
            urgent_indicators = ['urgent', 'asap', 'quickly', 'deadline', 'due', 'exam', 'test tomorrow']
            if any(word in message_lower for word in urgent_indicators):
                analysis['urgency'] = 'high'
            
            # Educational value assessment
            educational_indicators = ['learn', 'understand', 'study', 'practice', 'explain', 'teach']
            if any(word in message_lower for word in educational_indicators):
                analysis['educational_value'] = 0.8
            elif '?' in message:
                analysis['educational_value'] = 0.7
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return {
                'content_type': 'text',
                'concepts': [],
                'subject': session.subject or '',
                'difficulty_level': 'medium',
                'question_type': 'general',
                'educational_value': 0.5,
                'sentiment': 'neutral'
            }
    
    async def _build_conversation_context(self, session: ChatSession) -> Dict:
        """Build conversation context for AI response generation"""
        try:
            # Get recent messages (last 10)
            recent_messages = ChatMessage.objects.filter(
                session=session
            ).order_by('-order')[:10]
            
            # Build conversation history
            conversation_history = []
            for msg in reversed(recent_messages):
                role = "user" if msg.message_type == 'user' else "assistant"
                conversation_history.append({
                    "role": role,
                    "content": msg.content
                })
            
            # Get user learning pattern
            user_pattern = getattr(session.user, 'learning_pattern', None)
            
            # Get tutor personality
            personality = self._select_tutor_personality(session.subject, user_pattern)
            
            # Build educational context
            subject_context = ""
            if session.subject:
                knowledge_items = KnowledgeBase.objects.filter(
                    subjects__contains=[session.subject]
                )[:3]
                if knowledge_items:
                    subject_context = "\\n".join([f"- {item.title}: {item.content[:200]}..." 
                                               for item in knowledge_items])
            
            context = {
                "conversation_history": conversation_history,
                "session_info": {
                    "type": session.session_type,
                    "subject": session.subject,
                    "topic": session.topic,
                    "message_count": session.message_count
                },
                "user_info": {
                    "name": session.user.first_name or "Student",
                    "learning_style": user_pattern.learning_style if user_pattern else "adaptive",
                    "difficulty_preference": user_pattern.difficulty_preference if user_pattern else "moderate"
                },
                "tutor_personality": {
                    "type": personality.personality_type,
                    "teaching_style": personality.teaching_style,
                    "formality_level": personality.formality_level,
                    "use_examples": personality.use_examples,
                    "use_analogies": personality.use_analogies
                },
                "educational_context": subject_context,
                "learning_objectives": self.educational_context.get("learning_objectives", {}).get(session.subject, [])
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return {
                "conversation_history": [],
                "session_info": {"type": "tutoring", "subject": "", "topic": ""},
                "user_info": {"name": "Student"},
                "tutor_personality": {"type": "friendly", "teaching_style": "adaptive"}
            }
    
    async def _generate_ai_response(self, user_message: str, context: Dict, 
                                  analysis: Dict, session: ChatSession) -> Dict:
        """Generate intelligent AI tutor response"""
        try:
            # Build system prompt based on context
            system_prompt = self._build_system_prompt(context, analysis)
            
            # Add conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history
            if context.get("conversation_history"):
                messages.extend(context["conversation_history"][-6:])  # Last 6 messages
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using AI
            response = await self._call_ai_model(
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            # Post-process response
            processed_response = self._post_process_response(response, analysis, context)
            
            return {
                "content": processed_response,
                "model_used": self.primary_model,
                "confidence": 0.85,
                "tokens_used": len(response.split()) * 1.3  # Rough estimate
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            
            # Try fallback response
            try:
                fallback_response = await self._generate_fallback_response(user_message, analysis)
                return {
                    "content": fallback_response,
                    "model_used": "fallback",
                    "confidence": 0.6,
                    "tokens_used": 50
                }
            except:
                return {
                    "content": "I understand you're asking about this topic. Let me think about the best way to explain it to you. Could you provide a bit more context about what specifically you'd like to learn?",
                    "model_used": "emergency_fallback",
                    "confidence": 0.3,
                    "tokens_used": 30
                }
    
    def _build_system_prompt(self, context: Dict, analysis: Dict) -> str:
        """Build comprehensive system prompt for AI tutor"""
        personality = context.get("tutor_personality", {})
        user_info = context.get("user_info", {})
        session_info = context.get("session_info", {})
        
        prompt = f"""You are an expert AI tutor with a {personality.get('type', 'friendly')} personality and {personality.get('teaching_style', 'adaptive')} teaching approach.

STUDENT CONTEXT:
- Name: {user_info.get('name', 'Student')}
- Learning style: {user_info.get('learning_style', 'adaptive')}
- Difficulty preference: {user_info.get('difficulty_preference', 'moderate')}

SESSION CONTEXT:
- Type: {session_info.get('type', 'tutoring')}
- Subject: {session_info.get('subject', 'general')}
- Topic: {session_info.get('topic', 'various')}

TEACHING PRINCIPLES:
1. Use the Socratic method - ask guiding questions to help the student discover answers
2. Provide step-by-step explanations for complex topics
3. Use real-world examples and analogies when helpful
4. Adapt your language to the student's level
5. Be encouraging and supportive
6. Check for understanding before moving to new concepts
7. Connect new information to what the student already knows

RESPONSE GUIDELINES:
- Keep responses focused and educational (200-400 words max)
- Ask follow-up questions to assess understanding
- Provide examples when explaining concepts
- Use encouraging language
- If the student seems confused, break down concepts further
- Suggest practice problems or exercises when appropriate

CURRENT ANALYSIS:
- Question type: {analysis.get('question_type', 'general')}
- Difficulty level: {analysis.get('difficulty_level', 'medium')}
- Student sentiment: {analysis.get('sentiment', 'neutral')}
- Content type: {analysis.get('content_type', 'text')}

Educational context: {context.get('educational_context', '')}

Remember: You are a tutor, not just an answer provider. Guide the student's learning process."""

        return prompt
    
    async def _call_ai_model(self, system_prompt: str = None, user_message: str = None, 
                           messages: List[Dict] = None, max_tokens: int = 500, 
                           temperature: float = 0.7) -> str:
        """Call AI model with error handling and retries"""
        try:
            if messages is None:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            
            # Call primary model
            response = self.openai_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            
            try:
                # Try fallback model
                response = self.openai_client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=30
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                raise Exception("All AI models unavailable")
    
    def _post_process_response(self, response: str, analysis: Dict, context: Dict) -> str:
        """Post-process AI response for better educational value"""
        try:
            # Add encouraging elements if student seems frustrated
            if analysis.get('sentiment') == 'negative':
                if not any(word in response.lower() for word in ['understand', 'don\'t worry', 'it\'s okay']):
                    response = "I understand this can be challenging. " + response
            
            # Add follow-up questions for engagement
            if analysis.get('question_type') == 'definition' and '?' not in response:
                response += "\\n\\nDoes this explanation make sense to you? Would you like me to provide an example?"
            
            # Format mathematical expressions (basic LaTeX-like formatting)
            if analysis.get('content_type') == 'math':
                # This is a simplified example - in production, you'd use proper math formatting
                response = re.sub(r'\\b(x|y|z)\\^(\\d+)', r'\\1^{\\2}', response)
            
            # Ensure response ends with engagement
            if not response.strip().endswith(('?', '!', '.')):
                response += "."
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error post-processing response: {e}")
            return response
    
    async def _generate_fallback_response(self, user_message: str, analysis: Dict) -> str:
        """Generate fallback response when AI models are unavailable"""
        try:
            # Use knowledge base for common questions
            if analysis.get('subject'):
                knowledge_items = KnowledgeBase.objects.filter(
                    subjects__contains=[analysis['subject']]
                ).order_by('-usage_count')[:1]
                
                if knowledge_items:
                    item = knowledge_items[0]
                    item.usage_count += 1
                    item.save()
                    return f"Based on my knowledge about {analysis['subject']}: {item.content}\\n\\nWould you like me to elaborate on any part of this?"
            
            # Question type-based responses
            if analysis.get('question_type') == 'definition':
                return "I'd be happy to help you understand this concept. Could you tell me more specifically what you'd like me to define or explain?"
            elif analysis.get('question_type') == 'procedure':
                return "I can walk you through this step by step. Let me break down the process for you. What specific part would you like me to start with?"
            elif analysis.get('question_type') == 'problem_solving':
                return "Let's work through this problem together. Can you show me what you've tried so far, or would you like me to guide you through the approach?"
            
            # Default fallback
            return "I'm here to help you learn! Could you provide a bit more detail about what you're working on so I can give you the best guidance possible?"
            
        except Exception as e:
            logger.error(f"Error generating fallback: {e}")
            return "I want to help you with your question. Could you please rephrase it or provide more context?"
    
    async def _update_conversation_analytics(self, session: ChatSession, analysis: Dict):
        """Update conversation analytics based on message analysis"""
        try:
            analytics, created = ConversationAnalytics.objects.get_or_create(
                session=session,
                defaults={
                    'engagement_score': 0.5,
                    'coherence_score': 0.5,
                    'learning_progress': 0.0
                }
            )
            
            # Update engagement score based on sentiment and question quality
            if analysis.get('sentiment') == 'positive':
                analytics.engagement_score = min(1.0, analytics.engagement_score + 0.1)
            elif analysis.get('sentiment') == 'negative':
                analytics.engagement_score = max(0.0, analytics.engagement_score - 0.05)
            
            # Update learning progress based on question types
            if analysis.get('question_type') in ['definition', 'procedure', 'problem_solving']:
                analytics.learning_progress = min(1.0, analytics.learning_progress + 0.05)
            
            # Track concepts
            if analysis.get('concepts'):
                if not analytics.concepts_mastered:
                    analytics.concepts_mastered = []
                analytics.concepts_mastered.extend(analysis['concepts'])
                analytics.concepts_mastered = list(set(analytics.concepts_mastered))  # Remove duplicates
            
            analytics.save()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def _store_question_pattern(self, user_message: str, analysis: Dict, ai_response: Dict):
        """Store question patterns for continuous improvement"""
        try:
            # Normalize the question
            normalized = re.sub(r'[^\w\s]', '', user_message.lower()).strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Check if similar pattern exists
            pattern, created = StudentQuestionPattern.objects.get_or_create(
                normalized_question=normalized[:200],  # Limit length
                defaults={
                    'question_text': user_message,
                    'question_type': analysis.get('question_type', 'general'),
                    'subject_area': analysis.get('subject', 'general'),
                    'difficulty_level': analysis.get('difficulty_level', 'medium'),
                    'keywords': analysis.get('concepts', []),
                    'frequency': 1
                }
            )
            
            if not created:
                # Update existing pattern
                pattern.frequency += 1
                pattern.save()
            
        except Exception as e:
            logger.error(f"Error storing question pattern: {e}")
    
    async def end_session(self, session: ChatSession, user_feedback: Dict = None):
        """End tutoring session and generate summary"""
        try:
            session.end_session()
            
            # Generate session summary using AI
            messages = ChatMessage.objects.filter(session=session).order_by('order')
            
            if messages.count() > 1:
                conversation_text = "\\n".join([
                    f"{'Student' if msg.message_type == 'user' else 'Tutor'}: {msg.content}"
                    for msg in messages
                ])
                
                summary_prompt = f"""Summarize this tutoring session in 2-3 sentences, highlighting:
                1. Main topics covered
                2. Student's learning progress
                3. Areas that may need more work
                
                Conversation:
                {conversation_text[:2000]}"""
                
                try:
                    summary = await self._call_ai_model(
                        system_prompt="You are an educational analyst creating session summaries.",
                        user_message=summary_prompt,
                        max_tokens=150
                    )
                    session.summary = summary
                    session.save()
                except:
                    session.summary = f"Session covered {session.subject or 'various topics'} with {messages.count()} messages exchanged."
                    session.save()
            
            # Update user feedback if provided
            if user_feedback:
                session.user_satisfaction = user_feedback.get('rating')
                session.save()
                
                # Update last message with feedback
                last_ai_message = messages.filter(message_type='ai_tutor').last()
                if last_ai_message:
                    last_ai_message.user_rating = user_feedback.get('message_rating')
                    last_ai_message.feedback_notes = user_feedback.get('notes', '')
                    last_ai_message.save()
            
            logger.info(f"Ended session {session.id} with {messages.count()} messages")
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")


class ConversationAnalyzer:
    """Analyze conversation quality and learning outcomes"""
    
    def analyze_learning_progress(self, session: ChatSession) -> Dict:
        """Analyze learning progress from conversation"""
        try:
            messages = ChatMessage.objects.filter(session=session).order_by('order')
            
            if not messages:
                return {"progress": 0.0, "insights": []}
            
            # Analyze question complexity progression
            user_messages = messages.filter(message_type='user')
            complexity_scores = []
            
            for msg in user_messages:
                # Simple complexity analysis
                score = 0.0
                content_lower = msg.content.lower()
                
                # Question indicators
                if '?' in msg.content:
                    score += 0.2
                
                # Concept words
                concept_words = ['why', 'how', 'explain', 'difference', 'relationship', 'compare']
                score += sum(0.1 for word in concept_words if word in content_lower)
                
                # Advanced vocabulary
                advanced_words = ['analyze', 'synthesize', 'evaluate', 'hypothesize']
                score += sum(0.15 for word in advanced_words if word in content_lower)
                
                complexity_scores.append(min(1.0, score))
            
            # Calculate progress
            if len(complexity_scores) > 1:
                progress = (complexity_scores[-1] - complexity_scores[0])
            else:
                progress = 0.0
            
            # Generate insights
            insights = []
            if progress > 0.2:
                insights.append("Student shows increasing complexity in questions")
            if len([msg for msg in user_messages if 'thank' in msg.content.lower()]) > 0:
                insights.append("Student expressed gratitude - positive engagement")
            
            return {
                "progress": max(0.0, min(1.0, progress + 0.5)),
                "insights": insights,
                "complexity_trend": complexity_scores
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning progress: {e}")
            return {"progress": 0.5, "insights": [], "complexity_trend": []}


class LearningProgressTracker:
    """Track and update student learning progress"""
    
    async def update_progress(self, user: User, message_analysis: Dict):
        """Update learning progress based on conversation analysis"""
        try:
            # Get or create learning pattern
            pattern, created = LearningPattern.objects.get_or_create(
                user=user,
                defaults={
                    'learning_style': 'visual',
                    'difficulty_preference': 'moderate'
                }
            )
            
            # Update subject scores
            if message_analysis.get('subject') and message_analysis.get('educational_value', 0) > 0.6:
                subject = message_analysis['subject']
                if not pattern.subject_scores:
                    pattern.subject_scores = {}
                
                current_score = pattern.subject_scores.get(subject, 70.0)
                improvement = message_analysis['educational_value'] * 10
                new_score = min(100.0, current_score + improvement)
                pattern.subject_scores[subject] = new_score
            
            # Update total study time (estimate)
            pattern.total_study_time += 5  # Assume 5 minutes per interaction
            
            # Update help-seeking behavior
            if message_analysis.get('question_type') in ['definition', 'explanation', 'procedure']:
                # This indicates active learning
                pattern.lessons_completed += 1
            
            pattern.save()
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {e}")


# Global tutor instance
intelligent_tutor = IntelligentTutor()
