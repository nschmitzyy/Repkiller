import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & LUXURY DESIGN ---
st.set_page_config(page_title="AURUM PRESTIGE", layout="centered")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1550345332-09e3ac987658?q=80&w=2000"

# --- AUDIO CONVERSION ---
def get_audio_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            return f"data:audio/mp3;base64,{base64.b64encode(data).decode()}"
    return ""

# Wir laden den Sound in eine Variable
boom_sound_src = get_audio_base64("vine-boom-sound.mp3")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    .block-container {{ padding-top: 0rem !important; margin-top: 0rem !important; max-width: 100% !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}

    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -2; object-fit: cover; 
        background: url('{BG_IMAGE_URL}') center/cover no-repeat;
        filter: brightness(25%) grayscale(100%);
    }}
    
    .stApp {{ background: transparent !important; }}

    .luxury-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 80px;
        background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(15px);
        display: flex; align-items: center; justify-content: center; z-index: 9999;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .luxury-header h1 {{
        margin: 0 !important; font-family: 'Playfair Display', serif !important;
        font-size: 1.6rem !important; letter-spacing: 6px !important;
        color: #ffffff !important; text-transform: uppercase;
    }}

    .main-card {{
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(30px);
        border-radius: 40px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 110px; 
        font-family: 'Inter', sans-serif; animation: fadeIn 1.5s ease;
    }}

    .stButton {{ display: flex; justify-content: center; }}
    .stButton>button {{
        width: auto !important; min-width: 250px; padding: 12px 40px !important;
        background: #ffffff; color: #000000; font-weight: 700; border: 1px solid #ffffff; 
        letter-spacing: 3px; transition: all 0.5s ease; text-transform: uppercase;
    }}
    .stButton>button:hover {{
        background: transparent !important; color: #ffffff !important;
        transform: translateY(-3px);
    }}

    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    <div id="bgVideo"></div>
    <div class="luxury-header"><h1>AURUM PRESTIGE</h1></div>
    """, unsafe_allow_html=True)

# Session State
if 'phase' not in st.session_state: st.session_state.phase = "SETUP"
if 'current_set' not in st.session_state: st.session_state.current_set = 1

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if st.session_state.phase == "SETUP":
    st.write("PRESTIGE WORKOUT CONFIGURATION")
    col1, col2 = st.columns(2)
    with col1:
        target_sets = st.number_input("SETS", 1, 20, 3)
        target_reps = st.number_input("REPS", 1, 100, 10)
    with col2:
        pause_time = st.slider("REST (SEC)", 5, 180, 60)
        tempo_bpm = st.number_input("TEMPO BPM", 20, 120, 45)
    
    if st.button("INITIALIZE SESSION"):
        st.session_state.update({"target_sets": target_sets, "target_reps": target_reps, "pause_time": pause_time, "tempo_bpm": tempo_bpm, "phase": "WORKOUT"})
        st.rerun()

elif st.session_state.phase == "WORKOUT":
    js_code = f"""
    <div style="color: white; font-family: 'Inter', sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
            <div><small>SET</small><h2 style="font-family:'Playfair Display';">{st.session_state.current_set}/{st.session_state.target_sets}</h2></div>
            <div><small>REPS</small><h2 id="rep-count" style="font-family:'Playfair Display';">0/{st.session_state.target_reps}</h2></div>
            <div><small>TIMER</small><h2 id="timer-text" style="font-family:'Playfair Display';">--</h2></div>
        </div>
        <video id="vid" style="width: 100%; filter: grayscale(100%); background: #000;" autoplay playsinline></video>
        <p id="status-text" style="letter-spacing: 3px; margin-top: 20px; text-transform: uppercase;">READY</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const boomSound = new Audio("{boom_sound_src}");
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const tempoBpm = {st.session_state.tempo_bpm};
        
        let reps = 0; let stage = "up"; let mode = "TRAINING";
        const video = document.getElementById('vid');
        const repDisplay = document.getElementById('rep-count');
        const timerDisplay = document.getElementById('timer-text');
        const statusDisplay = document.getElementById('status-text');

        async function initCamera() {{
            const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
            video.srcObject = stream;
        }}

        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.onResults(results => {{
            if (!results.poseLandmarks) return;
            const angle = calculateAngle(results.poseLandmarks[24], results.poseLandmarks[26], results.poseLandmarks[28]);

            if (mode === "TRAINING") {{
                if (angle > 160) stage = "up";
                if (angle < 90 && stage === "up") {{
                    stage = "down"; reps++;
                    repDisplay.innerText = reps + "/" + targetReps;
                    if (reps >= targetReps) startRest();
                }}
            }} else if (mode === "ALARM" && angle < 140) {{
                boomSound.pause(); window.location.reload(); 
            }}
        }});

        function calculateAngle(a, b, c) {{
            let radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
            let angle = Math.abs(radians * 180.0 / Math.PI);
            return angle > 180 ? 360 - angle : angle;
        }}

        function startRest() {{
            mode = "REST";
            boomSound.play(); // Erster Boom beim Start der Pause
            statusDisplay.innerText = "REST";
            let timeLeft = pauseTime;
            const itv = setInterval(() => {{
                timeLeft--; timerDisplay.innerText = timeLeft + "s";
                if (timeLeft <= 0) {{ 
                    clearInterval(itv); mode = "ALARM"; 
                    statusDisplay.innerText = "SQUAT NOW!"; 
                    boomSound.play(); // Boom als Alarm
                }}
            }}, 1000);
        }}

        initCamera();
        pose.setOptions({{ modelComplexity: 1 }});
        async function detectionLoop() {{
            await pose.send({{image: video}});
            requestAnimationFrame(detectionLoop);
        }}
        video.onloadeddata = detectionLoop;
    </script>
    """
    components.html(js_code, height=650)

st.markdown('</div>', unsafe_allow_html=True)
