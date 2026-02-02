#!/usr/bin/env python3
"""
DNA Lifesong Studio - Backend Server
Flask server for DNA music generation and MusicAPI integration
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import secrets
import time
from datetime import datetime
from functools import wraps
from collections import defaultdict

from dna_processor import DNAProcessor
from musicapi_client import MusicAPIClient

# Configuration
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

# Use /tmp on Railway, Desktop folder locally
if os.environ.get('RAILWAY_ENVIRONMENT'):
    OUTPUT_DIR = "/tmp/DNA_Lifesong"
else:
    OUTPUT_DIR = os.path.expanduser("~/Desktop/DNA_Lifesong")

# Version
VERSION = "3.3.0"

# Security Configuration
# Set your allowed domain when deploying (e.g., 'https://lifesong.railway.app')
_origins = os.environ.get('ALLOWED_ORIGINS', 'http://127.0.0.1:8080,http://localhost:8080')
ALLOWED_ORIGINS = [origin.strip() for origin in _origins.split(',') if origin.strip()]

# User Access Key - master key for all users to access the app
# Set via environment variable in production
USER_ACCESS_KEY = os.environ.get('LIFESONG_USER_KEY', None)

# Your MusicAPI key - stored securely on the server, users never see this
# IMPORTANT: Set this via environment variable in production!
MUSICAPI_KEY = os.environ.get('MUSICAPI_KEY', None)

# Rate limiting: max requests per IP per minute
RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 30))
rate_limit_store = defaultdict(list)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

# Strict CORS - only allow specific origins
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# Initialize processors
dna_processor = DNAProcessor()
musicapi_client = MusicAPIClient()


# ==================== Security Middleware ====================

def check_rate_limit(ip):
    """Check if IP has exceeded rate limit"""
    now = time.time()
    minute_ago = now - 60

    # Clean old entries
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if t > minute_ago]

    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return False

    rate_limit_store[ip].append(now)
    return True


def require_user_key(f):
    """Decorator to require user access key for protected endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip key check if not configured (for local development)
        if USER_ACCESS_KEY is None:
            return f(*args, **kwargs)

        # Check header or query param
        provided_key = request.headers.get('X-User-Key') or request.args.get('user_key')

        if not provided_key or provided_key != USER_ACCESS_KEY:
            return jsonify({'success': False, 'error': 'Invalid or missing access key'}), 401

        return f(*args, **kwargs)
    return decorated


def rate_limited(f):
    """Decorator to apply rate limiting"""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr

        if not check_rate_limit(ip):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please wait a moment.'
            }), 429

        return f(*args, **kwargs)
    return decorated


# ==================== Static File Routes ====================

@app.route('/')
def serve_index():
    """Serve the Egg UI as the main page"""
    return send_from_directory(FRONTEND_DIR, 'egg-ui.html')


@app.route('/classic')
def serve_classic_ui():
    """Serve the original/classic UI"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory(FRONTEND_DIR, path)


# ==================== API Routes ====================

@app.route('/api/health', methods=['GET'])
@rate_limited
def api_health():
    """Health check endpoint"""
    return jsonify({
        'healthy': True,
        'version': VERSION,
        'output_dir': OUTPUT_DIR
    })


@app.route('/api/validate-key', methods=['POST'])
@rate_limited
def api_validate_key():
    """Validate user access key"""
    # If no key is configured on server, allow any non-empty key (dev mode)
    if USER_ACCESS_KEY is None:
        provided_key = request.headers.get('X-User-Key') or ''
        return jsonify({'valid': len(provided_key) > 0})

    # Check if provided key matches
    provided_key = request.headers.get('X-User-Key') or ''
    is_valid = provided_key == USER_ACCESS_KEY

    return jsonify({'valid': is_valid})


@app.route('/api/generate', methods=['POST'])
@require_user_key
@rate_limited
def api_generate():
    """Generate MIDI and MP3 from DNA sequence"""
    try:
        data = request.json
        dna = data.get('dna', '')
        duration = data.get('duration', 45)

        # Validate input
        if not dna:
            return jsonify({'success': False, 'error': 'No DNA sequence provided'}), 400

        if len(dna) < 20:
            return jsonify({'success': False, 'error': 'Need at least 20 DNA bases'}), 400

        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        midi_path = os.path.join(OUTPUT_DIR, f'dna_{timestamp}.mid')
        mp3_path = os.path.join(OUTPUT_DIR, f'dna_{timestamp}.mp3')

        # Generate MIDI
        analysis = dna_processor.generate_midi(dna, duration, midi_path)

        # Convert to MP3
        success = dna_processor.convert_to_mp3(midi_path, mp3_path)

        if success:
            # Clean analysis for JSON (remove non-serializable items)
            clean_analysis = {
                'key': analysis.get('key', 'C'),
                'mode': analysis.get('mode', 'aeolian'),
                'character': analysis.get('character', 'reflective'),
                'tempo': analysis.get('tempo', 72),
                'gc': round(analysis.get('gc', 50.0), 1),
                'at_gc_ratio': analysis.get('at_gc_ratio', 1.0),
                'pu_py_ratio': analysis.get('pu_py_ratio', 1.0),
                'codon_count': analysis.get('codon_count', 0),
                'motif_count': analysis.get('motif_count', 0),
                'length': analysis.get('length', 0),
            }
            return jsonify({
                'success': True,
                'analysis': clean_analysis,
                'mp3_path': mp3_path,
                'filename': os.path.basename(mp3_path)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'MP3 conversion failed. Make sure timidity is installed.'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/audio/<filename>')
@rate_limited
def api_audio(filename):
    """Serve audio files from output directory"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        print(f"Serving audio: {file_path}, exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='audio/mpeg')
        else:
            # List files in output dir for debugging
            files = os.listdir(OUTPUT_DIR) if os.path.exists(OUTPUT_DIR) else []
            print(f"Available files: {files}")
            return jsonify({'error': 'File not found', 'requested': filename, 'available': files[:10]}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
@require_user_key
@rate_limited
def api_upload():
    """Upload MP3 to Catbox and register with MusicAPI"""
    try:
        # Check if MusicAPI key is configured
        if not MUSICAPI_KEY:
            return jsonify({'success': False, 'error': 'MusicAPI not configured on server'}), 500

        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({'success': False, 'error': 'Missing file_path'}), 400

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        # Upload to Catbox and MusicAPI using server's key
        result = musicapi_client.upload(file_path, MUSICAPI_KEY)

        if result.get('clip_id'):
            return jsonify({'success': True, 'clip_id': result['clip_id']})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Upload failed')}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/create_cover', methods=['POST'])
