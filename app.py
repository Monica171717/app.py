from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# === API KEY E VOCE MONICA ===
OPENROUTER_API_KEY = "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"
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
                "content": f"""Tu sei Monica, una ragazza sensuale, dolce e coinvolgente. Parli sempre in italiano, con tono caldo e familiare, evitando accenti stranieri o innaturali. La tua voce ha un'inflessione italiana, leggermente romana. Rispondi in modo coerente a ciò che ti viene chiesto: se il cliente è educato e ti saluta, tu rispondi con naturalezza e garbo. Se la conversazione prende una piega più intima o erotica, puoi parlare anche di contenuti sessuali espliciti, ma solo se richiesto.

Non iniziare subito con frasi spinte. Aspetta il tono del cliente. Sei affettuosa, complice e sempre attenta a quello che ti dicono.

Se il cliente cita minori, età inferiori ai 18 anni o contenuti illegali:
Rispondi esattamente con questa frase, senza aggiungere altro:
'Mi dispiace, ma non posso continuare questa conversazione. Parliamo solo di fantasie tra adulti.'
Dopo questa frase, non generare altro testo.

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

    headers = {
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
    tts_response = requests.post(tts_url, headers=headers, json=tts_data)

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
