// document.addEventListener('DOMContentLoaded', function() {
//   // DOM Elements
//   const authModal = document.getElementById('auth-modal');
//   const loginForm = document.getElementById('login-form');
//   const registerForm = document.getElementById('register-form');
//   const switchToRegister = document.getElementById('switch-to-register');
//   const switchToLogin = document.getElementById('switch-to-login');
//   const closeModal = document.querySelector('.close-modal');
//   const appContainer = document.getElementById('app-container');
//   const welcomeMessage = document.getElementById('welcome-message');
//   const logoutBtn = document.getElementById('logout-btn');
//   const showHistoryBtn = document.getElementById('show-history-btn');
//   const historyPanel = document.getElementById('history-panel');
//   const conversationList = document.getElementById('conversation-list');
  
//   // Chat elements
//   const chatBox = document.getElementById('chat-box');
//   const chatForm = document.getElementById('chat-form');
//   const userInput = document.getElementById('user-input');
//   const pdfUpload = document.getElementById('pdf-upload');
//   const uploadBtn = document.getElementById('upload-btn');
//   const statusMessage = document.getElementById('status-message');
  
//   const API_BASE_URL = "http://192.168.254.100:8080";
//   let currentConversation = [];
//   let isAuthenticated = false;

//   // Initialize the app
//   init();

//   async function init() {
//     // Check authentication status
//     const authStatus = await checkAuth();
//     if (authStatus.authenticated) {
//       isAuthenticated = true;
//       welcomeMessage.textContent = `Welcome, ${authStatus.username}`;
//       appContainer.style.display = 'block';
//       loadConversations();
//     } else {
//       authModal.style.display = 'flex';
//     }
//   }

//   // Authentication Functions
//   async function checkAuth() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/check-auth`, {
//         credentials: 'include'
//       });
//       return await response.json();
//     } catch (error) {
//       console.error('Auth check failed:', error);
//       return { authenticated: false };
//     }
//   }

//   async function login(username, password) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/login`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         credentials: 'include',
//         body: JSON.stringify({ username, password })
//       });
      
//       const data = await response.json();
//       if (response.ok) {
//         isAuthenticated = true;
//         authModal.style.display = 'none';
//         appContainer.style.display = 'block';
//         welcomeMessage.textContent = `Welcome, ${username}`;
//         loadConversations();
//       } else {
//         showStatus(data.error || 'Login failed', 'error');
//       }
//     } catch (error) {
//       showStatus('Login failed. Please try again.', 'error');
//       console.error('Login error:', error);
//     }
//   }

//   async function register(username, email, password) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/register`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ username, email, password })
//       });
      
//       const data = await response.json();
//       if (response.ok) {
//         showStatus('Registration successful! Please login.', 'success');
//         switchToLogin.click();
//       } else {
//         showStatus(data.error || 'Registration failed', 'error');
//       }
//     } catch (error) {
//       showStatus('Registration failed. Please try again.', 'error');
//       console.error('Registration error:', error);
//     }
//   }

//   async function logout() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/logout`, {
//         method: 'POST',
//         credentials: 'include'
//       });
      
//       if (response.ok) {
//         isAuthenticated = false;
//         appContainer.style.display = 'none';
//         authModal.style.display = 'flex';
//         loginForm.classList.add('active');
//         registerForm.classList.remove('active');
//         currentConversation = [];
//         chatBox.innerHTML = '';
//       }
//     } catch (error) {
//       console.error('Logout error:', error);
//     }
//   }

//   // Conversation History Functions
//   async function loadConversations() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/get-conversations`, {
//         credentials: 'include'
//       });
      
//       if (response.ok) {
//         const data = await response.json();
//         renderConversationList(data.conversations);
//       }
//     } catch (error) {
//       console.error('Failed to load conversations:', error);
//     }
//   }

//   function renderConversationList(conversations) {
//     conversationList.innerHTML = '';
    
//     if (conversations.length === 0) {
//       conversationList.innerHTML = '<p>No previous conversations</p>';
//       return;
//     }
    
//     conversations.forEach(conv => {
//       const convData = JSON.parse(conv.conversation_data);
//       const firstMessage = convData.length > 0 ? convData[0].text : 'Empty conversation';
//       const date = new Date(conv.updated_at).toLocaleString();
      
//       const convItem = document.createElement('div');
//       convItem.className = 'conversation-item';
//       convItem.innerHTML = `
//         <p><strong>${date}</strong></p>
//         <p>${firstMessage.substring(0, 50)}${firstMessage.length > 50 ? '...' : ''}</p>
//       `;
      
