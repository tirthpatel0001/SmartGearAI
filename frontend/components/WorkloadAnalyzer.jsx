import React, { useState } from "react";

export default function WorkloadAnalyzer() {
  const [teeth, setTeeth] = useState(90);
  const [diameter, setDiameter] = useState(180);
  const [processSteps, setProcessSteps] = useState(4);
  const [machineCount, setMachineCount] = useState(3);
  const [airTemp, setAirTemp] = useState(300);
  const [processTemp, setProcessTemp] = useState(310);
  const [speed, setSpeed] = useState(1500);
  const [torque, setTorque] = useState(50);
  const [toolWear, setToolWear] = useState(5);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/production/workload-analyzer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          teeth: Number(teeth),
          diameter: Number(diameter),
          process_steps: Number(processSteps),
          machine_count: Number(machineCount),
          air_temperature: Number(airTemp),
          process_temperature: Number(processTemp),
          rotational_speed: Number(speed),
          torque: Number(torque),
          tool_wear: Number(toolWear),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Failed to analyze workload");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: 16 }}>
      <h2>Workload Analyzer</h2>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8 }}>
        <label>
          Teeth:
          <input type="number" value={teeth} onChange={(e) => setTeeth(e.target.value)} min={1} required />
        </label>
        <label>
          Diameter:
          <input type="number" value={diameter} onChange={(e) => setDiameter(e.target.value)} min={1} required />
        </label>
        <label>
          Process Steps:
          <input type="number" value={processSteps} onChange={(e) => setProcessSteps(e.target.value)} min={1} required />
        </label>
        <label>
          Machine Count:
          <input type="number" value={machineCount} onChange={(e) => setMachineCount(e.target.value)} min={1} required />
        </label>
        <label>
          Air Temperature:
          <input type="number" value={airTemp} onChange={(e) => setAirTemp(e.target.value)} min={0} required />
        </label>
        <label>
          Process Temperature:
          <input type="number" value={processTemp} onChange={(e) => setProcessTemp(e.target.value)} min={0} required />
        </label>
        <label>
          Rotational Speed:
          <input type="number" value={speed} onChange={(e) => setSpeed(e.target.value)} min={0} required />
        </label>
        <label>
          Torque:
          <input type="number" value={torque} onChange={(e) => setTorque(e.target.value)} min={0} required />
        </label>
        <label>
          Tool Wear:
          <input type="number" value={toolWear} onChange={(e) => setToolWear(e.target.value)} min={0} required />
        </label>
        <button type="submit" disabled={loading} style={{ marginTop: 10 }}>
          {loading ? "Analyzing..." : "Analyze Workload"}
        </button>
      </form>

      {error && <div style={{ marginTop: 12, color: "red" }}>Error: {error}</div>}
      {result && (
        <div style={{ marginTop: 12, padding: 12, border: "1px solid #ddd", borderRadius: 6 }}>
          <h3>Results</h3>
          <p><strong>Lead Time:</strong> {result.lead_time}</p>
          <p><strong>Machines:</strong> {result.machine_count}</p>
          <p><strong>Remaining Time:</strong> {result.remaining_time}</p>
          <p><strong>Machine Risk:</strong> {result.machine_risk}</p>
        </div>
      )}
    </div>
  );
}
