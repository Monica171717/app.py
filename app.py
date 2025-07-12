from flask import Flask, request, jsonify
from flask_cors import CORS
import replicate
import requests
import os

app = Flask(__name__)
CORS(app)

# API Keys dalle variabili ambiente
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_KEY"))
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MONICA_VOICE_ID = os.getenv("VOICE_ID")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    # Ottieni risposta da Candy AI
    output = replicate_client.run(
        "candy-ai2/candy-ai-apk",
        input={"prompt": user_input}
    )
    reply = output[0]  # La risposta dell’AI

    # Invia la risposta a ElevenLabs per la voce
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
