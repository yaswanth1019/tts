import io
import os
import tempfile
from flask import Flask, request, send_file, jsonify
from gtts import gTTS
from pydub import AudioSegment
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "").strip()
        lang = data.get("lang", "en")
        speed = data.get("speed", 1.0)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        app.logger.info(f"TTS Request: '{text}' (lang: {lang}, speed: {speed})")

        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
            mp3_path = mp3_file.name
            
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = wav_file.name

        try:
            # Generate TTS with gTTS
            tts = gTTS(text=text, lang=lang, slow=(speed < 0.8))
            tts.save(mp3_path)
            
            # Convert MP3 to WAV using pydub
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Adjust speed if needed
            if speed != 1.0:
                # Speed up/slow down audio
                new_sample_rate = int(audio.frame_rate * speed)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(22050)  # Normalize to common sample rate
            
            # Export as WAV (16-bit, mono for Unity compatibility)
            audio = audio.set_channels(1)  # Convert to mono
            audio = audio.set_sample_width(2)  # 16-bit
            audio.export(wav_path, format="wav")
            
            # Read WAV file and return
            with open(wav_path, 'rb') as f:
                wav_data = f.read()
                
            app.logger.info(f"Generated WAV: {len(wav_data)} bytes")
            
            return send_file(
                io.BytesIO(wav_data),
                mimetype='audio/wav',
                as_attachment=False,
                download_name='tts.wav'
            )
            
        finally:
            # Clean up temporary files
            for path in [mp3_path, wav_path]:
                if os.path.exists(path):
                    os.remove(path)
                    
    except Exception as e:
        app.logger.error(f"TTS Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "TTS Server"})

@app.route('/languages', methods=['GET'])
def get_supported_languages():
    # Return commonly supported gTTS languages
    languages = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
    }
    return jsonify(languages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
