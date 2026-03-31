from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_recommendation(expenses):

    if not expenses:
        return ["No data available"]

    # 🔹 Convert data into readable format
    summary = ""
    total = 0

    for e in expenses:
        summary += f"{e['category']}: ₹{e['amount']}\n"
        total += float(e["amount"])

    # 🔥 PROMPT
    prompt = f"""
    You are a smart financial advisor.

    User monthly expenses:
    {summary}

    Total spending: ₹{total}

    Give:
    - overspending insights
    - category analysis
    - savings suggestions
    - practical advice

    Keep it short, clear, and in bullet points.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful financial advisor."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content

    # 🔹 Convert text → list
    insights = output.split("\n")

    return insights