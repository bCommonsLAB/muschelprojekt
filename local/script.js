document.addEventListener("DOMContentLoaded", () => {
    const dropArea = document.getElementById('drop-area');
    const fileElem = document.getElementById('fileElem');
    const audioPlayer = document.getElementById('audio-player');
    const uploadedAudio = document.getElementById('uploaded-audio');
    const transcriptionOutput = document.getElementById('transcription-output');
    const markdownOutput = document.getElementById('markdown-viewer');
    const loadingOverlay = document.getElementById('loading-overlay');
    const downloadBtn = document.getElementById('download-btn');
    const templateSelect = document.getElementById('template-select');

    function loadTemplates() {
        fetch('http://127.0.0.1:5000/templates')
            .then(response => response.json())
            .then(data => {
                data.templates.forEach(template => {
                    const option = document.createElement('option');
                    option.value = template;
                    option.textContent = template;
                    templateSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading templates:', error));
    }

    function handleFiles(files) {
        const file = files[0];
        if (file) {
            handleAudioFile(file);
            displayAudio(file);
        }
    }

    function handleAudioFile(file) {
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('template', templateSelect.value);

        document.body.classList.add('loading');
        loadingOverlay.style.display = 'flex';
        transcriptionOutput.innerText = '';
        markdownOutput.innerText = '';
        downloadBtn.style.display = 'none';

        fetch('http://127.0.0.1:5000/transcribe', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            document.body.classList.remove('loading');
            loadingOverlay.style.display = 'none';
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                transcriptionOutput.innerText = 'Fehler bei der Transkription: ' + data.error;
            } else {
                transcriptionOutput.innerText = 'Transkription erfolgreich';
                displayMarkdown(data.filled_template);
                downloadBtn.style.display = 'block';
            }
        })
        .catch(error => {
            document.body.classList.remove('loading');
            loadingOverlay.style.display = 'none';
            transcriptionOutput.innerText = 'Fehler bei der Transkription';
            console.error('Transcription error:', error);
        });
    }

    function displayAudio(file) {
        const fileURL = URL.createObjectURL(file);
        audioPlayer.src = fileURL;
        uploadedAudio.style.display = 'block';
    }

    function displayMarkdown(data) {
        const markdownViewer = document.createElement('pre');
        markdownViewer.style.whiteSpace = "pre-wrap";
        markdownViewer.textContent = data;
        markdownOutput.appendChild(markdownViewer);
    }

    function downloadMarkdown() {
        const markdownContent = markdownOutput.querySelector('pre').textContent;
        const blob = new Blob([markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transcription.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    dropArea.addEventListener('dragover', event => {
        event.preventDefault();
        dropArea.classList.add('highlight');
    });

    dropArea.addEventListener('dragleave', event => {
        dropArea.classList.remove('highlight');
    });

    dropArea.addEventListener('drop', event => {
        event.preventDefault();
        dropArea.classList.remove('highlight');
        const files = event.dataTransfer.files;
        handleFiles(files);
    });

    dropArea.addEventListener('click', () => {
        fileElem.click();
    });

    fileElem.addEventListener('change', (event) => {
        handleFiles(event.target.files);
    });

    window.downloadMarkdown = downloadMarkdown;
    loadTemplates();
});
