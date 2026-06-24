"""Endpoint czatu — oparty na API Anthropic Claude."""

from flask import Blueprint, request, jsonify
from app.claude import generate_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'Wiadomość użytkownika nie może być pusta.'}), 400

    try:
        reply = generate_response(user_message, history)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': f"Błąd serwera backendu: {str(e)}"}), 500
