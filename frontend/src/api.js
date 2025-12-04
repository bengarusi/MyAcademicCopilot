// src/api.js
export const API_URL = "http://localhost:8000";

export async function askCopilot(query) {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, mode: "answer" }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Server error: ${response.status} - ${text}`);
  }

  // מחזיר { answer, citations, mode }
  return response.json();
}

export async function uploadDocs(files) {
  const formData = new FormData();

  // files זה Array או FileList
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_URL}/upload-docs`, {
    method: "POST",
    body: formData, // חשוב: לא לשים Content-Type ידנית
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Upload failed: ${response.status} - ${text}`);
  }

  return response.json(); // { status: "ok", files: [...] }
}
