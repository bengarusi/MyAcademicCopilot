function ChatMessages({ messages, isLoading }) {
  return (
    <div className="messages">
      {messages.length === 0 && (
        <div className="empty-state">
          <h2>ברוך הבא ל-Academic Copilot 🎓</h2>
          <p>תכתוב שאלה על קורס, תרגיל או מושג שלא ברור לך.</p>
          <ul>
            <li>💡 "תסביר לי את BFS ו-DFS"</li>
            <li>📚 "סכם לי את שקופיות 10–20 במחברת של אלגוריתמים"</li>
            <li>✉️ "תנסח מייל למתרגל לגבי שאלה במטלה"</li>
          </ul>
        </div>
      )}

      {messages.map((msg, index) => (
        <div
          key={index}
          className={
            "message-row " +
            (msg.role === "user" ? "message-user" : "message-assistant")
          }
        >
          <div className="avatar">{msg.role === "user" ? "👤" : "🤖"}</div>
          <div className="bubble">
            <div className="bubble-text">
              {msg.text.split("\n").map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>

            {msg.citations && msg.citations.length > 0 && (
              <div className="citations">
                מקורות:
                {msg.citations.map((c, i) => (
                  <span key={i} className="citation-pill">
                    {c}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message-row message-assistant">
          <div className="avatar">🤖</div>
          <div className="bubble typing">Academic Copilot חושב…</div>
        </div>
      )}
    </div>
  );
}

export default ChatMessages;


