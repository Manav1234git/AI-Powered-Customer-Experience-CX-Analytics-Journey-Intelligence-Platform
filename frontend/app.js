const apiPaths = {
  sentiment: "/sentiment",
  churn: "/churn",
  recommendations: "/recommendations",
};

const elements = {
  totalReviews: document.getElementById("totalReviews"),
  positiveMentions: document.getElementById("positiveMentions"),
  negativeMentions: document.getElementById("negativeMentions"),
  positiveBar: document.getElementById("positiveBar"),
  negativeBar: document.getElementById("negativeBar"),
  churnProb: document.getElementById("churnProb"),
  riskSummary: document.getElementById("riskSummary"),
  eventTotal: document.getElementById("eventTotal"),
  riskBar: document.getElementById("riskBar"),
  recommendationList: document.getElementById("recommendationList"),
  metricGrid: document.getElementById("metricGrid"),
  refreshButton: document.getElementById("refreshButton"),
};

function setMetricGrid(items) {
  elements.metricGrid.innerHTML = items
    .map(
      item => `
      <div class="metric-card">
        <div>
          <p class="metric-title">${item.title}</p>
          <p class="stat-value">${item.value}</p>
          <p class="stat-label">${item.subtitle}</p>
        </div>
      </div>
    `,
    )
    .join("");
}

function createRecommendationList(recommendations) {
  if (!recommendations || !recommendations.length) {
    return "<li>No insight recommendations available.</li>";
  }
  return recommendations
    .map(rec => `<li>${rec}</li>`)
    .join("");
}

function updateBar(element, percent) {
  element.style.width = `${Math.min(Math.max(percent, 0), 100)}%`;
}

function numberWithCommas(value) {
  return value.toLocaleString();
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Unable to fetch ${path}`);
  }
  return response.json();
}

async function refreshDashboard() {
  try {
    elements.metricGrid.innerHTML = `<div class="metric-card"><span class="metric-title">Refreshing…</span></div>`;
    const [sentiment, churn, recommendations] = await Promise.all([
      fetchJson(apiPaths.sentiment),
      fetchJson(apiPaths.churn),
      fetchJson(apiPaths.recommendations),
    ]);

    const positive = sentiment.positive_mentions || 0;
    const negative = sentiment.negative_mentions || 0;
    const total = sentiment.total_reviews || 0;
    const sentimentScore = total ? Math.round((positive / Math.max(total, 1)) * 100) : 0;
    const negativeScore = total ? Math.round((negative / Math.max(total, 1)) * 100) : 0;

    setMetricGrid([
      {
        title: "Total reviews",
        value: numberWithCommas(total),
        subtitle: "Customer review records",
      },
      {
        title: "Positive sentiment",
        value: `${sentimentScore}%`,
        subtitle: "Positive keyword share",
      },
      {
        title: "Negative sentiment",
        value: `${negativeScore}%`,
        subtitle: "Negative keyword share",
      },
      {
        title: "Churn probability",
        value: `${Math.round((churn.churn_probability || 0) * 100)}%`,
        subtitle: "Estimated churn risk",
      },
    ]);

    elements.totalReviews.textContent = numberWithCommas(total);
    elements.positiveMentions.textContent = numberWithCommas(positive);
    elements.negativeMentions.textContent = numberWithCommas(negative);
    elements.churnProb.textContent = `${Math.round((churn.churn_probability || 0) * 100)}%`;
    elements.eventTotal.textContent = numberWithCommas(churn.total_events || 0);
    elements.riskSummary.textContent = `${churn.risk_level || "Unknown"} risk detected`;

    updateBar(elements.positiveBar, sentimentScore);
    updateBar(elements.negativeBar, negativeScore);
    updateBar(elements.riskBar, Math.min(Math.max((churn.churn_probability || 0) * 100, 10), 100));

    elements.recommendationList.innerHTML = createRecommendationList(recommendations.recommendations);
  } catch (error) {
    elements.metricGrid.innerHTML = `<div class="metric-card"><span class="metric-title">Failed to load data</span></div>`;
    elements.recommendationList.innerHTML = `<li>${error.message}</li>`;
  }
}

elements.refreshButton.addEventListener("click", () => refreshDashboard());
refreshDashboard();
