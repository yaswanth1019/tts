import io
from flask import Flask, request, send_file, jsonify
import pyttsx3
import tempfile
import os

app = Flask(__name__)
engine = pyttsx3.init()

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        temp_path = tf.name

    engine.save_to_file(text, temp_path)
    engine.runAndWait()

    if not os.path.exists(temp_path):
        return jsonify({"error": "TTS generation failed"}), 500

    with open(temp_path, 'rb') as f:
        audio_bytes = f.read()
    os.remove(temp_path)

    return send_file(
        io.BytesIO(audio_bytes),
        mimetype='audio/wav',
        as_attachment=False,
        download_name='tts.wav'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

