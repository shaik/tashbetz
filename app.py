from flask import Flask, render_template, request, jsonify
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change')

# Cache for Hebrew words
hebrew_words = None

def load_hebrew_words():
    """Load Hebrew words from the dictionary file."""
    global hebrew_words
    if hebrew_words is None:
        try:
            with open('hebrew_words.txt', 'r', encoding='utf-8') as f:
                hebrew_words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            hebrew_words = []
    return hebrew_words

def find_matching_words(pattern, words):
    """Find words that match the given pattern."""
    # Convert pattern to regex (replace empty spaces with . for any character)
    regex_pattern = ''.join('.' if c == ' ' else re.escape(c) for c in pattern)
    regex = re.compile(f'^{regex_pattern}$')
    return [word for word in words if regex.match(word)]

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/find_words', methods=['POST'])
def find_words():
    """API endpoint to find matching words."""
    data = request.get_json()
    pattern = data.get('pattern', '')
    length = data.get('length', 0)
    
    # Load words and filter by length
    words = load_hebrew_words()
    words = [word for word in words if len(word) == length]
    
    # Find matches
    matching_words = find_matching_words(pattern, words)
    return jsonify({'words': matching_words})

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development') 