let chart;

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const product = document.getElementById("productInput").value.trim();
  if (!product) return alert("Please enter a product!");

  const resultsCard = document.getElementById("resultsCard");
  const loading = document.getElementById("loading");
  
  resultsCard.style.display = "none";
  loading.style.display = "flex";

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ product })
    });

    const data = await response.json();

    if (data.error) return alert(data.error);

    document.getElementById("productName").innerText = data.product;
    document.getElementById("trendResult").innerText = data.trend;
    document.getElementById("scoreResult").innerText = data.score;
    document.getElementById("predictionResult").innerText = data.prediction;

    const recEl = document.getElementById("recommendationResult");
    recEl.innerText = data.recommendation;
    recEl.style.color = data.recommendation === "Invest" ? "green" :
                        data.recommendation === "Hold" ? "orange" : "red";

    // Chart
    const ctx = document.getElementById('trendChart').getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
        datasets: [{
          label: 'Trend Score',
          data: [data.score-5, data.score-2, data.score-1, data.score],
          borderColor: '#1abc9c',
          backgroundColor: 'rgba(26, 188, 156, 0.2)',
          fill: true,
          tension: 0.4
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });

    resultsCard.style.display = "block";
  } catch (err) {
    alert("Error connecting to backend. Make sure backend is running.");
    console.error(err);
  } finally {
    loading.style.display = "none";
  }
});