//       convItem.addEventListener('click', () => loadConversation(conv.id, convData));
//       conversationList.appendChild(convItem);
//     });
//   }

//   function loadConversation(conversationId, conversationData) {
//     chatBox.innerHTML = '';
//     currentConversation = [];
    
//     conversationData.forEach(msg => {
//       appendMessage(msg.sender, msg.text, msg.timestamp);
//       currentConversation.push(msg);
//     });
    
//     historyPanel.style.display = 'none';
//   }

//   async function saveConversation() {
//     if (currentConversation.length === 0) return;
    
//     try {
//       const response = await fetch(`${API_BASE_URL}/save-conversation`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         credentials: 'include',
//         body: JSON.stringify({ conversation: currentConversation })
//       });
      
//       if (response.ok) {
//         loadConversations();
//       }
//     } catch (error) {
//       console.error('Failed to save conversation:', error);
//     }
//   }

//   // Chat Functions
//   function appendMessage(sender, text, timestamp = null) {
//     const messageDiv = document.createElement('div');
//     messageDiv.classList.add('message');
//     messageDiv.classList.add(sender === 'You' ? 'user-message' : 'bot-message');
    
//     const now = timestamp ? new Date(timestamp) : new Date();
//     const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
//     messageDiv.innerHTML = `
//       ${text}
//       <span class="message-time">${sender} • ${timeString}</span>
//     `;
    
//     chatBox.appendChild(messageDiv);
//     chatBox.scrollTop = chatBox.scrollHeight;
    
//     // Add to current conversation
//     if (isAuthenticated) {
//       currentConversation.push({
//         sender,
//         text,
//         timestamp: now.toISOString()
//       });
//     }
//   }

//   function showTyping() {
//     const typingDiv = document.createElement('div');
//     typingDiv.classList.add('typing-indicator');
//     typingDiv.id = 'typing-indicator';
//     typingDiv.innerHTML = `
//       <div class="typing-dot"></div>
//       <div class="typing-dot"></div>
//       <div class="typing-dot"></div>
//     `;
//     chatBox.appendChild(typingDiv);
//     chatBox.scrollTop = chatBox.scrollHeight;
//   }

//   function hideTyping() {
//     const typingIndicator = document.getElementById('typing-indicator');
//     if (typingIndicator) {
//       typingIndicator.remove();
//     }
//   }

//   function showStatus(message, type = '') {
//     statusMessage.textContent = message;
//     statusMessage.className = 'status-message';
//     if (type) {
//       statusMessage.classList.add(type);
//     }
//   }

//   // Event Listeners
//   // Auth form events
//   document.getElementById('login-form-element').addEventListener('submit', function(e) {
//     e.preventDefault();
//     const username = document.getElementById('login-username').value;
//     const password = document.getElementById('login-password').value;
//     login(username, password);
//   });

//   document.getElementById('register-form-element').addEventListener('submit', function(e) {
//     e.preventDefault();
//     const username = document.getElementById('register-username').value;
//     const email = document.getElementById('register-email').value;
//     const password = document.getElementById('register-password').value;
//     register(username, email, password);
//   });

//   switchToRegister.addEventListener('click', function(e) {
//     e.preventDefault();
//     loginForm.classList.remove('active');
//     registerForm.classList.add('active');
//   });

//   switchToLogin.addEventListener('click', function(e) {
//     e.preventDefault();
//     registerForm.classList.remove('active');
//     loginForm.classList.add('active');
//   });

//   closeModal.addEventListener('click', function() {
//     authModal.style.display = 'none';
//   });

//   logoutBtn.addEventListener('click', logout);

//   // Chat events
//   chatForm.addEventListener('submit', async function(e) {
//     e.preventDefault();
//     const message = userInput.value.trim();
//     if (!message) return;
    
//     appendMessage('You', message);
//     userInput.value = '';
    
//     showTyping();
    
//     try {
//       const response = await fetch(`${API_BASE_URL}/chat`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: 'include',
//         body: JSON.stringify({ message })
//       });

//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//       }

//       const data = await response.json();
//       hideTyping();
      
//       if (data.responses && Array.isArray(data.responses)) {
//         data.responses.forEach(response => {
//           if (response.text) {
//             appendMessage('NetBot', response.text);
//           } else if (response.image) {
//             appendMessage('NetBot', `<img src="${response.image}" alt="Bot response image" style="max-width: 100%;">`);
//           }
//         });
        
