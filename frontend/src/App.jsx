import React, { useState } from "react";

import AuthForm from "./components/AuthForm.jsx";
import Modal from "./components/Modal.jsx";
import Tabs from "./components/Tabs.jsx";
import FlightsTab from "./components/tabs/FlightsTab.jsx";
import AirportsTab from "./components/tabs/AirportsTab.jsx";
import AirlinesTab from "./components/tabs/AirlinesTab.jsx";
import IngestTab from "./components/tabs/IngestTab.jsx";
import AssistantTab from "./components/tabs/AssistantTab.jsx";
import useApi from "./components/useApi.js";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("jwt") || "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [activeTab, setActiveTab] = useState("flights");
  const [status, setStatus] = useState("");
  const [oauthProcessing, setOauthProcessing] = useState(false);
  const [showGoogleModal, setShowGoogleModal] = useState(false);

  const { apiRequest } = useApi(token);

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatus("Logging in...");
    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      const jwt = data?.access_token;
      if (!jwt) throw new Error("No access_token returned");
      localStorage.setItem("jwt", jwt);
      setToken(jwt);
      setStatus("Logged in");
    } catch (err) {
      setStatus(`Login failed: ${err.message}`);
    }
  };

  const handleGoogleLogin = async () => {
    setStatus("Redirecting to Google...");
    try {
      const data = await apiRequest("/auth/google/url");
      if (!data?.url) throw new Error("Missing Google auth URL");
      window.location.href = data.url;
    } catch (err) {
      setStatus(`Google login failed: ${err.message}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt");
    setToken("");
    setStatus("Logged out");
  };

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const error = params.get("error");
    const hash = window.location.hash;
    if (hash && hash.startsWith("#token=")) {
      const jwt = decodeURIComponent(hash.replace("#token=", ""));
      if (jwt) {
        localStorage.setItem("jwt", jwt);
        setToken(jwt);
        setStatus("Logged in with Google");
        window.history.replaceState({}, "", window.location.pathname);
      }
      return;
    }
    if (!code && !error) return;

    if (error) {
      setStatus(`Google login error: ${error}`);
      return;
    }

    const exchange = async () => {
      setOauthProcessing(true);
      setStatus("Completing Google login...");
      try {
        const data = await apiRequest("/auth/google/token", {
          method: "POST",
          body: JSON.stringify({ code })
        });
        const jwt = data?.access_token;
        if (!jwt) throw new Error("No access_token returned");
        localStorage.setItem("jwt", jwt);
        setToken(jwt);
        setStatus("Logged in with Google");
        window.history.replaceState({}, "", window.location.pathname);
      } catch (err) {
        setStatus(`Google login failed: ${err.message}`);
      } finally {
        setOauthProcessing(false);
      }
    };

    exchange();
  }, []);

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Airport Dashboard</h1>
          <p className="muted">CRUD for airports/airlines. Read-only flights. Ingest from AviationStack.</p>
        </div>
        <div className="auth">
          <AuthForm
            token={token}
            email={email}
            password={password}
            onEmailChange={setEmail}
            onPasswordChange={setPassword}
            onLogin={handleLogin}
            onGoogle={handleGoogleLogin}
            onLogout={handleLogout}
            oauthProcessing={oauthProcessing}
            onOpenGoogleModal={() => setShowGoogleModal(true)}
          />
        </div>
      </header>

      <Tabs
        tabs={["flights", "airports", "airlines", "ingest", "assistant"]}
        active={activeTab}
        onChange={setActiveTab}
      />

      <section className="content">
        {status && <div className="status">{status}</div>}
        {activeTab === "flights" && <FlightsTab apiRequest={apiRequest} />}
        {activeTab === "airports" && <AirportsTab apiRequest={apiRequest} />}
        {activeTab === "airlines" && <AirlinesTab apiRequest={apiRequest} />}
        {activeTab === "ingest" && <IngestTab apiRequest={apiRequest} />}
        {activeTab === "assistant" && <AssistantTab apiRequest={apiRequest} />}
      </section>

      <Modal show={showGoogleModal} title="Continue with Google" onClose={() => setShowGoogleModal(false)}>
        <p className="muted">You will be redirected to Google to sign in. After consent, you will return here.</p>
        <div className="modal-actions">
          <button className="ghost" onClick={() => setShowGoogleModal(false)}>Cancel</button>
          <button onClick={handleGoogleLogin} disabled={oauthProcessing}>
            {oauthProcessing ? "Redirecting..." : "Continue"}
          </button>
        </div>
      </Modal>
    </div>
  );
}

export default App;
