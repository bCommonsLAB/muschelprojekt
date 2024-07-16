# Audio Transkription

![image](https://github.com/user-attachments/assets/7891002e-f2fe-4ac0-af7e-ec8b2f3853c8)


## Überblick
Diese Anwendung ermöglicht das Hochladen und Transkribieren von Audiodateien. Die Transkription wird in ein Markdown-Format umgewandelt, das heruntergeladen werden kann.

## Features
- **Audiodatei hochladen**: Ziehen Sie Ihre Audiodatei in den Drop-Bereich oder klicken Sie, um eine Datei auszuwählen.
- **Transkription**: Die hochgeladene Audiodatei wird transkribiert und als Markdown angezeigt.
- **Markdown herunterladen**: Nach erfolgreicher Transkription kann die Markdown-Datei heruntergeladen werden.

## Installation

1. **Repository klonen**:
    ```bash
    [git clone https://github.com/bCommonsLAB/muschelprojekt.git
    cd muschelprojekt/local
    ```

2. **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements.txt
    ```

3. **OpenAI API-Schlüssel einrichten**:
    Ersetze `Your-Open-AI-Key` in der `app.py` durch deinen tatsächlichen API-Schlüssel.

## Nutzung

1. **Server starten**:
    ```bash
    python app.py
    ```

2. **Weboberfläche öffnen**:
    Öffne deinen Webbrowser und gehe zu `http://127.0.0.1:5000`.

3. **Audiodatei hochladen**:
    Ziehe deine Audiodatei in den Drop-Bereich oder klicke, um eine Datei auszuwählen. Unterstützte Formate sind: `flac`, `m4a`, `mp3`, `mp4`, `mpeg`, `mpga`, `oga`, `ogg`, `wav`, `webm`.

4. **Transkription anzeigen und herunterladen**:
    Nach erfolgreicher Transkription wird das Ergebnis angezeigt. Du kannst es als Markdown-Datei herunterladen.

## Code-Details

### HTML

Die HTML-Datei strukturiert die Weboberfläche mit Bereichen zum Hochladen und Anzeigen der Audiodatei, sowie für die Transkription und den Markdown-Viewer.

### CSS

Die CSS-Datei sorgt für das Styling der Weboberfläche, einschließlich des Drop-Bereichs, der Buttons und des Lade-Overlays.

### JavaScript

Das JavaScript handhabt das Hochladen der Audiodatei, die Anzeige des Audio-Players und das Abrufen der Transkription von der Flask-API.

### Flask Backend

Das Flask-Backend empfängt die Audiodatei, nutzt die OpenAI API zur Transkription und formatiert das Ergebnis als Markdown.

### Markdown Konvertierung

Der transkribierte Text wird analysiert und in ein strukturiertes JSON-Format umgewandelt, das dann in Markdown konvertiert wird.

## API-Endpunkt

### POST `/transcribe`
- **Beschreibung**: Nimmt eine Audiodatei entgegen, transkribiert sie und liefert das Ergebnis als Markdown zurück.
- **Erforderliche Parameter**: `audio` (Datei)
- **Erfolgsantwort**: JSON mit `markdown_data`



##Fehlerbehandlung
- Kein Audiodatei hochgeladen: "error": "No audio file provided"
- Nicht unterstütztes Format: "error": "Unsupported file format"
- Fehler bei der Transkription: "error": "Transcription error"
- Fehler bei der JSON-Analyse: "error": "Error decoding JSON"
