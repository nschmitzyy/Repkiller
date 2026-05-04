import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & LUXURY DESIGN ---
st.set_page_config(page_title="AURUM PRESTIGE; your about to get shredded.", layout="centered")

# Hintergrundbild
BG_IMAGE_URL = "https://images.unsplash.com/photo-1550345332-09e3ac987658?q=80&w=2000"

# --- CSS RESET & STYLING ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* 1. RADIKALER RESET DES CONTAINERS */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        max-width: 100% !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    /* 2. HINTERGRUND */
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -2; object-fit: cover; 
        background: url('{BG_IMAGE_URL}') center/cover no-repeat;
        filter: brightness(25%) grayscale(100%);
    }}
    
    .stApp {{ background: transparent !important; }}

    /* 3. FIXIERTER LUXURY HEADER */
    .luxury-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 80px;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .luxury-header h1 {{
        margin: 0 !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.6rem !important;
        letter-spacing: 6px !important;
        color: #ffffff !important;
        text-transform: uppercase;
    }}

    /* 4. MAIN CARD */
    .main-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-radius: 40px; 
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.9);
        font-family: 'Inter', sans-serif;
        margin-top: 110px; /* Präziser Abstand zum Header */
        margin-bottom: 50px;
        animation: fadeIn 1.5s ease;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* 5. BUTTONS & INPUTS */
    .stButton>button {{
        width: 100%; border-radius: 0px;
        background: #ffffff; color: #000000; font-weight: 700; 
        border: none; padding: 15px; letter-spacing: 2px;
        transition: all 0.4s ease; text-transform: uppercase;
    }}
    .stButton>button:hover {{ background: #dddddd; transform: scale(1.01); }}
    
    div[data-testid="stWidgetLabel"] p {{ color: #ffffff !important; opacity: 0.8; }}
    input {{ background: rgba(255,255,255,0.05) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; }}
    </style>
    
    <div id="bgVideo"></div>
    <div class="luxury-header">
        <h1>AURUM PRESTIGE</h1>
    </div>
    """, unsafe_allow_html=True)

# Audio-Setup
audio_html_src = ""
if os.path.exists("alarm.mp3"):
    with open("alarm.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

# Session State
if 'phase' not in st.session_state: st.session_state.phase = "SETUP"
if 'current_set' not in st.session_state: st.session_state.current_set = 1

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- PHASE: SETUP ---
if st.session_state.phase == "SETUP":
    st.write("ELITE PERFORMANCE CONFIGURATION")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        target_sets = st.number_input("SETS", 1, 20, 3)
        target_reps = st.number_input("REPS", 1, 100, 10)
    with col2:
        pause_time = st.slider("REST (SEC)", 5, 180, 60)
        tempo_bpm = st.number_input("METRONOME BPM", 20, 120, 45)
    
    if st.button("INITIALIZE SESSION"):
        st.session_state.target_sets = target_sets
        st.session_state.target_reps = target_reps
        st.session_state.pause_time = pause_time
        st.session_state.tempo_bpm = tempo_bpm
        st.session_state.phase = "WORKOUT"
        st.rerun()

# --- PHASE: WORKOUT ---
elif st.session_state.phase == "WORKOUT":
    js_code = f"""
    <div style="color: white; font-family: 'Inter', sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
            <div><small style="letter-spacing: 2px;">SET</small><h2 style="margin:0; font-family:'Playfair Display';">{st.session_state.current_set}/{st.session_state.target_sets}</h2></div>
            <div><small style="letter-spacing: 2px;">REPS</small><h2 id="rep-count" style="margin:0; font-family:'Playfair Display';">0/{st.session_state.target_reps}</h2></div>
            <div><small style="letter-spacing: 2px;">TIMER</small><h2 id="timer-text" style="margin:0; font-family:'Playfair Display';">--</h2></div>
        </div>
        
        <div style="position: relative; width: 100%; border: 1px solid rgba(255,255,255,0.2);">
            <video id="vid" style="width: 100%; filter: grayscale(100%) contrast(1.1); background: #000;" autoplay playsinline></video>
            <button onclick="toggleCamera()" style="position: absolute; top: 10px; right: 10px; background: white; color: black; border: none; padding: 5px 12px; font-size: 10px; font-weight: bold; cursor: pointer;">SWITCH CAMERA</button>
        </div>
        
        <p id="status-text" style="font-size: 16px; letter-spacing: 3px; margin-top: 20px; text-transform: uppercase; font-weight: 300;">SYNCING POSE...</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const tempoBpm = {st.session_state.tempo_bpm};
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playTick() {{
            const osc = audioCtx.createOscillator();
            const env = audioCtx.createGain();
            osc.frequency.setValueAtTime(1000, audioCtx.currentTime);
            env.gain.setValueAtTime(0.04, audioCtx.currentTime);
            env.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
            osc.connect(env); env.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + 0.05);
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
                    repDisplay.innerText = reps + "/" + targetReps;
                    if (reps >= targetReps) startRest();
                }}
                statusDisplay.innerText = angle < 95 ? "DEPTH REACHED" : "LOWER";
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
            statusDisplay.innerText = "REST";
            let timeLeft = pauseTime;
            const itv = setInterval(() => {{
                timeLeft--; timerDisplay.innerText = timeLeft + "s";
                if (timeLeft <= 0) {{ clearInterval(itv); mode = "ALARM"; statusDisplay.innerText = "SQUAT TO STOP ALARM"; alarm.play(); }}
            }}, 1000);
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
    
    if st.button("TERMINATE SESSION"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