//         // Save conversation after each interaction
//         if (isAuthenticated) {
//           saveConversation();
//         }
//       } else {
//         appendMessage('NetBot', "I received your message but didn't get a proper response.");
//       }
//     } catch (error) {
//       hideTyping();
//       console.error('Error:', error);
//       appendMessage('NetBot', "Sorry, I encountered an error processing your request.");
//       showStatus('Error communicating with the server', 'error');
//     }
//   });

//   // Upload events
//   uploadBtn.addEventListener('click', async function() {
//     const file = pdfUpload.files[0];
//     if (!file) {
//       showStatus('Please select a file first', 'error');
//       return;
//     }
    
//     showStatus('Uploading and processing document... This may take a few minutes.', '');
    
//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
//         method: "POST",
//         credentials: 'include',
//         body: formData,
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.error || 'Upload failed');
//       }

//       const result = await response.json();
//       showStatus('Document processed and AI model trained successfully!', 'success');
//       appendMessage('NetBot', `I've processed your document "${file.name}". You can now ask me questions about it.`);
      
//       // Save this interaction
//       if (isAuthenticated) {
//         saveConversation();
//       }
//     } catch (error) {
//       console.error('Upload error:', error);
//       showStatus(`Processing failed: ${error.message}`, 'error');
//       appendMessage('NetBot', "Sorry, I couldn't process that document. Please try another file.");
//     }
//   });

//   // History panel toggle
//   showHistoryBtn.addEventListener('click', function() {
//     historyPanel.style.display = historyPanel.style.display === 'block' ? 'none' : 'block';
//   });

//   // Initial welcome message
//   if (isAuthenticated) {
//     appendMessage('NetBot', "Hello! I'm your AI assistant. How can I help you today?");
//   }
// });

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

    const API_BASE_URL = "http://192.168.254.100:8080";

    // Show auth modal by default
    authModal.style.display = 'flex';

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
    closeModal.addEventListener('click', function() {
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
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          authModal.style.display = 'none';
          appContainer.style.display = 'block';
          welcomeMessage.textContent = `Welcome, ${username}`;
          userInput.disabled = false;
          sendBtn.disabled = false;
          pdfUpload.disabled = false;
          uploadBtn.disabled = false;
          
          appendMessage('NetBot', `Hello ${username}! How can I assist you with your networking needs today?`, false);
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
    logoutBtn.addEventListener('click', async function() {
      try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
          method: "POST",
          credentials: 'include'
        });

        if (response.ok) {
          appContainer.style.display = 'none';
          authModal.style.display = 'flex';
          document.getElementById('login-form').classList.add('active');
          document.getElementById('register-form').classList.remove('active');
          chatBox.innerHTML = '<div class="message bot-message">Hello! I\'m NetBot Pro, your AI networking assistant. Please login to start chatting.<span class="message-time">NetBot • Just now</span></div>';
          userInput.disabled = true;
          sendBtn.disabled = true;
          pdfUpload.disabled = true;
          uploadBtn.disabled = true;
        }
      } catch (error) {
        console.error('Logout error:', error);
      }
    });

    // Chat form submission
    chatForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const message = userInput.value.trim();
      if (!message) return;
      
      appendMessage('You', message, true);
      userInput.value = '';
      
      showTyping();
      
      try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: 'include',
          body: JSON.stringify({ message })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        hideTyping();
        
        if (data.responses && Array.isArray(data.responses)) {
          data.responses.forEach(response => {
            if (response.text) {
              appendMessage('NetBot', response.text, false);
            } else if (response.image) {
              appendMessage('NetBot', `<img src="${response.image}" alt="Bot response image" style="max-width: 100%;">`, false);
            }
          });
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
    uploadBtn.addEventListener('click', async function() {
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
          credentials: 'include',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Upload failed');
        }

        const result = await response.json();
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

    // Check authentication status on page load
    async function checkAuth() {
      try {
        const response = await fetch(`${API_BASE_URL}/check-auth`, {
          credentials: 'include'
        });
        const data = await response.json();
        
        if (data.authenticated) {
          authModal.style.display = 'none';
          appContainer.style.display = 'block';
          welcomeMessage.textContent = `Welcome, ${data.username}`;
          userInput.disabled = false;
          sendBtn.disabled = false;
          pdfUpload.disabled = false;
          uploadBtn.disabled = false;
          appendMessage('NetBot', `Welcome back ${data.username}! How can I help you today?`, false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    }

    checkAuth();
  });