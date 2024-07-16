from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import tempfile
import json

app = Flask(__name__)
CORS(app)

openai.api_key = 'Your-Open-AI-Key'  # Ersetzen Sie dies durch Ihren tatsächlichen API-Schlüssel

SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        app.logger.error('No audio file provided')
        return jsonify({'error': 'No audio file provided'}), 400

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

        prompt = f"""
Hier ist der transkribierte Text:

{text}

Analysiere den Text und fülle die folgenden Felder entsprechend aus. Wenn eine Information nicht vorhanden ist, setze sie auf "nicht gegeben". Gib das Ergebnis als gültiges JSON zurück.

{{
"Titel": "{{{{title}}}}",
"Autor": "{{{{author}}}}",
"Veröffentlichungsdatum": "{{{{date}}}}",
"Genre": "{{{{genre}}}}",
"ISBN": "{{{{isbn}}}}",
"Tags": "{{{{tags}}}}",
"Zusammenfassung": "{{{{summary}}}}",
"Persönliche Bedeutung": "{{{{personal_impact}}}}",
"Wichtige Zitate": ["{{{{quote1}}}}", "{{{{quote2}}}}", "{{{{quote3}}}}"],
"Notizen": ["{{{{note1}}}}", "{{{{note2}}}}", "{{{{note3}}}}"]
}}
"""


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

        gpt_text = gpt_response['choices'][0]['message']['content']
        
        try:
            gpt_text = gpt_text.strip().replace('json:', '').strip()
            json_response = json.loads(gpt_text)
        except (json.JSONDecodeError, ValueError) as e:
            app.logger.error('Error decoding JSON: %s', str(e))
            app.logger.error('GPT-3.5 Turbo response: %s', gpt_text)
            return jsonify({'error': 'Error decoding JSON from GPT-3.5 Turbo response'}), 500

        # Convert JSON response to Markdown
        markdown_content = convert_to_markdown(json_response)
        
        return jsonify({"markdown_data": markdown_content})

    except openai.error.OpenAIError as e:
        app.logger.error('OpenAI error: %s', str(e))
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error('Unexpected error: %s', str(e))
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500

def convert_to_markdown(data):
    markdown = f"# {data.get('Titel', 'Titel nicht gegeben')}\n\n"
    markdown += f"**Autor:** {data.get('Autor', 'Nicht gegeben')}\n\n"
    markdown += f"**Veröffentlichungsdatum:** {data.get('Veröffentlichungsdatum', 'Nicht gegeben')}\n\n"
    markdown += f"**Genre:** {data.get('Genre', 'Nicht gegeben')}\n\n"
    markdown += f"**ISBN:** {data.get('ISBN', 'Nicht gegeben')}\n\n"
    markdown += f"**Tags:** {data.get('Tags', 'Nicht gegeben')}\n\n"
    markdown += f"## Zusammenfassung\n\n{data.get('Zusammenfassung', 'Nicht gegeben')}\n\n"
    markdown += f"## Persönliche Bedeutung\n\n{data.get('Persönliche Bedeutung', 'Nicht gegeben')}\n\n"
    markdown += "## Wichtige Zitate\n\n"
    for quote in data.get('Wichtige Zitate', []):
        markdown += f"- {quote}\n"
    markdown += "\n## Notizen\n\n"
    for note in data.get('Notizen', []):
        markdown += f"- {note}\n"
    return markdown

if __name__ == '__main__':
    app.run(debug=True, port=5000)
