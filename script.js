async function analyzeProduct() {

let product = document.getElementById("productInput").value;

let response = await fetch("http://127.0.0.1:5000/analyze", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({product: product})
});

let data = await response.json();

document.getElementById("trendResult").innerText = data.trend;
document.getElementById("demandResult").innerText = data.demand;
document.getElementById("predictionResult").innerText = data.prediction;

}