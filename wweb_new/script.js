const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;
  
  appendMessage("You", message);
  userInput.value = "";

  const response = await fetch("http://192.168.57.11:8080/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await response.json();
  data.responses.forEach((r) => appendMessage("NetBot", r.text));
});

function appendMessage(sender, text) {
  const messageEl = document.createElement("div");
  messageEl.className = sender;
  messageEl.innerHTML = `${text}`;
  chatBox.appendChild(messageEl);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function uploadPDF() {
  const fileInput = document.getElementById("pdf-upload");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a PDF file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://192.168.57.11:8080/upload-pdf", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    alert("❌ Upload failed: " + errorText);
    return;
  }

  const result = await response.json();
  alert("PDF uploaded and processed successfully!");
}
