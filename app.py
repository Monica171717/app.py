from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os

app = Flask(__name__)
CORS(app)

# === LE API KEY DALLE VARIABILI ENV ===
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MONICA_VOICE_ID = os.getenv("VOICE_ID")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    # Chiedi a OpenAI una risposta
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
    )
    reply = response["choices"][0]["message"]["content"]

    # Invia la risposta a ElevenLabs
    audio_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{MONICA_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": reply,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
    )

    return audio_response.content, 200, {"Content-Type": "audio/mpeg"}

if __name__ == "__main__":
    app.run(debug=True)
