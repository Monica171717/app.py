from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import uuid
import time

app = Flask(__name__)
CORS(app)

# === LE TUE API KEY ===
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

    # === RICHIESTA A REPLICATE ===
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "version": "9b98f2e799c132dc41d9c6f810f9e96e22ddc75b376f6cb05dcb02fe942e6d1f",
        "input": {
            "prompt": user_message,
            "system_prompt": f"""Tu sei Monica, una ragazza sensuale, dolce e coinvolgente. Parli sempre in italiano, con tono caldo e familiare, evitando accenti stranieri o innaturali. La tua voce ha un'inflessione italiana, leggermente romana. Rispondi in modo coerente a ciò che ti viene chiesto: se il cliente è educato e ti saluta, tu rispondi con naturalezza e garbo. Se la conversazione prende una piega più intima o erotica, puoi parlare anche di contenuti sessuali espliciti, ma solo se richiesto.

Non iniziare subito con frasi spinte. Aspetta il tono del cliente. Sei affettuosa, complice e sempre attenta a quello che ti dicono.

Se il cliente cita minori, età inferiori ai 18 anni o contenuti illegali:
Rispondi esattamente con questa frase, senza aggiungere altro:
'Mi dispiace, ma non posso continuare questa conversazione. Parliamo solo di fantasie tra adulti.'

{forbidden_words_filter}"""
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)

    if response.status_code != 201:
        return f"Errore Replicate: {response.status_code}", 500

    prediction = response.json()
    prediction_id = prediction['id']

    status = prediction['status']
    while status != "succeeded":
        time.sleep(1)
        poll = requests.get(f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers)
        prediction = poll.json()
        status = prediction['status']
        if status == "failed":
            return "Errore nella generazione della risposta AI.", 500

    ai_reply = prediction['output']

    # === TEXT TO SPEECH (ELEVENLABS) ===
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

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{MONICA_VOICE_ID}"
    tts_response = requests.post(tts_url, headers=tts_headers, json=tts_data)

    if tts_response.status_code != 200:
        return f"Errore ElevenLabs: {tts_response.status_code}", 500

    filename = f"monica_response_{uuid.uuid4().hex}.mp3"
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
        return "Errore caricamento audio.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
