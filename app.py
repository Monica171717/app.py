from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# === VARIABILI DA RAILWAY ===
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MONICA_VOICE_ID = os.getenv("VOICE_ID")

# === FILTRO PAROLE VIETATE ===
forbidden_words = [
    "3 anni", "4 anni", "5 anni", "6 anni", "7 anni", "8 anni", "9 anni", "10 anni", "11 anni", "12 anni",
    "13 anni", "14 anni", "15 anni", "16 anni", "17 anni", "minorenne", "bambina", "elementari", "ragazzina",
    "undicenne", "dodicenne", "tredicenne", "quattordicenne", "quindicenne", "sedicenne", "diciassettenne", "pedofilia"
]

@app.route("/", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").lower()

    # Blocco se contiene parole vietate
    if any(word in user_input for word in forbidden_words):
        reply = "Mi dispiace, ma non posso continuare questa conversazione. Parliamo solo di fantasie tra adulti."
    else:
        # Prompt moderato, erotico se richiesto
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu sei Monica, una ragazza sensuale e intrigante. Puoi parlare di contenuti sessuali espliciti, "
                        "ma solo se è ciò che il cliente desidera. Adatta il tuo tono: puoi essere dolce, provocante, "
                        "romantica o più audace, ma non esagerare se non richiesto."
                    )
                },
                {
                    "role": "user",
                    "content": data.get("message", "")
                }
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            return f"Errore OpenRouter: {response.status_code}", 500

        reply = response.json()['choices'][0]['message']['content']

    # Voce con ElevenLabs
    tts_headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    tts_data = {
        "text": reply,
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

    with open("monica_output.mp3", "wb") as f:
        f.write(tts_response.content)

    return send_file("monica_output.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