@require_user_key
@rate_limited
def api_create_cover():
    """Create AI cover using MusicAPI"""
    try:
        # Check if MusicAPI key is configured
        if not MUSICAPI_KEY:
            return jsonify({'success': False, 'error': 'MusicAPI not configured on server'}), 500

        data = request.json
        clip_id = data.get('clip_id')
        prompt = data.get('prompt')
        tags = data.get('tags', 'ambient, electronic')

        if not all([clip_id, prompt]):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        result = musicapi_client.create_cover(clip_id, prompt, tags, MUSICAPI_KEY)

        if result.get('task_id'):
            return jsonify({'success': True, 'task_id': result['task_id']})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Cover creation failed')}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check_cover', methods=['POST'])
@require_user_key
@rate_limited
def api_check_cover():
    """Check cover generation status"""
    try:
        # Check if MusicAPI key is configured
        if not MUSICAPI_KEY:
            return jsonify({'success': False, 'error': 'MusicAPI not configured on server'}), 500

        data = request.json
        task_id = data.get('task_id')

        if not task_id:
            return jsonify({'success': False, 'error': 'Missing task_id'}), 400

        result = musicapi_client.check_status(task_id, MUSICAPI_KEY)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
@require_user_key
@rate_limited
def api_download():
    """Download generated cover from URL"""
    try:
        data = request.json
        audio_url = data.get('audio_url')

        if not audio_url:
            return jsonify({'success': False, 'error': 'No audio_url provided'}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'cover_{timestamp}.mp3'
        output_path = os.path.join(OUTPUT_DIR, filename)

        success = musicapi_client.download_audio(audio_url, output_path)

        if success:
            return jsonify({
                'success': True,
                'path': output_path,
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'error': 'Download failed'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download-file/<filename>')
@rate_limited
def api_download_file(filename):
    """Download a generated audio file to user's device"""
    try:
        # Security: only allow .mp3 and .mid files, no path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400

        if not filename.endswith(('.mp3', '.mid')):
            return jsonify({'error': 'Invalid file type'}), 400

        file_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(file_path):
            return send_file(
                file_path,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Main ====================

if __name__ == '__main__':
    # Use Railway's PORT or default to 8080 for local dev
    port = int(os.environ.get('PORT', 8080))
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') is not None

    print("=" * 50)
    print(f"🧬 DNA LIFESONG STUDIO v{VERSION}")
    print("=" * 50)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🌐 Server: http://127.0.0.1:{port}")
    print("=" * 50)
    print("\n🔒 Security Status:")
    print(f"   CORS: {ALLOWED_ORIGINS}")
    print(f"   User Key: {'ENABLED' if USER_ACCESS_KEY else 'DISABLED (dev mode)'}")
    print(f"   MusicAPI: {'CONFIGURED' if MUSICAPI_KEY else 'NOT SET (covers disabled)'}")
    print(f"   Rate Limit: {RATE_LIMIT} req/min per IP")
    print("=" * 50)

    if is_production:
        print("\n🚀 Running in PRODUCTION mode\n")
        app.run(debug=False, port=port, host='0.0.0.0')
    else:
        print(f"\nOpen your browser to: http://127.0.0.1:{port}\n")
        app.run(debug=True, port=port, host='0.0.0.0')
