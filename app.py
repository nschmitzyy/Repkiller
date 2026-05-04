import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import pygame
from datetime import datetime

# --- INITIALISIERUNG ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pygame.mixer.init()

# Luxus-Design via CSS
st.set_page_config(page_title="AURUM Fitness AI", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e0e0e0; }
    .stSlider > div > div > div > div { background-color: #d4af37; }
    h1 { color: #d4af37; font-family: 'Playfair Display', serif; text-align: center; }
    .stat-box { padding: 20px; border-radius: 10px; border: 1px solid #d4af37; text-align: center; background: #1a1c23; }
    </style>
    """, unsafe_allow_html=True)

def calculate_angle(a, b, c):
    a = np.array(a) # Hüfte
    b = np.array(b) # Knie
    c = np.array(c) # Knöchel
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360-angle
    return angle

def play_alarm():
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.load("alarm.mp3")
            pygame.mixer.music.play(-1) # Loop
        except:
            pass

def stop_alarm():
    pygame.mixer.music.stop()

# --- SIDEBAR EINSTELLUNGEN ---
st.sidebar.header("⚜️ COACH EINSTELLUNGEN")
target_reps = st.sidebar.number_input("Ziel Wiederholungen", min_value=1, value=10)
rest_time = st.sidebar.slider("Pausenzeit (Sekunden)", 5, 120, 30)
tempo_bpm = st.sidebar.number_input("Metronom (BPM)", 20, 100, 40)

# --- APP LOGIK ---
st.title("AURUM PERSONAL COACH")

col1, col2 = st.columns([3, 1])

with col2:
    rep_counter = st.empty()
    stage_display = st.empty()
    timer_display = st.empty()
    feedback_display = st.empty()

ctx = cv2.VideoCapture(0)
counter = 0
stage = None # "up" oder "down"
workout_state = "TRAINING" # TRAINING, REST, ALARM
start_rest_time = 0

with col1:
    view = st.image([])

with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
    while ctx.isOpened():
        ret, frame = ctx.read()
        if not ret: break

        # Bild verarbeiten
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Koordinaten holen (Hüfte, Knie, Knöchel)
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            angle = calculate_angle(hip, knee, ankle)

            # LOGIK: Kniebeuge zählen
            if workout_state == "TRAINING":
                if angle > 160:
                    stage = "UP"
                if angle < 90 and stage == 'UP':
                    stage = "DOWN"
                    counter += 1
                    
                if counter >= target_reps:
                    workout_state = "REST"
                    start_rest_time = time.time()

            # LOGIK: Pausen & Alarm
            elif workout_state == "REST":
                elapsed = time.time() - start_rest_time
                remaining = rest_time - int(elapsed)
                timer_display.markdown(f"<div class='stat-box'>⏳ PAUSE: {remaining}s</div>", unsafe_allow_html=True)
                
                if remaining <= 0:
                    workout_state = "ALARM"
            
            elif workout_state == "ALARM":
                timer_display.markdown("<div class='stat-box' style='color:red;'>🚨 ZEIT ABGELAUFEN! BEWEG DICH!</div>", unsafe_allow_html=True)
                play_alarm()
                # Wenn Winkel sich 90 Grad nähert (Bewegung startet), stoppe Alarm
                if angle < 140: 
                    stop_alarm()
                    counter = 0 # Reset für nächsten Satz
                    workout_state = "TRAINING"

        except Exception as e:
            pass

        # Visualisierung
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        view.image(image, channels="RGB")
        
        rep_counter.markdown(f"<div class='stat-box'><h1>{counter} / {target_reps}</h1>REPS</div>", unsafe_allow_html=True)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

ctx.release()
