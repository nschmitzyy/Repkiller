import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & STYLE ---
st.set_page_config(page_title="AURUM Elite Coach", layout="centered")

# Video-Hintergrund (Gold/Dunkel)
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(25%);
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 30px; padding: 40px;
        border: 1px solid #d4af37;
        color: #d4af37; text-align: center;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.3);
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: #d4af37; 
        color: black; font-weight: bold; border: none; padding: 12px;
    }}
    div[data-testid="stWidgetLabel"] p {{ color: #d4af37 !important; }}
    h1, h2, h3 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# Audio-Setup
audio_html_src = ""
if os.path.exists("alarm.mp3"):
    with open("alarm.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

# Session State Initialisierung
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"
if 'current_set' not in st.session_state:
    st.session_state.current_set = 1

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- SETUP PHASE ---
if st.session_state.phase == "SETUP":
    st.title("⚜️ AURUM ELITE")
    col1, col2 = st.columns(2)
    with col1:
        target_sets = st.number_input("Sätze gesamt", 1, 20, 3)
        target_reps = st.number_input("Reps pro Satz", 1, 100, 10)
    with col2:
        pause_time = st.slider("Pause (Sekunden)", 5, 180, 60)
        tempo_bpm = st.number_input("Metronom BPM", 20, 120, 45)
    
    if st.button("TRAINING STARTEN"):
        st.session_state.target_sets = target_sets
        st.session_state.target_reps = target_reps
        st.session_state.pause_time = pause_time
        st.session_state.tempo_bpm = tempo_bpm
        st.session_state.current_set = 1
        st.session_state.phase = "WORKOUT"
        st.rerun()

# --- WORKOUT PHASE ---
elif st.session_state.phase == "WORKOUT":
    # JavaScript Code Block
    js_code = f"""
    <div style="color: #d4af37; font-family: sans-serif; text-align: center;">
        <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
            <div><small>SATZ</small><h2 id="set-disp">{st.session_state.current_set} / {st.session_state.target_sets}</h2></div>
            <div><small>REPS</small><h2 id="rep-count">0 / {st.session_state.target_reps}</h2></div>
            <div><small>TIMER</small><h2 id="timer-text">--</h2></div>
        </div>
        
        <div style="position: relative; width: 100%; max-width: 500px; margin: 0 auto;">
            <video id="vid" style="width: 100%; border-radius: 20px; border: 2px solid #d4af37; background: #000;" autoplay playsinline></video>
            <div style="position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); width: 100%; display: flex; justify-content: center; gap: 10px;">
                <button onclick="toggleCamera()" style="background: rgba(212, 175, 55, 0.9); color: black; border: none; border-radius: 20px; padding: 8px 15px; font-weight: bold; cursor: pointer;">🔄 Kamera wechseln</button>
            </div>
        </div>
        <p id="status-text" style="font-size: 22px; font-weight: bold; margin-top: 15px;">BEREIT</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const tempoBpm = {st.session_state.tempo_bpm};
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        // Metronom Audio Context
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playTick() {{
            const osc = audioCtx.createOscillator();
            const envelope = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1000, audioCtx.currentTime);
            envelope.gain.setValueAtTime(0.1, audioCtx.currentTime);
            envelope.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
            osc.connect(envelope); envelope.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + 0.1);
        }}

        let reps = 0; let stage = "up"; let mode = "TRAINING";
        let useFrontCamera = true; let currentStream = null;
        let metronomeInterval = null;

        const video = document.getElementById('vid');
        const repDisplay = document.getElementById('rep-count');
        const timerDisplay = document.getElementById('timer-text');
        const statusDisplay = document.getElementById('status-text');

        async function initCamera() {{
            if (currentStream) currentStream.getTracks().forEach(t => t.stop());
            const constraints = {{ video: {{ facingMode: useFrontCamera ? "user" : "environment", width: 1280, height: 720 }} }};
            currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = currentStream;
            video.style.transform = useFrontCamera ? "scaleX(-1)" : "scaleX(1)";
            if (audioCtx.state === 'suspended') audioCtx.resume();
            startMetronome();
        }}

        function toggleCamera() {{ useFrontCamera = !useFrontCamera; initCamera(); }}

        function startMetronome() {{
            if (metronomeInterval) clearInterval(metronomeInterval);
            metronomeInterval = setInterval(() => {{ if (mode === "TRAINING") playTick(); }}, 60000 / tempoBpm);
        }}

        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.setOptions({{ modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 }});
        
        pose.onResults(results => {{
            if (!results.poseLandmarks) return;
            const lm = results.poseLandmarks;
            const angle = calculateAngle(lm[24], lm[26], lm[28]);

            if (mode === "TRAINING") {{
                if (angle > 160) stage = "up";
                if (angle < 90 && stage === "up") {{
                    stage = "down"; reps++;
                    repDisplay.innerText = reps + " / " + targetReps;
                    if (reps >= targetReps) startRest();
                }}
                statusDisplay.innerText = angle < 95 ? "TIEF GENUG!" : "GEH TIEFER...";
            }} else if (mode === "ALARM") {{
                if (angle < 140) {{ alarm.pause(); window.location.reload(); }} 
            }}
        }});

        function calculateAngle(a, b, c) {{
            let radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
            let angle = Math.abs(radians * 180.0 / Math.PI);
            if (angle > 180.0) angle = 360 - angle;
            return angle;
        }}

        function startRest() {{
            mode = "REST"; clearInterval(metronomeInterval);
            statusDisplay.innerText = "PAUSE!";
            let timeLeft = pauseTime;
            const itv = setInterval(() => {{
                timeLeft--; timerDisplay.innerText = timeLeft + "s";
                if (timeLeft <= 0) {{ clearInterval(itv); mode = "ALARM"; statusDisplay.innerText = "ALARM! SQUAT NOW!"; alarm.play(); }}
            }}, 1000);
        }}

        function calculateAngle(a, b, c) {{
            let radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
            let angle = Math.abs(radians * 180.0 / Math.PI);
            if (angle > 180.0) angle = 360 - angle;
            return angle;
        }}

        initCamera();
        async function detectionLoop() {{
            if (!video.paused) await pose.send({{image: video}});
            requestAnimationFrame(detectionLoop);
        }}
        video.onloadeddata = () => {{ detectionLoop(); }};
    </script>
    """
    components.html(js_code, height=650)
    
    if st.button("Training abbrechen"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
