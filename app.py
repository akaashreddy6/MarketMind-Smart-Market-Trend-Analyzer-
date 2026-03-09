from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    product = data['product']

    # Example logic
    trend = "Trending 🔥"
    demand = "High Demand"
    prediction = "Sales likely to increase"

    return jsonify({
        "trend": trend,
        "demand": demand,
        "prediction": prediction
    })

if __name__ == '__main__':
    app.run(debug=True)