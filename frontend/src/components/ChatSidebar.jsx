function ChatSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}) {
  return (
    <aside className="chat-sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewConversation}>
          + New Chat
        </button>
      </div>

      <div className="conversations-list">
        {conversations.length === 0 ? (
          <div className="empty-conversations">No conversations yet</div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                activeConversationId === conversation.id ? "active" : ""
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="conversation-title">{conversation.title}</div>
              <div className="conversation-meta">
                {conversation.messages.length} messages
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default ChatSidebar;
