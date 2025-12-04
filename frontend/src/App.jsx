import { useState, useEffect } from "react";
import { askCopilot, API_URL } from "./api";
import "./App.css";
import ChatHeader from "./components/ChatHeader";
import ChatMessages from "./components/ChatMessages";
import ChatInput from "./components/ChatInput";
import ChatSidebar from "./components/ChatSidebar";
import ContextPanel from "./components/ContextPanel"; // ← חדש
import { uploadDocs } from "./api";


function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("unknown"); // "ok" | "error" | "unknown"
  const [isUploadingDocs, setIsUploadingDocs] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  
  // בדיקת חיבור ל-backend פעם אחת כשאפליקציה נטענת
  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (!res.ok) {
          setBackendStatus("error");
          return;
        }
        const data = await res.json();
        setBackendStatus(data.status === "ok" ? "ok" : "error");
      } catch (e) {
        console.error("Health check failed", e);
        setBackendStatus("error");
      }
    }

    checkHealth();
  }, []);


  // Get the currently active conversation
  const activeConversation = conversations.find(
    (conv) => conv.id === activeConversationId
  );
  const currentMessages = activeConversation?.messages || [];

  // ההודעה האחרונה של העוזר – בשביל הפאנל הימני
  const lastAssistantMessage = [...currentMessages]
    .reverse()
    .find((m) => m.role === "assistant");
  const activeCitations = lastAssistantMessage?.citations || [];

  // Create a new conversation – מחזיר את ה-ID החדש
  function handleNewConversation() {
    const newConversationId = Date.now().toString();
    const newConversation = {
      id: newConversationId,
      title: "New Conversation",
      messages: [],
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversationId);
    setInput("");
    setError("");
    return newConversationId;
  }

  // Select an existing conversation
  function handleSelectConversation(conversationId) {
    setActiveConversationId(conversationId);
    setInput("");
    setError("");
  }

  // Update a conversation's messages
  function updateConversationMessages(conversationId, newMessages) {
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversationId ? { ...conv, messages: newMessages } : conv
      )
    );
  }

  async function handleUploadDocs(files) {
    if (!files || files.length === 0) return;

    try {
      setIsUploadingDocs(true);
      setUploadError("");
      setUploadSuccess("");

      const result = await uploadDocs(files);
      setUploadSuccess(`הקבצים עלו בהצלחה (${result.files.length})`);
    } catch (err) {
      console.error("Upload error", err);
      setUploadError(err.message || "שגיאה בהעלאת הקבצים");
    } finally {
      setIsUploadingDocs(false);
    }
  }


  // Generate a title from the first user message (optional improvement)
  function generateTitle(messages) {
    const firstUserMsg = messages.find((m) => m.role === "user");
    if (firstUserMsg) {
      const text = firstUserMsg.text.substring(0, 50);
      return text.length < firstUserMsg.text.length ? text + "..." : text;
    }
    return "New Conversation";
  }

  // Update conversation title after first message
  function updateConversationTitle(conversationId) {
    setConversations((prev) =>
      prev.map((conv) => {
        if (conv.id === conversationId && conv.title === "New Conversation") {
          return {
            ...conv,
            title: generateTitle(conv.messages),
          };
        }
        return conv;
      })
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // אם אין שיחה פעילה – ניצור אחת ונשתמש ב-ID שלה עכשיו
    let conversationId = activeConversationId;
    if (!conversationId) {
      conversationId = handleNewConversation();
    }

    const userText = input.trim();

    // Add user message to the active conversation
    const previousMessages =
      conversations.find((c) => c.id === conversationId)?.messages || [];
    const updatedMessages = [
      ...previousMessages,
      { role: "user", text: userText },
    ];

    updateConversationMessages(conversationId, updatedMessages);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      // אין יותר mode ב-frontend – שולחים רק query
      const data = await askCopilot(userText);

      const messagesWithAssistant = [
        ...updatedMessages,
        {
          role: "assistant",
          text: data.answer || "No answer returned from server.",
          citations: data.citations || [],
        },
      ];

      updateConversationMessages(conversationId, messagesWithAssistant);

      // Update title after first message
      if (updatedMessages.length === 1) {
        updateConversationTitle(conversationId);
      }
    } catch (err) {
      console.error(err);
      setError("שגיאה בתקשורת עם השרת. בדוק שה-backend רץ ונסה שוב.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app-root">
      {/* ChatHeader כבר לא מקבל mode/setMode – המוח ב-backend מחליט */}
      <ChatHeader
       backendStatus={backendStatus} 
       onUploadDocs={handleUploadDocs}
       isUploadingDocs={isUploadingDocs}
       
       />

      {/* כאן נוסיף את הבאנרים של השגיאה/הצלחה */}
      {uploadError && (
        <div className="upload-banner upload-banner-error">
          {uploadError}
        </div>
      )}

      {uploadSuccess && (
        <div className="upload-banner upload-banner-success">
          {uploadSuccess}
        </div>
      )}
       

      <div className="app-body">
        <ChatSidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />

        <main className="chat-container">
          <section className="chat-main">
            <ChatMessages messages={currentMessages} isLoading={isLoading} />

            <ChatInput
              input={input}
              setInput={setInput}
              isLoading={isLoading}
              onSubmit={handleSubmit}
            />

            {error && <div className="error">{error}</div>}
          </section>

          {/* פאנל המקורות בצד ימין */}
          <ContextPanel citations={activeCitations} />
        </main>
      </div>
    </div>
  );
}

export default App;



