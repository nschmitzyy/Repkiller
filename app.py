import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & LUXURY STYLE ---
st.set_page_config(page_title="AURUM Squat Coach", layout="centered")

# Hintergrund-Video für den Luxus-Look (Gold/Dunkel)
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(25%);
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 30px; padding: 40px;
        border: 1px solid #d4af37;
        color: #d4af37; text-align: center;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: #d4af37; 
        color: black; font-weight: bold; border: none; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: #f4cf67; transform: scale(1.02); }}
    h1, h2, h3 {{ font-family: 'Playfair Display', serif; color: #d4af37 !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# Audio-Datei einbinden (Deine mp3)
audio_html_src = ""
if os.path.exists("alarm.mp3"):
    with open("alarm.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if st.session_state.phase == "SETUP":
    st.title("⚜️ AURUM SQUAT")
    st.write("Konfiguriere dein Elite-Training")
    
    target_reps = st.number_input("Ziel Wiederholungen", 1, 100, 10)
    pause_time = st.slider("Pausenzeit (Sekunden)", 5, 120, 30)
    tempo = st.number_input("Tempo (BPM - Metronom)", 20, 100, 40)
    
    if st.button("TRAINING STARTEN"):
        st.session_state.target_reps = target_reps
        st.session_state.pause_time = pause_time
        st.session_state.tempo = tempo
        st.session_state.phase = "WORKOUT"
        st.rerun()

elif st.session_state.phase == "WORKOUT":
    # JavaScript Logik für MediaPipe im Browser
    js_code = f"""
    <div style="color: #d4af37; font-family: sans-serif;">
        <div id="stats" style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div><small>REPS</small><h2 id="rep-count">0 / {st.session_state.target_reps}</h2></div>
            <div><small>PHASE</small><h2 id="status-text">BEREIT</h2></div>
            <div><small>PAUSE</small><h2 id="timer-text">--</h2></div>
        </div>
        
        <video id="vid" style="width: 100%; border-radius: 20px; border: 1px solid #d4af37; transform: scaleX(-1);" autoplay playsinline></video>
        <p id="feedback" style="font-size: 18px; margin-top: 15px; font-weight: bold; height: 30px;"></p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    
    <script>
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        let reps = 0;
        let stage = "up";
        let mode = "TRAINING"; // TRAINING, REST, ALARM
        let pauseTimer = null;

        const video = document.getElementById('vid');
        const repDisplay = document.getElementById('rep-count');
        const statusDisplay = document.getElementById('status-text');
        const timerDisplay = document.getElementById('timer-text');
        const feedback = document.getElementById('feedback');

        function calculateAngle(a, b, c) {{
            let radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
            let angle = Math.abs(radians * 180.0 / Math.PI);
            if (angle > 180.0) angle = 360 - angle;
            return angle;
        }}

        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.setOptions({{ modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 }});

        pose.onResults(results => {{
            if (!results.poseLandmarks) return;
            
            const lm = results.poseLandmarks;
            const hip = lm[24]; const knee = lm[26]; const ankle = lm[28];
            const angle = calculateAngle(hip, knee, ankle);

            if (mode === "TRAINING") {{
                if (angle > 160) stage = "up";
                if (angle < 90 && stage === "up") {{
                    stage = "down";
                    reps++;
                    repDisplay.innerText = reps + " / " + targetReps;
                    if (reps >= targetReps) startRest();
                }}
                feedback.innerText = angle < 100 ? "TIEF GENUG!" : "TIEFER GEHEN...";
                feedback.style.color = angle < 90 ? "#d4af37" : "#666";
            }} 
            else if (mode === "ALARM") {{
                if (angle < 140) {{ // Bewegung erkannt (Puffer)
                    alarm.pause();
                    reps = 0;
                    repDisplay.innerText = "0 / " + targetReps;
                    mode = "TRAINING";
                    statusDisplay.innerText = "TRAINING";
                }}
            }}
        }});

        function startRest() {{
            mode = "REST";
            statusDisplay.innerText = "PAUSE";
            let timeLeft = pauseTime;
            
            pauseTimer = setInterval(() => {{
                timeLeft--;
                timerDisplay.innerText = timeLeft + "s";
                if (timeLeft <= 0) {{
                    clearInterval(pauseTimer);
                    mode = "ALARM";
                    statusDisplay.innerText = "ALARM!";
                    alarm.play();
                }}
            }}, 1000);
        }}

        const camera = new Camera(video, {{
            onFrame: async () => {{ await pose.send({{image: video}}); }},
            width: 640, height: 480
        }});
        camera.start();
    </script>
    """
    components.html(js_code, height=700)
    
    if st.button("ZURÜCK ZUM SETUP"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
