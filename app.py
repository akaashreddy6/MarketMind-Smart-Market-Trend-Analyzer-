# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Allow frontend to access

# Simulated product database
PRODUCTS_DB = {
    "smartphone": {"trend_history": [70, 75, 80, 85]},
    "laptop": {"trend_history": [60, 65, 63, 68]},
    "headphones": {"trend_history": [50, 55, 60, 70]},
    "book": {"trend_history": [20, 25, 30, 28]},
    "shoes": {"trend_history": [40, 45, 50, 55]},
}

def calculate_trend(trend_history):
    """Determine trend direction and score"""
    last = trend_history[-1]
    prev = trend_history[-2]
    if last > prev:
        return "Trending 🔥", last
    elif last == prev:
        return "Stable ➖", last
    else:
        return "Falling ❄️", last

def predict_sales(score):
    """Predict sales and recommendation"""
    growth = random.randint(-10, 20) + (score // 5)
    if growth > 15:
        return "Sales likely to increase 📈", "Invest"
    elif growth > 5:
        return "Sales might slightly increase ⬆️", "Hold"
    else:
        return "Sales might decrease 📉", "Avoid"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    product = data.get("product", "").strip().lower()

    if not product:
        return jsonify({"error": "No product provided"}), 400

    product_info = PRODUCTS_DB.get(
        product,
        {"trend_history": [random.randint(20, 50) for _ in range(4)]}
    )

    trend, score = calculate_trend(product_info["trend_history"])
    prediction, recommendation = predict_sales(score)

    return jsonify({
        "product": product.title(),
        "trend": trend,
        "score": score,
        "prediction": prediction,
        "recommendation": recommendation
    })

if __name__ == "__main__":
    app.run(debug=True)
