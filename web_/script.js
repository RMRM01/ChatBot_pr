document.addEventListener('DOMContentLoaded', function() {
  // DOM Elements
  const authModal = document.getElementById('auth-modal');
  const loginForm = document.getElementById('login-form-element');
  const registerForm = document.getElementById('register-form-element');
  const switchToRegister = document.getElementById('switch-to-register');
  const switchToLogin = document.getElementById('switch-to-login');
  const closeModal = document.querySelector('.close-modal');
  const appContainer = document.getElementById('app-container');
  const welcomeMessage = document.getElementById('welcome-message');
  const logoutBtn = document.getElementById('logout-btn');
  const chatBox = document.getElementById('chat-box');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const pdfUpload = document.getElementById('pdf-upload');
  const uploadBtn = document.getElementById('upload-btn');
  const statusMessage = document.getElementById('status-message');

  // const API_BASE_URL = "http://192.168.254.100:8080";
   const API_BASE_URL = "http://10.10.122.56:8080";

  // Helper: show or hide UI based on login state
  function updateUIForUser(user) {
    if (user) {
      authModal.style.display = 'none';
      appContainer.style.display = 'block';
      welcomeMessage.textContent = `Welcome, ${user.username}`;
      userInput.disabled = false;
      sendBtn.disabled = false;
      pdfUpload.disabled = false;
      uploadBtn.disabled = false;
      appendMessage('NetBot', `Hello ${user.username}! How can I assist you today?`, false);
    } else {
      authModal.style.display = 'flex';
      appContainer.style.display = 'none';
      document.getElementById('login-form').classList.add('active');
      document.getElementById('register-form').classList.remove('active');
      chatBox.innerHTML = '<div class="message bot-message">Hello! I\'m NetBot Pro, your AI networking assistant. Please login to start chatting.<span class="message-time">NetBot • Just now</span></div>';
      userInput.disabled = true;
      sendBtn.disabled = true;
      pdfUpload.disabled = true;
      uploadBtn.disabled = true;
      welcomeMessage.textContent = '';
    }
  }

  //save to the database 
async function saveMessageToBackend(sender, message, userId) {
  if (!sender || !message || !userId) {
    console.error('sender, message, and userId are all required');
    return;
  }

  const conversation = {
    messages: [
      {
        text: message,
        sender: sender
      }
    ]
  };
  console.log(conversation)

  try {
    const response = await fetch(`${API_BASE_URL}/save-conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        conversation: conversation
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.log("fuc****")
      throw new Error(errorData.error || 'Failed to save message');
    }

    const data = await response.json();
    console.log('Message saved successfully:', data.message);
  } catch (error) {
    console.error('Error saving message:', error.message);
  }
}
// get data from data base 
async function loadConversations(userId) {
  if (!userId) {
    console.error("User ID is required to load conversations");
    return;
  }

  try {
    const response = await fetch(`http://10.10.122.56:8080/get-conversations?user_id=${encodeURIComponent(userId)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch conversations: ${response.status}`);
    }
    const data = await response.json();

    if (!data.conversations || data.conversations.length === 0) {
      console.log("No conversations found for this user.");
      return;
    }
    if (data.conversations && Array.isArray(data.conversations)) {
      data.conversations.forEach(conversation => {
      // Parse the JSON string stored in DB
        const conversationObj = JSON.parse(conversation.conversation_data);

        if (conversationObj.messages && Array.isArray(conversationObj.messages)) {
          conversationObj.messages.forEach(msg => {
            const isUser = (msg.sender === 'user');
              appendMessage(isUser ? 'You' : 'NetBot', msg.text, isUser);
          });
    }
  });
      } 
else {
  console.log("No conversations found.");
}
}
catch (error) {
    console.error("Error loading conversations:", error);
  }
}

  // Try to restore user from localStorage on page load
  const storedUser = JSON.parse(localStorage.getItem('user'));
  updateUIForUser(storedUser);

  // Switch between login and register forms
  switchToRegister.addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('register-form').classList.add('active');
  });

  switchToLogin.addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('register-form').classList.remove('active');
    document.getElementById('login-form').classList.add('active');
  });

  // Close modal
  closeModal.addEventListener('click', function(e) {
      e.preventDefault();  // Must be first!
  console.log('Login form submit intercepted');
    authModal.style.display = 'none';
  });

  // Login form submission
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        // removed credentials
      });

      if (response.ok) {
        alert("Welcome!")
        const data = await response.json();
        console.log(data.user.id)
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('user_id', data.user.id);
        updateUIForUser(data.user);
        loadConversations(data.user.id)
      } else {
        const errorData = await response.json();
        showStatus(errorData.error || 'Login failed', 'error');
      }
    } catch (error) {
      showStatus('Login failed. Please try again.', 'error');
      console.error('Login error:', error);
    }
  });

  // Register form submission
  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    console.log("ok")
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });

      if (response.ok) {
        showStatus('Registration successful! Please login.', 'success');
        document.getElementById('register-form').classList.remove('active');
        document.getElementById('login-form').classList.add('active');
        document.getElementById('login-username').value = username;
        document.getElementById('login-password').value = password;
      } else {
        const errorData = await response.json();
        showStatus(errorData.error || 'Registration failed', 'error');
      }
    } catch (error) {
      showStatus('Registration failed. Please try again.', 'error');
      console.error('Registration error:', error);
    }
  });

  // Logout
  logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
    localStorage.removeItem('user');
    updateUIForUser(null);
  });

  // Chat form submission
  chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('You', message, true);
    user_id=localStorage.getItem('user_id')
    

    userInput.value = '';

    //showing typing
    showTyping();
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      hideTyping();

      if (data.responses && Array.isArray(data.responses)) {
        if (data.responses.length > 0) {
          data.responses.forEach(response => {
            if (response.text) {
              
              appendMessage('NetBot', response.text, false);
            } else if (response.image) {
              appendMessage('NetBot', `<img src="${response.image}" alt="Bot response image" style="max-width: 100%;">`, false);
            }
          });
        } else {
          appendMessage('NetBot', "I don't have a answer to that question, If you want i can find the answer. if yes, type: find answer", false);
        }
      } else {
        appendMessage('NetBot', "I received your message but didn't get a proper response.", false);
      }
    } catch (error) {
      hideTyping();
      console.error('Error:', error);
      appendMessage('NetBot', "Sorry, I encountered an error processing your request.", false);
      showStatus('Error communicating with the server', 'error');
    }
  });

  // Upload button click
  uploadBtn.addEventListener('click', async function(e) {
    e.preventDefault();
    const file = pdfUpload.files[0];
    if (!file) {
      showStatus('Please select a file first', 'error');
      return;
    }

    showStatus('Uploading document...', '');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      // const result = await response.json();
      // console.log(result);
      showStatus('Document uploaded and processed successfully!', 'success');
      appendMessage('NetBot', `I've processed your document "${file.name}". You can now ask me questions about its content.`, false);
    } catch (error) {
      console.error('Upload error:', error);
      showStatus(`Upload failed: ${error.message}`, 'error');
      appendMessage('NetBot', "Sorry, I couldn't process that document. Please try another file.", false);
    }
  });

  // Helper functions
  function appendMessage(sender, text, isUser) {
    user_id=localStorage.getItem('user_id')
    speech="";
    if(sender == "You")
    {
      speech= "user";
    }
    else{
      speech="bot"
    }
    saveMessageToBackend(speech, text, user_id);
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');

    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
      ${text}
      <span class="message-time">${sender} • ${timeString}</span>
    `;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('typing-indicator');
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    `;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function hideTyping() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  function showStatus(message, type = '') {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message';
    if (type) {
      statusMessage.classList.add(type);
    }
  }
});
