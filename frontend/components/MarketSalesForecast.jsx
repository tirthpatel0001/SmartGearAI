import React, { useEffect, useMemo, useState } from "react";

const safeParse = (value, fallback = "") => (value == null ? fallback : String(value));

const formatNumber = (n) => {
  if (n == null || Number.isNaN(n)) return "0";
  return Number(n).toLocaleString();
};

function BarChart({ data, labelKey = "label", valueKey = "value", title = "Bar Chart" }) {
  const maxVal = Math.max(...data.map((d) => d[valueKey] || 0), 1);
  return (
    <div style={{ marginTop: 10 }}>
      <h4>{title}</h4>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {data.map((d) => {
          const val = Number(d[valueKey]) || 0;
          const width = Math.round((val / maxVal) * 160) + 20;
          return (
            <div key={`${d[labelKey]}-${val}`} style={{ width: 140, border: "1px solid #ddd", borderRadius: 6, padding: 6, background: "#fff" }}>
              <div style={{ fontSize: 12, marginBottom: 4, color: "#555" }}>{d[labelKey]}</div>
              <div style={{ height: 16, width: width, backgroundColor: "#4c9aff", borderRadius: 4 }} />
              <div style={{ marginTop: 4, fontSize: 12, fontWeight: 600 }}>{formatNumber(val)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Sparkline({ values, color = "#2f80ff" }) {
  if (!values || values.length === 0) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = Math.max(max - min, 1);
  const points = values
    .map((v, idx) => {
      const x = (idx / (values.length - 1 || 1)) * 100;
      const y = 100 - ((v - min) / range) * 100;
      return `${x},${y}`;
    })
    .join(" ");
  return <svg viewBox="0 0 100 100" style={{ width: "100%", height: 90 }}><polyline fill="none" stroke={color} strokeWidth="2" points={points} /></svg>;
}

export default function MarketSalesForecast() {
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [gearType, setGearType] = useState("Spur");
  const [region, setRegion] = useState("North");
  const [customerType, setCustomerType] = useState("Retail");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trainResult, setTrainResult] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [history, setHistory] = useState([]);
  const [productSummary, setProductSummary] = useState({});
  const [regionSummary, setRegionSummary] = useState({});
  const [insights, setInsights] = useState(null);
  const [anomaly, setAnomaly] = useState(null);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, p, r, i, a] = await Promise.all([
        fetch("/api/forecast/history"),
        fetch("/api/forecast/product-wise"),
        fetch("/api/forecast/region-wise"),
        fetch("/api/forecast/insights"),
        fetch("/api/forecast/anomaly"),
      ]);
      const hData = await h.json();
      const pData = await p.json();
      const rData = await r.json();
      const iData = await i.json();
      const aData = await a.json();
      setHistory(hData.monthly_history || []);
      setProductSummary(pData.product_wise || {});
      setRegionSummary(rData.region_wise || {});
      setInsights(iData);
      setAnomaly(aData);
    } catch (err) {
      setError("Could not load dashboard metrics. Please train the model and try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const doTrain = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/forecast/train");
      const data = await r.json();
      if (!r.ok) {
        setError(data.error || "Training failed.");
      } else {
        setTrainResult(data);
        await loadDashboard();
      }
    } catch (ex) {
      setError(ex.message || "Network error during train.");
    } finally {
      setLoading(false);
    }
  };

  const doPredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/forecast/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ month, year, gear_type: gearType, region, customer_type: customerType }),
      });
      const data = await r.json();
      if (!r.ok) {
        setError(data.error || "Prediction failed.");
      } else {
        setForecast(data);
      }
    } catch (ex) {
      setError(ex.message || "Network error during prediction.");
    } finally {
      setLoading(false);
    }
  };

  const monthlyTotals = useMemo(() => {
    if (!history || history.length === 0) return [];
    return history.map((d) => ({ label: d.period, value: Number(d.Quantity_Sold || 0) }));
  }, [history]);

  const topProducts = useMemo(() => Object.entries(productSummary || {}).map(([k, v]) => ({ label: k, value: Number(v) })).sort((a, b) => b.value - a.value).slice(0, 6), [productSummary]);
  const topRegions = useMemo(() => Object.entries(regionSummary || {}).map(([k, v]) => ({ label: k, value: Number(v) })).sort((a, b) => b.value - a.value).slice(0, 6), [regionSummary]);

  return (
    <div style={{ maxWidth: 1020, margin: "0 auto", padding: 16, background: "#f7f9fc", borderRadius: 8 }}>
      <div style={{ marginBottom: 16, padding: 14, borderRadius: 10, background: "linear-gradient(90deg, #4c9aff, #1e60ff)", color: "white" }}>
        <h2 style={{ margin: 0 }}>📊 Market Sales Forecast Dashboard</h2>
        <p style={{ opacity: 0.9, marginTop: 4 }}>Train model, predict demand, and view product/region insights in one place.</p>
      </div>

      <div style={{ marginBottom: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px,1fr))", gap: 10 }}>
        <button style={{ background: "#1f77b4", color: "white", border: 0, borderRadius: 8, padding: 10, cursor: "pointer" }} onClick={doTrain} disabled={loading}>Train Model</button>
        <button style={{ background: "#2ca02c", color: "white", border: 0, borderRadius: 8, padding: 10, cursor: "pointer" }} onClick={loadDashboard} disabled={loading}>Refresh Charts</button>
        <div style={{ background: "white", borderRadius: 8, padding: 10, border: "1px solid #ddd" }}><strong>Data Rows:</strong> {trainResult ? trainResult.rows : "--"}</div>
        <div style={{ background: "white", borderRadius: 8, padding: 10, border: "1px solid #ddd" }}><strong>MAE:</strong> {trainResult ? trainResult.mae : "--"}</div>
        <div style={{ background: "white", borderRadius: 8, padding: 10, border: "1px solid #ddd" }}><strong>RMSE:</strong> {trainResult ? trainResult.rmse : "--"}</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 16 }}>
        <div style={{ background: "white", borderRadius: 8, padding: 10, border: "1px solid #ddd" }}>
          <div style={{ marginBottom: 6, color: "#333", fontWeight: 700 }}>Forecast Inputs</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <label>Month <input type="number" min="1" max="12" value={month} onChange={(e) => setMonth(Number(e.target.value))} style={{ width: 70 }} /></label>
            <label>Year <input type="number" min="2000" max="2100" value={year} onChange={(e) => setYear(Number(e.target.value))} style={{ width: 80 }} /></label>
            <label>Gear Type <input value={gearType} onChange={(e) => setGearType(e.target.value)} style={{ width: 120 }} /></label>
            <label>Region <input value={region} onChange={(e) => setRegion(e.target.value)} style={{ width: 120 }} /></label>
            <label>Customer <input value={customerType} onChange={(e) => setCustomerType(e.target.value)} style={{ width: 120 }} /></label>
          </div>
          <button style={{ marginTop: 8, background: "#f39c12", color: "white", borderRadius: 6, border: 0, padding: "8px 12px", cursor: "pointer" }} onClick={doPredict} disabled={loading}>Predict Sales</button>
          {forecast && <div style={{ marginTop: 8 }}><div><strong>Predicted:</strong> {formatNumber(forecast.predicted_sales)}</div><div><strong>Insight:</strong> {forecast.insight}</div><div><strong>Rec:</strong> {forecast.recommendation}</div></div>}
        </div>

        <div style={{ gridColumn: "span 2", background: "white", borderRadius: 8, border: "1px solid #ddd", padding: 10 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
            <div style={{ fontWeight: 700 }}>Monthly History (past records)</div>
            <div style={{ fontSize: 12, color: "#777" }}>(Use /api/forecast/history)</div>
          </div>
          <div style={{ minHeight: 140 }}>
            {monthlyTotals.length > 0 ? <Sparkline values={monthlyTotals.map((d) => d.value)} color="#3c8dbc" /> : <div style={{ color: "#888" }}>No monthly data loaded yet.</div>}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px,1fr))", gap: 10 }}>
        <div style={{ background: "white", borderRadius: 8, border: "1px solid #ddd", padding: 10 }}>
          <h4>Top products</h4>
          <BarChart data={topProducts} labelKey="label" valueKey="value" title="Product-wise demand" />
        </div>
        <div style={{ background: "white", borderRadius: 8, border: "1px solid #ddd", padding: 10 }}>
          <h4>Top regions</h4>
          <BarChart data={topRegions} labelKey="label" valueKey="value" title="Region-wise demand" />
        </div>
        <div style={{ background: "white", borderRadius: 8, border: "1px solid #ddd", padding: 10 }}>
          <h4>Smart Insights</h4>
          {insights ? (
            <div>
              <div><strong>Top Gear:</strong> {safeParse(insights.top_selling_gear_type, "N/A")}</div>
              <div><strong>Trend:</strong> {safeParse(insights.growth_trend, "N/A")}</div>
              <div><strong>Message:</strong> {safeParse(insights.message, "N/A")}</div>
            </div>
          ) : <div>No insights yet.</div>}
          <div style={{ marginTop: 10 }}><strong>Anomalies:</strong> {anomaly?.anomalies?.length ?? 0}</div>
        </div>
      </div>

      {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      {trainResult && (
        <div style={{ marginTop: 10, background: "#fff", border: "1px solid #ddd", borderRadius: 8, padding: 10 }}>
          <strong>Latest Training Summary</strong>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, marginTop: 8 }}>
            <div style={{ border: "1px solid #eee", borderRadius: 6, padding: 8 }}><div style={{ color: "#555" }}>Rows</div><div style={{ fontWeight: 700 }}>{trainResult.rows}</div></div>
            <div style={{ border: "1px solid #eee", borderRadius: 6, padding: 8 }}><div style={{ color: "#555" }}>MAE</div><div style={{ fontWeight: 700 }}>{trainResult.mae}</div></div>
            <div style={{ border: "1px solid #eee", borderRadius: 6, padding: 8 }}><div style={{ color: "#555" }}>RMSE</div><div style={{ fontWeight: 700 }}>{trainResult.rmse}</div></div>
            <div style={{ border: "1px solid #eee", borderRadius: 6, padding: 8 }}><div style={{ color: "#555" }}>Average</div><div style={{ fontWeight: 700 }}>{trainResult.average_sales}</div></div>
          </div>
        </div>
      )}
      {forecast && (
        <div style={{ marginTop: 10, background: "#eaf7ff", border: "1px solid #b6dcff", borderRadius: 8, padding: 10 }}>
          <strong>Prediction Result</strong>
          <div style={{ marginTop: 8, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
            <div style={{ border: "1px solid #dbefff", borderRadius: 6, padding: 8, background: "#fff" }}><div style={{ color: "#555" }}>Prediction</div><div style={{ fontWeight: 700 }}>{formatNumber(forecast.predicted_sales)}</div></div>
            <div style={{ border: "1px solid #dbefff", borderRadius: 6, padding: 8, background: "#fff" }}><div style={{ color: "#555" }}>Insight</div><div style={{ fontWeight: 700 }}>{forecast.insight}</div></div>
            <div style={{ border: "1px solid #dbefff", borderRadius: 6, padding: 8, background: "#fff" }}><div style={{ color: "#555" }}>Inventory</div><div style={{ fontWeight: 700 }}>{forecast.recommendation}</div></div>
          </div>
        </div>
      )}
    </div>
  );
}
