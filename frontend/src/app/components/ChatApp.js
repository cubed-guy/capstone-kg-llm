// pages/chat.js
"use client"
import { useState } from "react";
import axios from "axios";
import MarkdownRenderer from "./MarkdownRenderer";
import "../styles/globals.css";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSend = async () => {
    if (!query.trim()) return; // Avoid sending empty or just whitespace
    setLoading(true);

    try {
      const res = await axios.get("http://localhost:4000/sequence"  , {
        headers: {
          "sequence": query
        }
      });
      setResponses([...responses, res["data"]["choices"][0]["message"]["content"]]);
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponses([...responses, "Sorry, there was an error."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">capstone lol</h1>
      <div className="chat-box">
        <div className="response-container">
          {responses.map((response, index) => (
            <div key={index} className="response-box">
              <h2 className="response-title">Response {index + 1}</h2>
              <MarkdownRenderer markdownText={response}></MarkdownRenderer>
            </div>
          ))}
          {loading && <div className={`loading-box visible`} />}
        </div>
        <div className="input-container">
          <textarea
            value={query}
            onChange={handleQueryChange}
            placeholder="Enter your gene sequence here..."
            className="input"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`button ${loading ? "loading" : ""}`}
          >
            {loading ? "Sending..." : "Submit"}
          </button>
        </div>
      </div>
    </div>
  );
}