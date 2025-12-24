from flask import Blueprint, request, jsonify
import os
import requests

chat_bp = Blueprint('chat', __name__)

# Groq API configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@chat_bp.route('/message', methods=['POST'])
def chat_message():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': 'Please type a message 😊'})
    
    print(f"DEBUG: User message: {user_message}")
    
    if GROQ_API_KEY:
        try:
            system_prompt = """You are MediBook AI Assistant — a friendly and concise medical advisor.

Rules:
- Be warm, empathetic, and brief
- Reply to greetings simply (e.g., "Hi! How can I help?")
- For symptoms: Give 3–4 short bullet points max
- Always include safe home tips and red flags
- End with a short recommendation to book a doctor
- Keep total response under 150 words

Example for back pain:
• Common causes: muscle strain, poor posture, stress
• Try: rest, gentle stretches, heat/ice, ibuprofen
• See doctor if: pain down leg, numbness, or >2 weeks
• Book an orthopedist via our Search feature!"""

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 250
            }
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result['choices'][0]['message']['content'].strip()
                return jsonify({'response': ai_reply})
            
            print(f"Groq error: {response.status_code} {response.text}")
            
        except Exception as e:
            print(f"Groq exception: {e}")
    
    # Fallback when Groq is unavailable
    lower = user_message.lower()
    if any(g in lower for g in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
        return jsonify({'response': 'Hello! 👋 How can I help you today?'})
    
    return jsonify({'response': "I'm having trouble connecting right now. For health concerns, please book an appointment with a specialist using our 'Find Your Doctor' feature!"})
