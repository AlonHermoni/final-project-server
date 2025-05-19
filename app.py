from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from algorithms.melody_matcher import MelodyMatcher

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize melody matcher
melody_matcher = MelodyMatcher()

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Flask Server!',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/api/compare-melodies', methods=['POST'])
def compare_melodies():
    try:
        data = request.get_json()
        
        if not data or 'melody1' not in data or 'melody2' not in data:
            return jsonify({
                'error': 'Missing required fields: melody1 and melody2'
            }), 400

        melody1 = data['melody1']  # Target melody
        melody2 = data['melody2']  # Played melody
        
        # Optional timing and duration data
        timings1 = data.get('timings1')  # Target note onset times
        timings2 = data.get('timings2')  # Played note onset times
        durations1 = data.get('durations1')  # Target note durations
        durations2 = data.get('durations2')  # Played note durations

        # Validate input
        if not isinstance(melody1, list) or not isinstance(melody2, list):
            return jsonify({
                'error': 'Melodies must be lists of integers'
            }), 400
            
        # Validate timing data if provided
        if timings1 and not isinstance(timings1, list):
            return jsonify({'error': 'timings1 must be a list of numbers'}), 400
        if timings2 and not isinstance(timings2, list):
            return jsonify({'error': 'timings2 must be a list of numbers'}), 400
            
        # Validate duration data if provided
        if durations1 and not isinstance(durations1, list):
            return jsonify({'error': 'durations1 must be a list of numbers'}), 400
        if durations2 and not isinstance(durations2, list):
            return jsonify({'error': 'durations2 must be a list of numbers'}), 400
            
        # Validate lengths
        if timings1 and len(timings1) != len(melody1):
            return jsonify({'error': 'timings1 must have the same length as melody1'}), 400
        if timings2 and len(timings2) != len(melody2):
            return jsonify({'error': 'timings2 must have the same length as melody2'}), 400
        if durations1 and len(durations1) != len(melody1):
            return jsonify({'error': 'durations1 must have the same length as melody1'}), 400
        if durations2 and len(durations2) != len(melody2):
            return jsonify({'error': 'durations2 must have the same length as melody2'}), 400

        # Compare melodies with all available data
        result = melody_matcher.compare_melodies(
            melody1, 
            melody2,
            timings1=timings1,
            timings2=timings2,
            durations1=durations1,
            durations2=durations2
        )
        
        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/estimate-difficulty', methods=['POST'])
def estimate_difficulty():
    try:
        data = request.get_json()
        
        if not data or 'melody' not in data:
            return jsonify({
                'error': 'Missing required field: melody'
            }), 400

        melody = data['melody']

        # Validate input
        if not isinstance(melody, list):
            return jsonify({
                'error': 'Melody must be a list of integers'
            }), 400

        # Estimate difficulty
        result = melody_matcher.get_difficulty_estimate(melody)
        
        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 