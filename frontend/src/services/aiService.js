// AI Service for DeepSeek V3.1 API Integration
class AIService {
  constructor() {
    // Debug: Check if environment variables are loaded
    console.log('Environment check:');
    console.log('DEEPSEEK KEY:', process.env.REACT_APP_DEEPSEEK_API_KEY ? 'Found' : 'Not found');
    console.log('LLAMA KEY:', process.env.REACT_APP_LLAMA_API_KEY ? 'Found' : 'Not found');
    
    // Multi-model AI configuration
    this.models = {
      deepseek: {
        apiUrl: 'https://openrouter.ai/api/v1/chat/completions',
        apiKey: process.env.REACT_APP_DEEPSEEK_API_KEY || 'your-deepseek-api-key',
        model: 'deepseek/deepseek-chat',
        name: 'DeepSeek V3.1'
      },
      llama: {
        apiUrl: 'https://openrouter.ai/api/v1/chat/completions',
        apiKey: process.env.REACT_APP_LLAMA_API_KEY || 'your-llama-api-key',
        model: 'meta-llama/llama-3.3-70b-instruct',
        name: 'Llama 3.3 70B Instruct'
      }
    };
    this.currentModel = 'deepseek'; // Default to DeepSeek
    this.maxTokens = 2048;
    this.temperature = 0.7;
  }

