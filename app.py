import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from nlp_engine import FAQChatbotNLP

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize NLP engine
bot_engine = FAQChatbotNLP(faq_file_path="data/faqs.json")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty"}), 400

    match_res = bot_engine.match_query(query)
    return jsonify({
        "success": True,
        "result": match_res
    })

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    category_filter = request.args.get('category')
    faqs = bot_engine.faqs
    if category_filter and category_filter != "All":
        faqs = [f for f in faqs if f.get('category') == category_filter]
    
    categories = sorted(list(set(f.get('category', 'General') for f in bot_engine.faqs)))
    return jsonify({
        "success": True,
        "count": len(faqs),
        "categories": categories,
        "faqs": faqs
    })

@app.route('/api/faqs', methods=['POST'])
def add_faq():
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    category = data.get('category', 'General').strip()

    if not question or not answer:
        return jsonify({"success": False, "error": "Question and Answer are required."}), 400

    added_faq = bot_engine.add_faq({
        "question": question,
        "answer": answer,
        "category": category,
        "keywords": data.get('keywords', ''),
        "tags": data.get('tags', '')
    })

    return jsonify({
        "success": True,
        "message": "FAQ added successfully!",
        "faq": added_faq
    })

@app.route('/api/feedback', methods=['POST'])
def record_feedback():
    data = request.get_json() or {}
    faq_id = data.get('faq_id')
    rating = data.get('rating') # 'positive' or 'negative'
    comment = data.get('comment', '')

    feedback = bot_engine.record_feedback(faq_id, rating, comment)
    return jsonify({
        "success": True,
        "message": "Thank you for your feedback!",
        "feedback": feedback
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_feedback = len(bot_engine.feedback_list)
    pos_feedback = sum(1 for f in bot_engine.feedback_list if f.get('rating') == 'positive')
    feedback_percentage = round((pos_feedback / total_feedback * 100), 1) if total_feedback > 0 else 100.0

    return jsonify({
        "success": True,
        "stats": {
            "total_faqs": len(bot_engine.faqs),
            "total_queries": bot_engine.stats["total_queries"],
            "avg_confidence": bot_engine.stats["avg_confidence"],
            "high_confidence_matches": bot_engine.stats["high_confidence_matches"],
            "medium_confidence_matches": bot_engine.stats["medium_confidence_matches"],
            "low_confidence_matches": bot_engine.stats["low_confidence_matches"],
            "positive_feedback_rate": feedback_percentage,
            "total_feedbacks": total_feedback
        }
    })

import sys
import io
import socket

# Ensure UTF-8 output encoding for Windows terminal
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

def find_available_port(start_port=5000):
    for port in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

if __name__ == '__main__':
    port = find_available_port(5000)
    print(f"NovaBot Server starting at http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=False)
