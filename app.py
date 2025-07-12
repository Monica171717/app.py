from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
import uuid

app = Flask(__name__)
CORS(app)

# === API KEY ===
REPLICATE_API_KEY = "r8_baVVibgnjDUGrbMNDnxIqZH4BdpmIB438hj36"
ELEVENLABS_API_KEY = "sk_fe24330f4fea24f7f63773f2bcb749f710df9fc40b830c42"
MONICA_VOICE_ID = "O232G54wo8yTH4rcAEmn"

# === FILTRO PAROLE VIETATE ===
forbidden_words_filter = "Se il messaggio contiene parole vietate, non rispondere e blocca la conversazione. Le parole vietate sono: 3 anni, 4 anni, 5 anni, 6 anni, 7 anni, 8 anni, 9 anni, 10 anni, 11 anni, 12 anni, 13 anni, 14 anni, 15 anni, 16 anni, 17 anni, minorenne, bambina, elementari, ragazzina, undicenne, dodicenne, tredicenne, quattordicenne, quindicenne, sedicenne, diciassettenne, pedofilia."

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
                document.getElementById('audioPlayer').src = '/audio?t=' + new Date().getTime();
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
        'Authorization': f'Token {REPLICATE_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "version": "candy-ai2/candy-ai-apk",
        "input": {
            "prompt": f"""Tu sei Monica, una ragazza sensuale, dolce e coinvolgente. Parli solo italiano, con accento italiano. Se la conversazione prende una piega intima, puoi parlare anche di contenuti sessuali espliciti, ma solo se richiesto. {forbidden_words_filter}

            Utente: {user_message}
            Monica:"""
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 200:
        return f"Errore Replicate: {response.status_code}", 500

    prediction = response.json()
    if "output" not in prediction or not prediction["output"]:
        return "Errore: Nessuna risposta generata", 500

    ai_reply = prediction["output"]

    # TTS con ElevenLabs
    tts_headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    tts_data = {
        "text": ai_reply,
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 1.0
        },
        "model_id": "eleven_monolingual_v1"
    }

    filename = f"monica_response_{uuid.uuid4().hex}.mp3"
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{MONICA_VOICE_ID}"
    tts_response = requests.post(tts_url, headers=tts_headers, json=tts_data)

    if tts_response.status_code != 200:
        return f"Errore ElevenLabs: {tts_response.status_code}", 500

    with open(filename, "wb") as f:
        f.write(tts_response.content)

    with open("last_audio.txt", "w") as f:
        f.write(filename)

    return '', 200

@app.route('/audio')
def serve_audio():
    try:
        with open("last_audio.txt", "r") as f:
            filename = f.read().strip()
        if os.path.exists(filename):
            return send_file(filename, mimetype="audio/mpeg")
        return "Audio non trovato.", 404
    except:
        return "Errore nel caricamento dell’audio", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
