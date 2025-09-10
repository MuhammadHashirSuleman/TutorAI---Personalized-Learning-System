import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter API to access DeepSeek and Llama models"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Your site URL
            "X-Title": "AI Learning System",  # Your site name
        }
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OpenRouter API
        
        Args:
            model: Model name (deepseek/deepseek-chat or meta-llama/llama-3.1-70b-instruct)
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            API response dictionary
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise
    
    async def generate_learning_recommendation(
        self,
        student_profile: Dict[str, Any],
        learning_history: List[Dict[str, Any]],
        model: str = "deepseek/deepseek-chat"
    ) -> Dict[str, Any]:
        """Generate personalized learning recommendations"""
        
        prompt = f"""
        You are an AI learning assistant. Based on the following student profile and learning history, 
        provide personalized learning recommendations.

        Student Profile:
        - Learning Style: {student_profile.get('learning_style', 'Not specified')}
        - Grade Level: {student_profile.get('grade_level', 'Not specified')}
        - Strengths: {', '.join(student_profile.get('strengths', []))}
        - Weaknesses: {', '.join(student_profile.get('weaknesses', []))}
        - Learning Goals: {student_profile.get('learning_goals', 'Not specified')}

        Recent Learning History:
        {json.dumps(learning_history, indent=2)}

        Please provide:
        1. Recommended topics to focus on
        2. Suggested learning resources
        3. Study schedule recommendations
        4. Areas that need improvement
        5. Motivational tips

        Format your response as a structured JSON with the following keys:
        - recommended_topics
        - suggested_resources
        - study_schedule
        - improvement_areas
        - motivational_tips
        """
        
        messages = [
            {"role": "system", "content": "You are an expert AI tutor specializing in personalized learning recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        try:
            content = response['choices'][0]['message']['content']
            # Try to parse JSON response
            recommendations = json.loads(content)
            return recommendations
        except (json.JSONDecodeError, KeyError):
            # Fallback to structured text parsing
            return {"raw_response": content}
    
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: str,
        question_count: int = 5,
        question_types: List[str] = None,
        model: str = "meta-llama/llama-3.1-70b-instruct"
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions for a specific topic"""
        
        if question_types is None:
            question_types = ["multiple_choice", "true_false", "short_answer"]
        
        prompt = f"""
        Generate {question_count} quiz questions about "{topic}" at {difficulty} difficulty level.
        
        Question types to include: {', '.join(question_types)}
        
        Format each question as a JSON object with:
        - question: the question text
        - type: question type (multiple_choice, true_false, short_answer)
        - options: list of options (for multiple choice)
        - correct_answer: the correct answer
        - explanation: brief explanation of the correct answer
        - difficulty: difficulty level
        - topic: the topic
        
        Return a JSON array of question objects.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert educator creating high-quality quiz questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            max_tokens=1500,
            temperature=0.5
        )
        
        try:
            content = response['choices'][0]['message']['content']
            questions = json.loads(content)
            return questions
        except (json.JSONDecodeError, KeyError):
            return []
    
    async def chat_with_tutor(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        student_context: Dict[str, Any],
        model: str = "deepseek/deepseek-chat"
    ) -> str:
        """Chat with AI tutor"""
        
        system_prompt = f"""
        You are an AI tutor helping a student learn. Here's the student context:
        - Learning Style: {student_context.get('learning_style', 'Not specified')}
        - Current Subjects: {', '.join(student_context.get('subjects', []))}
        - Strengths: {', '.join(student_context.get('strengths', []))}
        - Areas for improvement: {', '.join(student_context.get('weaknesses', []))}
        
        Guidelines:
        - Be encouraging and supportive
        - Adapt explanations to the student's learning style
        - Use examples and analogies when helpful
        - Ask clarifying questions when needed
        - Provide step-by-step explanations for complex topics
        - Keep responses concise but thorough
        """
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        
        try:
            return response['choices'][0]['message']['content']
        except KeyError:
            return "I'm sorry, I'm having trouble responding right now. Please try again."
    
    async def analyze_learning_pattern(
        self,
        performance_data: List[Dict[str, Any]],
        model: str = "deepseek/deepseek-chat"
    ) -> Dict[str, Any]:
        """Analyze learning patterns from performance data"""
        
        prompt = f"""
        Analyze the following learning performance data and identify patterns, strengths, and areas for improvement:

        Performance Data:
        {json.dumps(performance_data, indent=2)}

        Please provide analysis in JSON format with:
        - learning_patterns: identified patterns in learning behavior
        - strengths: areas where the student excels
        - weaknesses: areas needing improvement
        - recommendations: specific actionable recommendations
        - progress_trend: overall progress trend (improving/stable/declining)
        - confidence_score: confidence in the analysis (0-100)
        """
        
        messages = [
            {"role": "system", "content": "You are an AI learning analyst specializing in educational data analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.3
        )
        
        try:
            content = response['choices'][0]['message']['content']
            analysis = json.loads(content)
            return analysis
        except (json.JSONDecodeError, KeyError):
            return {"raw_analysis": content}

# Create a global instance
openrouter_client = OpenRouterClient()
