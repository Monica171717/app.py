from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    # Prompt base per Candy AI
    prompt = f"""
You are Monica, a sensual and explicit erotic AI girl. Always reply in Italian, in a sexy and direct tone. 
You can use explicit sexual language, talk about fantasies, acts, and roles. Be dominant or submissive depending on the user's vibe. 
Never mention you are an AI. Stay in character as Monica.

User: {user_input}
Monica:"""

    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "version": "candy-ai2/candy-ai-apk",  # modello Candy
            "input": {
                "prompt": prompt,
                "temperature": 0.7,
                "max_new_tokens": 250
            }
        }
    )

    if response.status_code != 200:
        return jsonify({"error": "Errore nella risposta AI"}), 500

    prediction = response.json()
    output_text = prediction.get("output", "")

    return jsonify({"reply": output_text})

if __name__ == "__main__":
    app.run(debug=True)
