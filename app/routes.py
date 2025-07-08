import os
import shutil
import json
import whisper
import numpy as np
import requests
from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator

from .models import db, Transcript, Vocabulary

main_routes = Blueprint('main', __name__)

# loads OpenAi Whisper Model
whisper_model = None
print("Loading AI models...")
try:
    device = "cpu"
    whisper_model = whisper.load_model("base", device=device)
    print(f"Whisper model loaded successfully on device: {device}.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load Whisper model on {device}: {e}")
    whisper_model = None

def clean_whisper_result(data):
    """Recursively cleans numpy data types from Whisper's output for JSON serialization."""
    if isinstance(data, dict):
        return {k: clean_whisper_result(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_whisper_result(i) for i in data]
    if isinstance(data, (np.float32, np.float64)):
        return float(data)
    if isinstance(data, (np.int32, np.int64)):
        return int(data)
    return data


@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(current_app.config['AUDIO_LIBRARY_FOLDER'], filename)

@main_routes.route('/api/transcripts', methods=['GET', 'POST'])
def handle_transcripts():
    if request.method == 'GET':
        transcripts = Transcript.query.order_by(Transcript.id.desc()).all()
        return jsonify([t.to_dict() for t in transcripts])

    if request.method == 'POST':
        if not whisper_model:
            return jsonify({"error": "Transcription service is unavailable: Model not loaded."}), 503

        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        original_filename = secure_filename(file.filename)
        temp_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], original_filename)
        file.save(temp_filepath)

        try:
            audio_for_model = AudioSegment.from_file(temp_filepath).set_channels(1).set_frame_rate(16000)
            audio_data = np.frombuffer(audio_for_model.raw_data, np.int16).flatten().astype(np.float32) / 32768.0
            result = whisper_model.transcribe(audio_data, word_timestamps=True, language="de")
            cleaned_result = clean_whisper_result(result)

            original_base, original_ext = os.path.splitext(original_filename)
            new_transcript = Transcript(
                title=original_base,
                audio_filename="placeholder",
                transcript_json=json.dumps(cleaned_result)
            )
            db.session.add(new_transcript)
            db.session.flush()

            permanent_filename = f"{new_transcript.id}_{original_base}{original_ext}"
            permanent_filepath = os.path.join(current_app.config['AUDIO_LIBRARY_FOLDER'], permanent_filename)
            shutil.move(temp_filepath, permanent_filepath)

            new_transcript.audio_filename = permanent_filename
            db.session.commit()

            return jsonify(new_transcript.to_dict()), 201

        except CouldntDecodeError:
             return jsonify({"error": "Could not decode audio file. Please use a standard format like MP3, WAV, or M4A."}), 415
        except Exception as e:
            db.session.rollback()
            print(f"ERROR during transcription/saving: {e}")
            return jsonify({"error": "An internal error occurred during transcription."}), 500
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

@main_routes.route('/api/transcripts/<int:transcript_id>', methods=['GET', 'DELETE'])
def handle_transcript_detail(transcript_id):
    transcript = db.get_or_404(Transcript, transcript_id, description='Transcript not found')

    if request.method == 'GET':
        detail = transcript.to_dict()
        detail['transcript_data'] = json.loads(transcript.transcript_json)
        return jsonify(detail)

    if request.method == 'DELETE':
        try:
            audio_filepath = os.path.join(current_app.config['AUDIO_LIBRARY_FOLDER'], transcript.audio_filename)
            if os.path.exists(audio_filepath):
                os.remove(audio_filepath)
            
            db.session.delete(transcript)
            db.session.commit()
            return jsonify({'message': 'Transcript deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"ERROR during transcript deletion: {e}")
            return jsonify({'error': 'Failed to delete transcript due to an internal error'}), 500

@main_routes.route('/api/vocabulary', methods=['GET', 'POST'])
def handle_vocabulary():
    if request.method == 'GET':
        return jsonify([word.to_dict() for word in Vocabulary.query.order_by(Vocabulary.german).all()])

    if request.method == 'POST':
        data = request.get_json()
        if not data or 'german' not in data or 'english' not in data:
            return jsonify({'error': 'Missing required data: german and english fields'}), 400

        if Vocabulary.query.filter(Vocabulary.german.ilike(data['german'])).first():
            return jsonify({'error': 'Word already exists in vocabulary'}), 409

        new_word = Vocabulary(
            german=data['german'],
            english=data['english'],
            gender=data.get('gender'),
            details_json=json.dumps(data.get('details'))
        )
        db.session.add(new_word)
        db.session.commit()
        return jsonify(new_word.to_dict()), 201

@main_routes.route('/api/vocabulary/<int:word_id>', methods=['DELETE'])
def delete_from_vocabulary(word_id):
    word = db.get_or_404(Vocabulary, word_id, description='Word not found in vocabulary')
    db.session.delete(word)
    db.session.commit()
    return jsonify({'message': 'Word deleted successfully'}), 200

@main_routes.route('/api/dictionary_lookup', methods=['POST'])
def dictionary_lookup():
    data = request.get_json()
    word = data.get('word')
    if not word:
        return jsonify({"error": "No word provided"}), 400

    try:
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/de/{word}"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        api_data = response.json()
        first_entry = api_data[0]

        primary_translation = "N/A"
        if first_entry.get('meanings'):
            for meaning in first_entry['meanings']:
                if meaning.get('definitions'):
                    primary_translation = meaning['definitions'][0]['definition'].split(';')[0].split(',')[0]
                    break
        
        gender = None
        if first_entry.get('meanings', [{}])[0].get('partOfSpeech') == 'noun':
            phonetic_texts = [p.get('text', '').lower() for p in first_entry.get('phonetics', [])]
            for text in phonetic_texts:
                if 'dɛr ' in text or 'deːr ' in text:
                    gender = 'der'
                    break
                elif 'diː ' in text:
                    gender = 'die'
                    break
                elif 'das ' in text:
                    gender = 'das'
                    break

        return jsonify({
            "original": word,
            "primary_translation": primary_translation,
            "gender": gender,
            "details": api_data
        })
    except requests.exceptions.HTTPError:
        try:
            translated_text = GoogleTranslator(source='de', target='en').translate(word)
            return jsonify({"original": word, "primary_translation": translated_text, "gender": None, "details": None})
        except Exception as trans_err:
            print(f"Fallback translator failed for '{word}': {trans_err}")
            return jsonify({"error": "Word not found and fallback translation failed."}), 404
    except Exception as e:
        print(f"An unexpected error occurred during dictionary lookup for '{word}': {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
