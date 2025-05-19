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

        melody1 = data['melody1']
        melody2 = data['melody2']
        
        # Optional parameters
        durations1 = data.get('durations1')
        durations2 = data.get('durations2')
        custom_weights = data.get('weights')
        include_letter_grade = data.get('include_letter_grade', False)

        # Validate input
        if not isinstance(melody1, list) or not isinstance(melody2, list):
            return jsonify({
                'error': 'Melodies must be lists of integers'
            }), 400
            
        # Validate durations if provided
        if durations1 and not isinstance(durations1, list):
            return jsonify({'error': 'durations1 must be a list of numbers'}), 400
        if durations2 and not isinstance(durations2, list):
            return jsonify({'error': 'durations2 must be a list of numbers'}), 400
        
        # Validate custom weights if provided
        if custom_weights and not isinstance(custom_weights, dict):
            return jsonify({'error': 'weights must be a dictionary'}), 400

        # Compare melodies
        result = melody_matcher.compare_melodies(
            melody1, 
            melody2, 
            durations1=durations1, 
            durations2=durations2, 
            custom_weights=custom_weights
        )
        
        # Add letter grade if requested
        if include_letter_grade:
            result['letter_grade'] = melody_matcher.get_letter_grade(result['final_score'])
        
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
        
@app.route('/api/transpose-melody', methods=['POST'])
def transpose_melody():
    try:
        data = request.get_json()
        
        if not data or 'melody' not in data or 'semitones' not in data:
            return jsonify({
                'error': 'Missing required fields: melody and semitones'
            }), 400

        melody = data['melody']
        semitones = data['semitones']

        # Validate input
        if not isinstance(melody, list):
            return jsonify({
                'error': 'Melody must be a list of integers'
            }), 400
            
        if not isinstance(semitones, int):
            return jsonify({
                'error': 'semitones must be an integer'
            }), 400

        # Transpose melody
        result = melody_matcher.transpose_melody(melody, semitones)
        
        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/compare-piano-notes', methods=['POST'])
def compare_piano_notes():
    try:
        data = request.get_json()
        
        if not data or 'target_notes' not in data or 'played_notes' not in data:
            return jsonify({
                'error': 'Missing required fields: target_notes and played_notes'
            }), 400

        target_notes = data['target_notes']
        played_notes = data['played_notes']

        # Validate input
        if not isinstance(target_notes, list) or not isinstance(played_notes, list):
            return jsonify({
                'error': 'Notes must be lists of integers'
            }), 400

        # Compare notes using binary matching
        result = melody_matcher.binary_note_match(target_notes, played_notes)
        
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