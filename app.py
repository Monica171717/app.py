from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    if any(word in prompt.lower() for word in ["minorenni", "17 anni", "ragazzina", "bambina"]):
        return jsonify({"response": "Mi dispiace, non posso continuare questa conversazione."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei Monica, una ragazza sensuale che risponde in modo erotico e provocante, ma blocca ogni riferimento a minori."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Monica AI è online. Usa POST /chat"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
