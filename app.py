js_code = f"""
    <div style="color: #d4af37; font-family: sans-serif;">
        <div id="stats" style="display: flex; justify-content: space-around; margin-bottom: 15px;">
            <div><small>SATZ</small><h2 id="set-count">{st.session_state.current_set} / {st.session_state.target_sets}</h2></div>
            <div><small>REPS</small><h2 id="rep-count">0 / {st.session_state.target_reps}</h2></div>
            <div><small>TIMER</small><h2 id="timer-text">--</h2></div>
        </div>
        
        <div style="position: relative; width: 100%; max-width: 640px; margin: 0 auto;">
            <video id="vid" style="width: 100%; border-radius: 15px; border: 2px solid #d4af37; background: #000;" autoplay playsinline></video>
            
            <!-- Kamera-Steuerung Buttons -->
            <div style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 10;">
                <button onclick="toggleCamera()" style="background: rgba(212, 175, 55, 0.8); color: black; border: none; border-radius: 25px; padding: 10px 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                    🔄 KAMERA WECHSELN
                </button>
            </div>
        </div>
        
        <p id="status-text" style="font-size: 20px; font-weight: bold; margin-top: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">BEREIT</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const targetReps = {st.session_state.target_reps};
        const pauseTime = {st.session_state.pause_time};
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        let currentStream = null;
        let useFrontCamera = true; // Startet standardmäßig mit Front
        let mode = "TRAINING";
        let reps = 0;
        let stage = "up";

        const video = document.getElementById('vid');
        const repDisplay = document.getElementById('rep-count');
        const timerDisplay = document.getElementById('timer-text');
        const statusDisplay = document.getElementById('status-text');

        // Funktion zum Starten der Kamera mit spezifischen Constraints
        async function initCamera() {{
            if (currentStream) {{
                currentStream.getTracks().forEach(track => track.stop());
            }}

            const constraints = {{
                video: {{
                    facingMode: useFrontCamera ? "user" : "environment",
                    width: {{ ideal: 1280 }},
                    height: {{ ideal: 720 }}
                }}
            }};

            try {{
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
                
                // Spiegelung nur bei der Frontkamera
                video.style.transform = useFrontCamera ? "scaleX(-1)" : "scaleX(1)";
                
            }} catch (err) {{
                console.error("Kamera-Fehler:", err);
                alert("Kamera konnte nicht geladen werden.");
            }}
        }}

        function toggleCamera() {{
            useFrontCamera = !useFrontCamera;
            initCamera();
        }}

        // Pose Erkennung Setup
        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.setOptions({{ modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 }});

        pose.onResults(results => {{
            if (!results.poseLandmarks) return;
            
            // Logik für Kniebeugen-Winkel (LM 24: Hüfte, 26: Knie, 28: Knöchel)
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
                statusDisplay.innerText = angle < 95 ? "TIEF GENUG!" : "GEH TIEFER...";
                statusDisplay.style.color = angle < 95 ? "#4CAF50" : "#d4af37";
            }} else if (mode === "ALARM") {{
                if (angle < 140) {{
                    alarm.pause();
                    // Reset für nächsten Satz
                    reps = 0;
                    repDisplay.innerText = "0 / " + targetReps;
                    mode = "TRAINING";
                    statusDisplay.innerText = "NÄCHSTER SATZ STARTET!";
                }}
            }}
        }});

        function calculateAngle(a, b, c) {{
            let radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
            let angle = Math.abs(radians * 180.0 / Math.PI);
            if (angle > 180.0) angle = 360 - angle;
            return angle;
        }}

        function startRest() {{
            mode = "REST";
            statusDisplay.innerText = "PAUSE!";
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

        // Start
        initCamera();
        
        // Loop für MediaPipe
        async function detectionLoop() {{
            if (video.paused || video.ended) return;
            await pose.send({{image: video}});
            requestAnimationFrame(detectionLoop);
        }}
        video.onloadeddata = () => {{ detectionLoop(); }};

    </script>
    """
