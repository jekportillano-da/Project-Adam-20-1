import os
import openai
from flask import Flask, jsonify, render_template, request
from cohere import Client as CohereClient

# ========================
# CONFIG
# ========================
USE_DEEPSEEK = True  # 🔄 Set to False to use Cohere instead

# Set up DeepSeek
openai.api_key = os.getenv("DEEPSEEK_API_KEY")
openai.api_base = "https://api.deepseek.com/v1"

# Set up Cohere
co = CohereClient(api_key=os.environ.get("COHERE_API_KEY"))

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/tip", methods=["POST"])
def get_tip():
    data = request.get_json()
    budget = float(data.get("budget", "100"))
    duration = data.get("duration", "daily")

    # Convert to daily budget
    if duration == "weekly":
        daily_budget = round(budget / 7, 2)
    elif duration == "monthly":
        daily_budget = round(budget / 30, 2)
    else:
        daily_budget = budget

    monthly_budget = round(daily_budget * 30, 2)

    prompt = f"""
You are a practical Filipino budget advisor helping someone manage ₱{daily_budget:.2f} per day in the Philippines. 
This budget was converted from their total 30-day budget of ₱{monthly_budget:.2f}.

Create a single, realistic budgeting tip tailored to this daily amount. Use Filipino culture, environment, and spending behavior, 
but do not speak in Tagalog or Taglish.

Use this format **exactly**:

Title: [A short, catchy Filipino-relevant title]

Breakdown:
- Food: ₱[amount]
- Transport: ₱[amount]
- Utilities: ₱[amount]
- Others: ₱[amount]
(Total = ₱{daily_budget:.2f})

Advice: [1–2 sentences. Make it relatable and practical for Filipinos — but keep the language in natural, simple English. You can reference Filipino habits (e.g., buying tingi, sari-sari stores, walking instead of tricycles, water refills, bringing baon, etc.). Imagine you're talking to someone on a budget in a barangay. Make sure it is also realistic and based on current scenarios.]

Rules:
- Use each category only once
- Make sure the total adds up exactly to ₱{daily_budget:.2f}
- Do not include multiple versions or repeat the format
- Do not explain, apologize, or add any extra commentary
"""

    try:
        if USE_DEEPSEEK:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )
            tip_text = response["choices"][0]["message"]["content"]
        else:
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=300,
                temperature=0.7,
                stop_sequences=["(End your response here.)"],
                return_likelihoods="NONE"
            )
            tip_text = response.generations[0].text.strip() if response.generations else "⚠️ No tip was generated. Try again."

        return jsonify({"tip": tip_text})
    except Exception as e:
        print("Error generating tip:", e)
        return jsonify({"tip": "⚠️ Something went wrong. Please try again later."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)