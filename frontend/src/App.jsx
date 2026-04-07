import { useState } from "react";

const API_URL = "http://localhost:8000/chat";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! Ask me to add tasks, events, or notes. Type 'help' to learn how to use me.",
    },
  ]);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content }),
      });

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error reaching backend." },
      ]);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>Multi-Agent Productivity Assistant</h1>
        <p>Hackathon-ready assistant for tasks, calendar, and notes.</p>
      </header>

      <main className="chat">
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <span>{message.content}</span>
            </div>
          ))}
        </div>

        <form className="composer" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type a message..."
          />
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  );
}
