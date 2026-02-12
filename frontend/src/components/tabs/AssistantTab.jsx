import { useMemo, useRef, useState } from "react";

const INITIAL_MESSAGE = {
  role: "assistant",
  text: "Ask me about the latest flights, gates, delays, or trends."
};

function AssistantTab({ apiRequest }) {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isSending,
    [input, isSending]
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    const question = (inputRef.current?.value || "").trim();
    if (!question || isSending) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    if (inputRef.current) {
      inputRef.current.value = "";
    }
    setError("");
    setIsSending(true);

    try {
      const result = await apiRequest("/ai/ask", {
        method: "POST",
        body: JSON.stringify({ question })
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: result?.answer || "No response." }
      ]);
    } catch (err) {
      setError(err.message || "Unable to reach the AI assistant.");
    } finally {
      setIsSending(false);
    }
  };

  const handleClear = () => {
    setMessages([INITIAL_MESSAGE]);
    setInput("");
    setError("");
  };

  return (
    <section className="panel chat-panel">
      <div className="panel-head">
        <div>
          <h3>Ops Assistant</h3>
          <p className="chat-subhead">Ask about the latest flights, gates, delays, or trends.</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>
            <span>{message.text}</span>
          </div>
        ))}
      </div>

      {isSending ? <div className="chat-loading">Loading...</div> : null}

      {error ? <div className="error chat-error">{error}</div> : null}

      <form className="chat-input" onSubmit={handleSubmit}>
        <textarea
          rows="2"
          ref={inputRef}
          onChange={(event) => setInput(event.target.value)}
          onInput={(event) => setInput(event.target.value)}
          placeholder="Ask about gates, delays, or next departures..."
        />
        <div className="chat-actions">
          <button type="button" onClick={handleClear} disabled={isSending} className="ghost">
            Clear
          </button>
          <button type="submit" disabled={!canSend}>
            {isSending ? "Sending..." : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default AssistantTab;
