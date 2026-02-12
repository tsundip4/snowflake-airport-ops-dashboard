import React, { useState } from "react";
import DataTable from "../DataTable.jsx";
import Field from "../Field.jsx";
import Panel from "../Panel.jsx";

function FlightsTab({ apiRequest }) {
  const [depIata, setDepIata] = useState("");
  const [arrIata, setArrIata] = useState("");
  const [flightDate, setFlightDate] = useState("");
  const [status, setStatus] = useState("");
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadFlights = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiRequest(
        `/flights?dep_iata=${depIata}&arr_iata=${arrIata}&flight_date=${flightDate}&status=${status}&limit=50&offset=0`
      );
      const items = Array.isArray(data) ? data : data?.items || [];
      setRows(items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Panel title="Flights (Read-only)">
      <div className="form-grid">
        <Field label="Dep IATA">
          <input value={depIata} onChange={(e) => setDepIata(e.target.value.toUpperCase())} />
        </Field>
        <Field label="Arr IATA">
          <input value={arrIata} onChange={(e) => setArrIata(e.target.value.toUpperCase())} />
        </Field>
        <Field label="Flight Date (YYYY-MM-DD)">
          <input value={flightDate} onChange={(e) => setFlightDate(e.target.value)} />
        </Field>
        <Field label="Status">
          <input value={status} onChange={(e) => setStatus(e.target.value)} />
        </Field>
      </div>
      <button onClick={loadFlights} disabled={loading}>{loading ? "Loading..." : "Load Flights"}</button>
      {error && <div className="error">{error}</div>}
      <DataTable rows={rows} />
    </Panel>
  );
}

export default FlightsTab;
