import os

from cohere import Client as ClientV2
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Load API key from environment (Replit secrets)
co = ClientV2(api_key=os.environ.get("COHERE_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/tip", methods=["POST"])
def get_tip():
    data = request.get_json()
    budget = data.get("budget", "100")

    prompt = f"""
    You are a frugal Filipino budget advisor.

    A person has ₱{budget} to spend per day in the Philippines.
    Break down how they should allocate their money across essential daily categories (e.g., food, transport, savings, etc.).

    Provide a local, realistic, and specific suggestion that fits the Filipino context.

    Format the response as:
    Title: [Bold tip title]
    Breakdown:
    - [Category 1]: ₱[amount]
    - [Category 2]: ₱[amount]
    ...
    Advice: [1–2 sentences on how to stretch the budget]

    Only return the formatted result. Do not repeat the prompt or explain anything else.
    """

    try:
            response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3
        )

        tip_text = response.text.strip() if response.text else "⚠️ No tip was generated. Try again."

        # Debugging output in console
        print("=== DEBUG PROMPT ===")
        print(prompt)
        print("=== DEBUG RESPONSE ===")
        print(tip_text)

        return jsonify({"tip": tip_text})

    except Exception as e:
        print("Error generating tip:", e)
        return jsonify({"tip": "⚠️ Something went wrong. Please try again later."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