  async sendMessage(message, context = [], userProfile = null, preferredModel = null) {
    // Use preferred model or fallback to current model
    const modelToUse = preferredModel || this.currentModel;
    const modelConfig = this.models[modelToUse];
    
    try {
      // Prepare the system message with educational context
      const systemMessage = this.createSystemMessage(userProfile, modelConfig.name);
      
      // Prepare conversation history
      const messages = [
        systemMessage,
        ...context.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        {
          role: 'user',
          content: message
        }
      ];

      // Clean API key (remove quotes if present)
      const cleanApiKey = modelConfig.apiKey?.replace(/["']/g, '');
      
      const response = await fetch(modelConfig.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${cleanApiKey}`,
          'HTTP-Referer': window.location.origin,
          'X-Title': 'AI Learning System',
        },
        body: JSON.stringify({
          model: modelConfig.model,
          messages: messages,
          max_tokens: this.maxTokens,
          temperature: this.temperature,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.choices && data.choices.length > 0) {
        return {
          success: true,
          message: data.choices[0].message.content,
          usage: data.usage
        };
      } else {
        throw new Error('No response from AI');
      }
    } catch (error) {
      console.error('AI Service Error:', error);
      
      // Fallback response when API is not available
      // Try fallback model if primary fails
      if (modelToUse === 'deepseek' && this.validateApiKey('llama')) {
        console.log('DeepSeek failed, trying Llama as fallback...');
        return this.sendMessage(message, context, userProfile, 'llama');
      } else if (modelToUse === 'llama' && this.validateApiKey('deepseek')) {
        console.log('Llama failed, trying DeepSeek as fallback...');
        return this.sendMessage(message, context, userProfile, 'deepseek');
      }
      
      // Both models failed, use fallback response
      return {
        success: false,
        message: this.getFallbackResponse(message),
        error: error.message,
        model: modelConfig.name
      };
    }
  }

  createSystemMessage(userProfile, modelName = 'AI Assistant') {
    const basePrompt = `You are an intelligent AI tutor designed to help students learn effectively. Your name is TutorAI Assistant powered by ${modelName}. You should:

1. Provide clear, accurate, and helpful educational content
2. Break down complex topics into understandable parts
3. Use examples and analogies to explain difficult concepts
4. Encourage critical thinking and problem-solving
5. Be patient and supportive in your responses
6. Offer additional resources when appropriate
7. Ask follow-up questions to ensure understanding
8. Adapt your teaching style to the student's level

Guidelines:
- Always be encouraging and positive
- Provide step-by-step explanations for complex problems
- Use markdown formatting for better readability
- Include relevant examples and practical applications
- Suggest related topics for deeper learning
- Be concise but comprehensive in your explanations`;

    if (userProfile) {
      const profileInfo = `

Student Profile:
- Name: ${userProfile.firstName} ${userProfile.lastName}
- Education Level: ${userProfile.educationLevel || 'Not specified'}
- Primary Subject Interest: ${userProfile.primarySubject || 'General'}
- Learning Goal: Personalized tutoring and academic support

Adjust your responses to match their education level and subject interests.`;
      
      return {
        role: 'system',
        content: basePrompt + profileInfo
      };
    }

    return {
      role: 'system',
      content: basePrompt
    };
  }

  getFallbackResponse(message) {
    const fallbackResponses = {
      greeting: [
        "Hello! I'm your AI tutor. I'm here to help you learn and understand various topics. What would you like to explore today?",
        "Hi there! I'm excited to help you with your learning journey. What subject or topic interests you?",
        "Welcome! I'm your AI learning assistant. Feel free to ask me about any academic topic you'd like to understand better."
      ],
      math: [
        "I'd love to help you with mathematics! Whether it's algebra, calculus, geometry, or statistics, I can break down complex problems step by step. What specific math topic are you working on?",
        "Mathematics is a fascinating subject! I can help you understand concepts, solve problems, and see the practical applications. What mathematical concept would you like to explore?"
      ],
      science: [
        "Science is amazing! I can help you understand physics, chemistry, biology, and more. I love explaining scientific concepts with real-world examples. What scientific topic interests you?",
        "Let's explore the wonders of science together! Whether it's understanding chemical reactions, physical laws, or biological processes, I'm here to help clarify any concepts."
      ],
      programming: [
        "Programming is a valuable skill! I can help you understand coding concepts, debug issues, explain algorithms, and guide you through different programming languages. What programming topic are you curious about?",
        "Code is poetry! I can help you with programming languages, data structures, algorithms, debugging, and best practices. What coding challenge are you facing?"
      ],
      general: [
        "I'm here to help you learn! I can assist with a wide range of subjects including mathematics, science, programming, languages, history, and more. What would you like to explore?",
        "Learning is a journey, and I'm here to guide you! Whether you need help understanding a concept, solving a problem, or exploring new topics, feel free to ask. What's on your mind?",
        "I'm your AI tutor, ready to help with any academic subject or learning challenge. I can explain concepts, provide examples, and help you understand complex topics. What would you like to learn about?"
      ]
    };

    // Simple keyword matching for fallback responses
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
      return this.getRandomResponse(fallbackResponses.greeting);
    } else if (lowerMessage.includes('math') || lowerMessage.includes('algebra') || lowerMessage.includes('calculus')) {
      return this.getRandomResponse(fallbackResponses.math);
    } else if (lowerMessage.includes('science') || lowerMessage.includes('physics') || lowerMessage.includes('chemistry') || lowerMessage.includes('biology')) {
      return this.getRandomResponse(fallbackResponses.science);
    } else if (lowerMessage.includes('code') || lowerMessage.includes('program') || lowerMessage.includes('javascript') || lowerMessage.includes('python')) {
      return this.getRandomResponse(fallbackResponses.programming);
    } else {
      return this.getRandomResponse(fallbackResponses.general);
    }
  }

  getRandomResponse(responses) {
    return responses[Math.floor(Math.random() * responses.length)];
  }

  // Method to get suggested questions based on user's field
  getSuggestedQuestions(userField) {
    const suggestions = {
      'computer-science': [
        "Can you explain object-oriented programming?",
        "What's the difference between arrays and linked lists?",
        "How do sorting algorithms work?",
        "Explain the concept of recursion with examples",
        "What are the principles of good software design?"
      ],
      'mathematics': [
        "Can you help me understand derivatives?",
        "Explain the Pythagorean theorem",
        "How do I solve quadratic equations?",
        "What are complex numbers?",
        "Can you explain probability distributions?"
      ],
      'science': [
        "How do chemical bonds form?",
        "Explain Newton's laws of motion",
        "What is photosynthesis?",
        "How does the periodic table work?",
        "Explain the theory of evolution"
      ],
      'business': [
        "What are the 4 P's of marketing?",
        "Explain supply and demand",
        "How do you calculate ROI?",
        "What is a business model canvas?",
        "Explain different leadership styles"
      ],
      'languages': [
        "How can I improve my grammar?",
        "What are the best ways to expand vocabulary?",
        "Explain the difference between active and passive voice",
        "How do I write a compelling essay?",
        "What are common pronunciation mistakes?"
      ],
      'arts': [
        "Explain color theory in art",
        "What are the elements of composition?",
        "How has art evolved through different periods?",
        "What makes a good creative writing piece?",
        "Explain different music scales"
      ]
    };

    return suggestions[userField] || suggestions['computer-science'];
  }

  // Method to switch between models
  setModel(modelKey) {
    if (this.models[modelKey] && this.validateApiKey(modelKey)) {
      this.currentModel = modelKey;
      return true;
    }
    return false;
  }

  // Method to get current model info
  getCurrentModel() {
    return {
      key: this.currentModel,
      name: this.models[this.currentModel].name,
      model: this.models[this.currentModel].model
    };
  }

  // Method to get available models
  getAvailableModels() {
    const available = [];
    Object.keys(this.models).forEach(key => {
      if (this.validateApiKey(key)) {
        available.push({
          key,
          name: this.models[key].name,
          model: this.models[key].model
        });
      }
    });
    return available;
  }

  // Method to validate API key for specific model
  validateApiKey(modelKey = null) {
    const modelToCheck = modelKey || this.currentModel;
    const modelConfig = this.models[modelToCheck];
    
    if (!modelConfig) {
      console.log(`Model config not found for: ${modelToCheck}`);
      return false;
    }
    
    // Clean the API key (remove quotes if present)
    const apiKey = modelConfig.apiKey?.replace(/["']/g, '');
    
    console.log(`Validating ${modelToCheck} API key:`, apiKey ? `${apiKey.substring(0, 15)}...` : 'Not found');
    
    const isValid = apiKey && 
           apiKey !== 'your-deepseek-api-key' && 
           apiKey !== 'your-llama-api-key' &&
           apiKey !== 'sk-your-actual-deepseek-api-key-here' &&
           apiKey !== 'your-deepseek-api-key-here' &&
           apiKey.length > 20 &&
           apiKey.startsWith('sk-or-v1-');
           
    console.log(`${modelToCheck} API key valid:`, isValid);
    return isValid;
  }

  // Method to get API status
  async getApiStatus() {
    const deepseekValid = this.validateApiKey('deepseek');
    const llamaValid = this.validateApiKey('llama');
    
    if (!deepseekValid && !llamaValid) {
      return {
        status: 'offline',
        message: 'No AI models configured. Add your DeepSeek and/or Llama API keys to .env file to enable AI capabilities.'
      };
    }

    try {
      // Test API with a simple request
      const response = await this.sendMessage("Hello", []);
      const availableModels = [];
      if (deepseekValid) availableModels.push('DeepSeek V3.1');
      if (llamaValid) availableModels.push('Llama 3.3 70B');
      
      return {
        status: response.success ? 'connected' : 'partial',
        message: response.success 
          ? `AI Tutor connected with ${availableModels.join(' and ')}`
          : `${availableModels.join(' and ')} available but connection issues detected`,
        models: availableModels
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message,
        models: []
      };
    }
  }
}

const aiService = new AIService();
export default aiService;
