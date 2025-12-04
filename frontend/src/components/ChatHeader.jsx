import { useRef } from "react";

function ChatHeader({ backendStatus, onUploadDocs, isUploadingDocs }) {
  const fileInputRef = useRef(null);

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    if (onUploadDocs) {
      onUploadDocs(files);
    }

    // כדי לאפשר בחירה מחדש של אותו קובץ אם רוצים
    event.target.value = "";
  };

  return (
    <header className="app-header">
      <div>
        <h1>Academic Copilot</h1>
        <p className="subtitle">
          Get A-grades with the AI that masters your courses, assignments, and exams.
        </p>
      </div>

      <div className="header-right">
        {/* כפתור העלאת קבצים */}
        <button
          type="button"
          className="upload-docs-btn"
          onClick={handleUploadClick}
          disabled={isUploadingDocs}
        >
          {isUploadingDocs ? "מעלה קבצים..." : "העלה PDF"}
        </button>

        {/* input חבוי לקבצים */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          multiple
          accept=".pdf,.txt"
          onChange={handleFileChange}
        />

        {/* סטטוס backend – זה החלק שהיה לך כבר */}
        <span
          className={
            "status-dot " +
            (backendStatus === "ok"
              ? "status-ok"
              : backendStatus === "error"
              ? "status-error"
              : "status-unknown")
          }
        />
        <span className="status-text">
          {backendStatus === "ok"
            ? "Connected to backend"
            : backendStatus === "error"
            ? "Backend not reachable"
            : "Checking backend…"}
        </span>
      </div>
    </header>
  );
}

export default ChatHeader;

