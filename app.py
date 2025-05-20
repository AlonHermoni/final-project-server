from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import threading
import time
from algorithms.melody_matcher import MelodyMatcher

# Import our modules
from api.room_routes import room_routes
from socket.events import socketio

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize melody matcher
melody_matcher = MelodyMatcher()

# Initialize SocketIO with the app
socketio.init_app(app, cors_allowed_origins="*")

# Register blueprint for room routes
app.register_blueprint(room_routes, url_prefix='/api/room')

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Piano Game Server!',
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

# Background task for cleaning up inactive rooms
def cleanup_task():
    """Background task to clean up inactive rooms"""
    from game.manager import room_manager
    
    while True:
        # Sleep for 60 seconds
        time.sleep(60)
        
        # Cleanup inactive rooms
        room_manager.cleanup_inactive_rooms()

if __name__ == '__main__':
    # Start the cleanup background task
    cleanup_thread = threading.Thread(target=cleanup_task)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    # Run the server with SocketIO
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True) 