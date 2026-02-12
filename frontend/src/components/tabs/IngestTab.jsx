import React, { useState } from "react";
import Panel from "../Panel.jsx";

function IngestTab({ apiRequest }) {
  const [depIata, setDepIata] = useState("");
  const [arrIata, setArrIata] = useState("");
  const [limit, setLimit] = useState(50);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const ingest = async (mode) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const path =
        mode === "dep"
          ? `/ingest/flights?dep_iata=${depIata}&limit=${limit}`
          : `/ingest/flights?arr_iata=${arrIata}&limit=${limit}`;
      const data = await apiRequest(path, { method: "POST", timeoutMs: 180000 });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Panel title="Ingest Flights">
      <div className="crud-grid">
        <div>
          <h3>Departures</h3>
          <input placeholder="Dep IATA" value={depIata} onChange={(e) => setDepIata(e.target.value.toUpperCase())} />
          <input type="number" placeholder="Limit" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
          <button onClick={() => ingest("dep")} disabled={loading}>Ingest Departures</button>
        </div>
        <div>
          <h3>Arrivals</h3>
          <input placeholder="Arr IATA" value={arrIata} onChange={(e) => setArrIata(e.target.value.toUpperCase())} />
          <input type="number" placeholder="Limit" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
          <button onClick={() => ingest("arr")} disabled={loading}>Ingest Arrivals</button>
        </div>
      </div>
      {loading ? <div className="muted">Ingesting...</div> : null}
      {error && <div className="error">{error}</div>}
      {result && (
        <pre className="code">{JSON.stringify(result, null, 2)}</pre>
      )}
    </Panel>
  );
}

export default IngestTab;
