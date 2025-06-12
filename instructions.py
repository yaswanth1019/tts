import io
from flask import Flask, request, send_file, jsonify
from gtts import gTTS
import tempfile
import os

app = Flask(__name__)

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tts = gTTS(text=text, lang='en')
        tts.save(tf.name)
        temp_path = tf.name

    with open(temp_path, 'rb') as f:
        audio_bytes = f.read()
    os.remove(temp_path)

    return send_file(
        io.BytesIO(audio_bytes),
        mimetype='audio/mpeg',
        as_attachment=False,
        download_name='tts.mp3'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
