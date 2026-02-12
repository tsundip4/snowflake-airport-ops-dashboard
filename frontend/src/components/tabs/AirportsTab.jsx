import React, { useState } from "react";
import DataTable from "../DataTable.jsx";
import Field from "../Field.jsx";
import Panel from "../Panel.jsx";

function AirportsTab({ apiRequest }) {
  const [rows, setRows] = useState([]);
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [createForm, setCreateForm] = useState({ iata: "", name: "", icao: "", timezone: "" });
  const [updateForm, setUpdateForm] = useState({ iata: "", name: "", icao: "", timezone: "" });
  const [deleteIata, setDeleteIata] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiRequest(`/airports?limit=${limit}&offset=${offset}`);
      const items = Array.isArray(data) ? data : data?.items || [];
      setRows(items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const create = async () => {
    setError("");
    try {
      await apiRequest("/airports", {
        method: "POST",
        body: JSON.stringify({
          airport_iata: createForm.iata,
          airport_name: createForm.name,
          icao: createForm.icao,
          timezone: createForm.timezone
        })
      });
      setCreateForm({ iata: "", name: "", icao: "", timezone: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const update = async () => {
    setError("");
    try {
      await apiRequest(`/airports/${updateForm.iata}`, {
        method: "PUT",
        body: JSON.stringify({
          airport_name: updateForm.name || undefined,
          icao: updateForm.icao || undefined,
          timezone: updateForm.timezone || undefined
        })
      });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const remove = async () => {
    setError("");
    try {
      await apiRequest(`/airports/${deleteIata}`, { method: "DELETE" });
      setDeleteIata("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Panel title="Airports (CRUD)">
      <div className="row">
        <Field label="Limit">
          <input type="number" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
        </Field>
        <Field label="Offset">
          <input type="number" value={offset} onChange={(e) => setOffset(Number(e.target.value))} />
        </Field>
        <button onClick={load} disabled={loading}>{loading ? "Loading..." : "Load"}</button>
      </div>

      <div className="crud-grid">
        <div>
          <h3>Create</h3>
          <input placeholder="IATA" value={createForm.iata} onChange={(e) => setCreateForm({ ...createForm, iata: e.target.value.toUpperCase() })} />
          <input placeholder="Name" value={createForm.name} onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })} />
          <input placeholder="ICAO" value={createForm.icao} onChange={(e) => setCreateForm({ ...createForm, icao: e.target.value.toUpperCase() })} />
          <input placeholder="Timezone" value={createForm.timezone} onChange={(e) => setCreateForm({ ...createForm, timezone: e.target.value })} />
          <button onClick={create}>Create</button>
        </div>
        <div>
          <h3>Update</h3>
          <input placeholder="IATA (key)" value={updateForm.iata} onChange={(e) => setUpdateForm({ ...updateForm, iata: e.target.value.toUpperCase() })} />
          <input placeholder="Name" value={updateForm.name} onChange={(e) => setUpdateForm({ ...updateForm, name: e.target.value })} />
          <input placeholder="ICAO" value={updateForm.icao} onChange={(e) => setUpdateForm({ ...updateForm, icao: e.target.value.toUpperCase() })} />
          <input placeholder="Timezone" value={updateForm.timezone} onChange={(e) => setUpdateForm({ ...updateForm, timezone: e.target.value })} />
          <button onClick={update}>Update</button>
        </div>
        <div>
          <h3>Delete</h3>
          <input placeholder="IATA" value={deleteIata} onChange={(e) => setDeleteIata(e.target.value.toUpperCase())} />
          <button className="danger" onClick={remove}>Delete</button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      <DataTable rows={rows} />
    </Panel>
  );
}

export default AirportsTab;
