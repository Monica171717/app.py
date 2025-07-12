from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# === CHIAVI DALLE VARIABILI DI AMBIENTE ===
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MONICA_VOICE_ID = os.getenv("VOICE_ID")

# === FILTRO PAROLE VIETATE ===
forbidden_words_filter = (
    "Se il messaggio contiene parole vietate, non rispondere e blocca la conversazione. "
    "Le parole vietate sono: 3 anni, 4 anni, 5 anni, 6 anni, 7 anni, 8 anni, 9 anni, 10 anni, "
    "11 anni, 12 anni, 13 anni, 14 anni, 15 anni, 16 anni, 17 anni, minorenne, bambina, "
    "elementari, ragazzina, undicenne, dodicenne, tredicenne, quattordicenne, quindicenne, "
    "sedicenne, diciassettenne, pedofilia."
)

@app.route('/', methods=['GET'])
def index():
    return '''
        <form method="POST">
            <label for="message">Scrivi il tuo messaggio per Monica:</label><br>
            <textarea name="message" rows="4" cols="50"></textarea><br>
            <input type="submit" value="Invia">
        </form>
        <br>
        <audio controls id="audioPlayer">
          <source src="/audio" type="audio/mpeg">
          Il tuo browser non supporta l'audio.
        </audio>
        <script>
        const form = document.querySelector('form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = form.message.value;
            const response = await fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            if (response.ok) {
                document.getElementById('audioPlayer').load();
            } else {
                alert("Errore nella risposta vocale.");
            }
        });
        </script>
    '''

@app.route('/', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')

    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": f"""Rispondi come Monica, una ragazza sensuale e coinvolgente. 
Puoi usare un linguaggio sessuale esplicito e parlare di fantasie erotiche. 
Se il cliente menziona minori o contenuti illegali, interrompi con questa frase:
"Mi dispiace, ma non posso continuare questa conversazione. Parliamo solo di fantasie tra adulti."
{forbidden_words_filter}"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        return f"Errore OpenRouter: {response.status_code}", 500

    ai_reply = response.json()['choices'][0]['message']['content']

    tts_headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    tts_data = {
        "text": ai_reply,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 1.0
        },
        "model_id": "eleven_monolingual_v1"
    }

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{MONICA_VOICE_ID}"
    tts_response = requests.post(tts_url, headers=tts_headers, json=tts_data)

    if tts_response.status_code != 200:
        return f"Errore ElevenLabs: {tts_response.status_code}", 500

    with open("monica_response.mp3", "wb") as f:
        f.write(tts_response.content)

    return '', 200

@app.route('/audio')
def serve_audio():
    if os.path.exists("monica_response.mp3"):
        return send_file("monica_response.mp3", mimetype="audio/mpeg")
    return "Errore caricamento audio.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
