import { useState } from "react";
import { sendChatMessage } from "../api";

export default function ChatPanel({ onCartChange }) {
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim()) return;

    const userMessage = message;
    setMessage("");
    setLoading(true);

    setChatLog((current) => [
      ...current,
      { role: "user", content: userMessage },
    ]);

    try {
      const response = await sendChatMessage(userMessage);
      onCartChange?.();

      setChatLog((current) => [
        ...current,
        {
          role: "assistant",
          content: response.message || JSON.stringify(response, null, 2),
        },
      ]);
    } catch (error) {
      setChatLog((current) => [
        ...current,
        {
          role: "assistant error",
          content: formatChatError(error),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chat-panel">
      <h2>Shopping Assistant</h2>

      <div className="chat-log">
        {chatLog.map((entry, index) => (
          <div key={index} className={`chat-message ${entry.role}`}>
            <strong>{entry.role}:</strong> {entry.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask for a product recommendation..."
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
    </section>
  );
}

function formatChatError(error) {
  const lines = [`${error.code || "chat_error"}: ${error.message}`];

  if (error.status) {
    lines.push(`HTTP status: ${error.status}`);
  }

  if (error.details && Object.keys(error.details).length > 0) {
    lines.push(`Details: ${JSON.stringify(error.details)}`);
  }

  return lines.join("\n");
}
