import { useEffect, useState } from 'react';
import './App.css';
import FileUpload from './FileUpload.jsx';

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState("");
  const handleReset = async () => {
  try {
    const res = await fetch("http://localhost:8000/reset/", {
      method: "POST",
    });
    const data = await res.json();
    alert(data.detail || "Reset complete");
  } catch (error) {
    alert("Failed to reset memory");
  }
  };

  useEffect(() => {
    let sid = localStorage.getItem("session_id");
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem("session_id", sid);
    }
    setSessionId(sid);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages([...messages, userMessage]);
    setInput("");

    const res = await fetch("http://localhost:8000/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: input }),
    });

    const data = await res.json();
    if (data.response) {
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } else {
      setMessages(prev => [...prev, { role: "assistant", content: "Error: No response" }]);
    }
  };

  return (
    <div style={{ padding: "20px", backgroundColor: "#1e1e1e", color: "#fff", height: "100vh" }}>
      <h2 style={{ textAlign: "center" }}>Chat with LM Studio</h2>
      <FileUpload />
      <div style={{ backgroundColor: "#fff", color: "#000", borderRadius: "8px", padding: "20px", height: "60vh", overflowY: "auto", margin: "20px auto", width: "90%" }}>
        {messages.map((m, i) => <p key={i}><strong>{m.role}:</strong> {m.content}</p>)}
      </div>
      <div style={{ display: "flex", gap: "10px", width: "90%", margin: "0 auto" }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask a question" style={{ flex: 1, padding: "12px", fontSize: "16px", borderRadius: "6px" }} />
        <button onClick={sendMessage} style={{ padding: "12px 20px", backgroundColor: "#007bff", color: "white", borderRadius: "6px" }}>Send</button>
      </div>
      <button
      onClick={handleReset}
      style={{
        padding: "10px 20px",
        fontSize: "16px",
        borderRadius: "6px",
        backgroundColor: "#dc3545",
        color: "white",
        border: "none",
        cursor: "pointer",
        marginTop: "10px"
      }}
      >
        Reset Memory
    </button>

    </div>
  );
}

export default App;
