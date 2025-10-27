def home_ui(image_path: str):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>🎧 Talking Agent</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{
      background: #0f172a;
      color: white;
      font-family: Inter, sans-serif;
    }}

    .avatar-frame {{
      position: relative;
      width: 320px;
      height: 400px;
      border-radius: 1rem;
      overflow: hidden;
      box-shadow: 0 0 20px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 1rem;
    }}

    .avatar-frame img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      transition: transform 0.1s ease, filter 0.1s ease;
      border-radius: 1rem;
    }}

    .talking {{
      animation: talkAnim 0.25s infinite ease-in-out alternate;
    }}

    @keyframes talkAnim {{
      from {{
        transform: scaleY(1);
        filter: brightness(1);
      }}
      to {{
        transform: scaleY(1.02);
        filter: brightness(1.2);
      }}
    }}

    .beat-circle {{
      position: absolute;
      top: 50%;
      left: 50%;
      width: 100%;
      height: 100%;
      transform: translate(-50%, -50%);
      border-radius: 50%;
      border: 3px solid rgba(0, 255, 255, 0.5);
      animation: beat 1.2s infinite ease-in-out;
      opacity: 0;
    }}

    @keyframes beat {{
      0% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.8; }}
      50% {{ transform: translate(-50%, -50%) scale(1.1); opacity: 0.3; }}
      100% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.8; }}
    }}

    /* ✅ Hide the default audio controls but keep it functional */
    audio::-webkit-media-controls {{
      display: none !important;
    }}
    audio {{
      width: 0;
      height: 0;
      opacity: 0;
      position: absolute;
    }}
  </style>
</head>

<body class="flex flex-col items-center justify-center min-h-screen p-6">
  <h1 class="text-3xl font-bold mb-6">🎧 Talking Agent</h1>

  <div class="flex flex-col items-center mt-4">
    <div class="avatar-frame">
      <img id="avatarImg" src="{image_path}" alt="Avatar" />
      <div id="beatEffect" class="beat-circle"></div>
    </div>

    <audio id="agentAudio"></audio>

    <div class="flex flex-col items-center mt-6 w-full max-w-md">
      <textarea id="textInput" placeholder="Type your message..." rows="2"
        class="w-full p-2 rounded text-black"></textarea>
      <div class="flex gap-2 mt-2">
        <button id="sendText" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded">
          Send
        </button>
        <button id="speakBtn" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
          🎙️ Speak
        </button>
      </div>
    </div>
  </div>

  <script>
    const agentAudio = document.getElementById('agentAudio');
    const beatEffect = document.getElementById('beatEffect');
    const speakBtn = document.getElementById('speakBtn');
    const avatarImg = document.getElementById('avatarImg');

    // --- Greeting ---
    async function playGreeting() {{
      const formData = new FormData();
      formData.append('user_text', '');
      const res = await fetch('/talking_agent/', {{ method: 'POST', body: formData }});
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      agentAudio.src = url;
      agentAudio.loop = false;  // ✅ Play once only
      agentAudio.play();
    }}

    // --- Text Send ---
    document.getElementById('sendText').onclick = async () => {{
      const text = document.getElementById('textInput').value.trim();
      if (!text) return;
      const formData = new FormData();
      formData.append('user_text', text);
      const res = await fetch('/talking_agent/', {{ method: 'POST', body: formData }});
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      agentAudio.src = url;
      agentAudio.loop = false;  // ✅ Play once only
      agentAudio.play();
    }};

    // --- Speech Recording ---
    let mediaRecorder;
    let audioChunks = [];

    speakBtn.onclick = async () => {{
      if (mediaRecorder && mediaRecorder.state === 'recording') {{
        mediaRecorder.stop();
        speakBtn.textContent = "🎙️ Speak";
        speakBtn.classList.remove("bg-red-600");
      }} else {{
        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {{
          const blob = new Blob(audioChunks, {{ type: 'audio/wav' }});
          const formData = new FormData();
          formData.append('user_audio', blob, 'speech.wav');
          const res = await fetch('/talking_agent/', {{ method: 'POST', body: formData }});
          const responseBlob = await res.blob();
          const url = URL.createObjectURL(responseBlob);
          agentAudio.src = url;
          agentAudio.loop = false;  // ✅ Play once only
          agentAudio.play();
        }};
        mediaRecorder.start();
        speakBtn.textContent = "🛑 Stop";
        speakBtn.classList.add("bg-red-600");
      }}
    }};

    // --- Avatar animation synced with audio ---
    agentAudio.addEventListener('play', () => {{
      avatarImg.classList.add('talking');
      beatEffect.style.opacity = '1';
    }});
    agentAudio.addEventListener('pause', () => {{
      avatarImg.classList.remove('talking');
      beatEffect.style.opacity = '0';
    }});
    agentAudio.addEventListener('ended', () => {{
      avatarImg.classList.remove('talking');
      beatEffect.style.opacity = '0';
    }});

    // --- Auto-play greeting only once per session ---
    window.onload = () => {{
      if (!sessionStorage.getItem('greetingPlayed')) {{
        playGreeting();
        sessionStorage.setItem('greetingPlayed', 'true');
      }}
    }};
  </script>
</body>
</html>
"""
