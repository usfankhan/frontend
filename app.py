from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["fintrack"]
collection = db["expenses"]

# OpenAI
client_ai = OpenAI(api_key="OPEN_API_KEY")

# -------------------- EXPENSE APIs --------------------

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    collection.insert_one(data)
    return jsonify({"message": "Expense added"})


@app.route('/expenses/<id>', methods=['DELETE'])
def delete_expense(id):
    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Deleted"})


@app.route('/expenses', methods=['GET'])
def get_expenses():
    data = []
    for e in collection.find():
        e["_id"] = str(e["_id"])
        data.append(e)
    return jsonify(data)

# -------------------- AI INSIGHTS --------------------
@app.route('/recommendation', methods=['GET'])
def recommendation():
    expenses = []

    for e in collection.find():
        e["_id"] = str(e["_id"])
        expenses.append(e)

    summary = "\n".join(
        [f"{e['category']}: ₹{e['amount']}" for e in expenses]
    )

    prompt = f"""
    You are a financial advisor.

    User expenses:
    {summary}

    Give insights.
    """

    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a smart finance advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        output = response.choices[0].message.content
        return jsonify(output.split("\n"))

    except Exception as e:
        print("AI Error:", e)

        # 🔥 FALLBACK LOGIC
        return jsonify([
            "⚠️ AI service temporarily unavailable",
            "💡 Reduce unnecessary expenses",
            "💰 Try saving 20% of income"
        ])

    output = response.choices[0].message.content

    return jsonify(output.split("\n"))

# -------------------- CHATBOT --------------------

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get("message")

    expenses = []
    for e in collection.find():
        e["_id"] = str(e["_id"])
        expenses.append(e)

    summary = "\n".join(
        [f"{e['category']}: ₹{e['amount']}" for e in expenses]
    )

    prompt = f"""
    You are a personal finance assistant.

    User expenses:
    {summary}

    Question: {message}

    Give helpful and simple advice.
    """

    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful finance chatbot."},
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content

    return jsonify({"reply": reply})

# --------------------

if __name__ == '__main__':
    app.run(debug=True)