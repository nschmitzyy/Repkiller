import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & LUXURY STYLE ---
st.set_page_config(page_title="AURUM Squat Coach", layout="centered")

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
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.3);
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: #d4af37; 
        color: black; font-weight: bold; border: none; padding: 10px;
    }}
    h1, h2, h3 {{ color: #d4af37 !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# Audio-Datei
audio_html_src = ""
if os.path.exists("alarm.mp3"):
    with open("alarm.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if st.session_state.phase == "SETUP":
    st.title("⚜️ AURUM ELITE")
    
    col1, col2 = st.columns(2)
    with col1:
        target_sets = st.number_input("Sätze gesamt", 1, 20, 3)
        target_reps = st.number_input("Reps pro Satz", 1, 100, 10)
    with col2:
        pause_time = st.slider("Pause (Sekunden)", 5, 180, 60)
        tempo = st.number_input("Metronom BPM", 20, 120, 45)
    
    if st.button("TRAINING STARTEN"):
        st.session_state.target_sets = target_sets
        st.session_state.target_reps = target_reps
        st.session_state.pause_time = pause_time
        st.session_state.current_set = 1
        st.session_state.phase = "WORKOUT"
        st.rerun()

elif st.session_state.phase == "WORKOUT":
    js_code = f"""
    <div style="color: #d4af37; font-family: sans-serif;">
        <div id="stats" style="display: flex; justify-content: space-around; margin-bottom: 15px;">
            <div><small>SATZ</small><h2 id="set-count">{st.session_state.current_set} / {st.session_state.target_sets}</h2></div>
            <div><small>REPS</small><h2 id="rep-count">0 / {st.session_state.target_reps}</h2></div>
            <div><small>TIMER</small><h2 id="timer-text">--</h2></div>
        </div>
        
        <div style="position: relative;">
            <video id="vid" style="width: 100%; border-radius: 15px; border: 1px solid #d4af37; transform: scaleX(-1);" autoplay playsinline></video>
            <div style="position: absolute; top: 10px; right: 10px; display: flex; gap: 5px;">
                <button onclick="switchCam()" style="background:rgba(0,0,0,0.5); color:white; border:1px solid #d4af37; border-radius:5px; padding:5px; cursor:pointer;">🔄 Kamera</button>
            </div>
        </div>
        
        <p id="status-text" style="font-size: 20px; font-weight: bold; margin-top: 10px;">BEREIT</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        let reps = 0;
        let stage = "up";
        let mode = "TRAINING";
        let currentFacingMode = "user";

        const video = document.getElementById('vid');
        const repDisplay = document.getElementById('rep-count');
        const timerDisplay = document.getElementById('timer-text');
        const statusDisplay = document.getElementById('status-text');

        async function startCamera() {{
            const constraints = {{
                video: {{
                    facingMode: currentFacingMode,
                    width: {{ ideal: 1280 }},
                    height: {{ ideal: 720 }},
                    // Zoom-Trick: Manche Browser erlauben "zoom", 
                    // aber für echte 0.5x nutzen wir den Weitwinkel-Constraint falls verfügbar
                    advanced: [{{ zoom: 0.5 }}] 
                }}
            }};
            
            try {{
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = stream;
            }} catch (err) {{
                console.error("Camera Error: ", err);
                // Fallback ohne Zoom
                const fallback = await navigator.mediaDevices.getUserMedia({{video: true}});
                video.srcObject = fallback;
            }}
        }}

        function switchCam() {{
            currentFacingMode = (currentFacingMode === "user") ? "environment" : "user";
            video.style.transform = (currentFacingMode === "user") ? "scaleX(-1)" : "scaleX(1)";
            startCamera();
        }}

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
            const angle = calculateAngle(lm[24], lm[26], lm[28]);

            if (mode === "TRAINING") {{
                if (angle > 160) stage = "up";
                if (angle < 90 && stage === "up") {{
                    stage = "down";
                    reps++;
                    repDisplay.innerText = reps + " / " + targetReps;
                    if (reps >= targetReps) startRest();
                }}
                statusDisplay.innerText = angle < 95 ? "TIEF GENUG!" : "TIEFER...";
            }} else if (mode === "ALARM") {{
                if (angle < 140) {{
                    alarm.pause();
                    window.parent.postMessage({{type: 'set_done'}}, '*');
                }}
            }}
        }});

        function startRest() {{
            mode = "REST";
            let timeLeft = pauseTime;
            const itv = setInterval(() => {{
                timeLeft--;
                timerDisplay.innerText = timeLeft + "s";
                if (timeLeft <= 0) {{
                    clearInterval(itv);
                    mode = "ALARM";
                    statusDisplay.innerText = "ALARM! BEWEG DICH!";
                    alarm.play();
                }}
            }}, 1000);
        }}

        startCamera();
        video.onloadedmetadata = () => {{
            setInterval(async () => {{ await pose.send({{image: video}}); }}, 100);
        }};
    </script>
    """
    components.html(js_code, height=650)
    
    # Button um Sätze manuell zu beenden oder Reset
    if st.button("Training abbrechen"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
