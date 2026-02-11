from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# This list stores our chat history in memory
# Each message is a dict: {'sender': 'Name', 'text': 'Hello', 'time': '10:00 AM'}
#Comment by Rakesh
messages = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anonymous Chat Hub</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #2c3e50; margin: 0; display: flex; justify-content: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 600px; background: #ecf0f1; display: flex; flex-direction: column; height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        
        /* Header */
        header { background: #34495e; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 1.2rem; }

        /* Chat History Area */
        #chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
        
        /* Message Bubbles */
        .message { padding: 10px 15px; border-radius: 20px; max-width: 80%; word-wrap: break-word; font-size: 0.95rem; }
        .message.mine { background: #3498db; color: white; align-self: flex-end; border-bottom-right-radius: 0; }
        .message.others { background: #fff; color: #333; align-self: flex-start; border-bottom-left-radius: 0; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        
        .meta { font-size: 0.75rem; margin-bottom: 2px; opacity: 0.8; }
        .meta strong { margin-right: 5px; }

        /* Input Area */
        .input-area { padding: 15px; background: white; border-top: 1px solid #ddd; display: flex; gap: 10px; }
        input[type="text"] { padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none; }
        #username { width: 80px; text-align: center; background: #f9f9f9; }
        #msg-input { flex: 1; }
        button { padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; }
        button:hover { background: #2ecc71; }
    </style>
</head>
<body>

    <div class="chat-container">
        <header>The Hub</header>
        <div id="chat-window">
            </div>
        <div class="input-area">
            <input type="text" id="username" placeholder="Name" value="Anon">
            <input type="text" id="msg-input" placeholder="Type a message..." autocomplete="off">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        const msgInput = document.getElementById('msg-input');
        const usernameInput = document.getElementById('username');
        
        let lastMessageCount = 0;

        // Generate a random ID for this session to know which messages are "mine"
        const mySessionId = Math.random().toString(36).substr(2, 9);

        // 1. Send Message
        function sendMessage() {
            const text = msgInput.value.trim();
            const name = usernameInput.value.trim() || "Anon";
            
            if (!text) return;

            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: text, 
                    sender: name, 
                    session_id: mySessionId 
                })
            }).then(() => {
                msgInput.value = ''; // Clear input
                fetchMessages(); // Refresh immediately
            });
        }

        // Allow pressing "Enter" to send
        msgInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") sendMessage();
        });

        // 2. Fetch Messages
        function fetchMessages() {
            fetch('/get_messages')
                .then(r => r.json())
                .then(data => {
                    // Only update if there are new messages
                    if (data.length > lastMessageCount) {
                        chatWindow.innerHTML = ''; // Simple clear and redraw
                        
                        data.forEach(msg => {
                            const div = document.createElement('div');
                            // Check if the message is mine or someone else's
                            const type = (msg.session_id === mySessionId) ? 'mine' : 'others';
                            
                            div.className = `message ${type}`;
                            div.innerHTML = `
                                <div class="meta"><strong>${msg.sender}</strong> ${msg.time}</div>
                                <div>${msg.text}</div>
                            `;
                            chatWindow.appendChild(div);
                        });

                        // Scroll to bottom
                        chatWindow.scrollTop = chatWindow.scrollHeight;
                        lastMessageCount = data.length;
                    }
                });
        }

        // Poll every 1 second
        setInterval(fetchMessages, 1000);
        fetchMessages(); // Initial load
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    # Add a timestamp
    now = datetime.now().strftime("%H:%M")
    
    new_msg = {
        'text': data.get('text'),
        'sender': data.get('sender'),
        'session_id': data.get('session_id'),
        'time': now
    }
    messages.append(new_msg)
    
    # Optional: Keep only last 50 messages to save memory
    if len(messages) > 50:
        messages.pop(0)
        
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Run on port 8000
    app.run(host='0.0.0.0', port=8000, debug=True)
