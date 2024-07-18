from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import tempfile
import json

app = Flask(__name__)
CORS(app)

openai.api_key = 'your-open-ai-key'  # Ersetzen Sie dies durch Ihren tatsächlichen API-Schlüssel

TEMPLATE_DIR = '..\mktemplates'  # Verzeichnis für die Templates
SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

@app.route('/templates', methods=['GET'])
def list_templates():
    templates = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.md')]
    return jsonify({'templates': templates})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        app.logger.error('No audio file provided')
        return jsonify({'error': 'No audio file provided'}), 400

    if 'template' not in request.form:
        app.logger.error('No template selected')
        return jsonify({'error': 'No template selected'}), 400

    template_name = request.form['template']
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    if not os.path.isfile(template_path):
        app.logger.error('Template not found: %s', template_name)
        return jsonify({'error': 'Template not found'}), 400

    audio_file = request.files['audio']
    file_ext = audio_file.filename.split('.')[-1].lower()

    if file_ext not in SUPPORTED_FORMATS:
        app.logger.error('Unsupported file format: %s', file_ext)
        return jsonify({'error': f'Unsupported file format: {file_ext}. Supported formats: {SUPPORTED_FORMATS}'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as temp_audio_file:
            temp_audio_file.write(audio_file.read())
            temp_audio_file_path = temp_audio_file.name

        with open(temp_audio_file_path, 'rb') as file_for_transcription:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=file_for_transcription,
                language="de"
            )

        os.remove(temp_audio_file_path)

        if 'text' not in response:
            app.logger.error('No text in response from OpenAI API')
            return jsonify({'error': 'No text in response from OpenAI API'}), 500

        text = response['text']

        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        prompt = f"bitte schaue dir dieses template an: {template_content} jetzt ersetze die ganzen gefragten daten mithilfe dieser angegebenen daten: {text}"

        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        if not gpt_response or 'choices' not in gpt_response or not gpt_response['choices']:
            app.logger.error('No choices in response from GPT-3.5 Turbo API')
            return jsonify({'error': 'No choices in response from GPT-3.5 Turbo API'}), 500

        filled_template = gpt_response['choices'][0]['message']['content']
        
        return jsonify({"filled_template": filled_template})

    except openai.error.OpenAIError as e:
        app.logger.error('OpenAI error: %s', str(e))
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', str(e))
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
