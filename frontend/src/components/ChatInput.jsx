function ChatInput({ input, setInput, isLoading, onSubmit }) {
  return (
    <form className="input-bar" onSubmit={onSubmit}>
      <textarea
        placeholder="שאל אותי שאלה…"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={1}
      />
      <button type="submit" disabled={isLoading || !input.trim()}>
        {isLoading ? "שולח..." : "Send"}
      </button>
    </form>
  );
}

export default ChatInput;


