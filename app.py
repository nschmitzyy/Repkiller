import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- CONFIG & LUXURY DESIGN ---
st.set_page_config(page_title="AURUM PRESTIGE", layout="centered")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1550345332-09e3ac987658?q=80&w=2000"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        max-width: 100% !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

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
        -webkit-backdrop-filter: blur(15px); display: flex;
        align-items: center; justify-content: center; z-index: 9999;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .luxury-header h1 {{
        margin: 0 !important; font-family: 'Playfair Display', serif !important;
        font-size: 1.6rem !important; letter-spacing: 6px !important;
        color: #ffffff !important; text-transform: uppercase;
    }}

    .main-card {{
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px); border-radius: 40px; 
        padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.9);
        font-family: 'Inter', sans-serif; margin-top: 110px; 
        margin-bottom: 50px; animation: fadeIn 1.5s ease;
    }}

    /* --- BUTTON STYLING (KLEINER & HOVER) --- */
    .stButton {{
        display: flex;
        justify-content: center;
    }}

    .stButton>button {{
        width: auto !important; /* Macht den Button kleiner */
        min-width: 250px;
        padding: 12px 40px !important;
        border-radius: 0px;
        background: #ffffff; 
        color: #000000; 
        font-weight: 700; 
        border: 1px solid #ffffff; 
        letter-spacing: 3px;
        transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        text-transform: uppercase;
        cursor: pointer;
    }}

    .stButton>button:hover {{
        background: transparent !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(255, 255, 255, 0.1);
    }}

    .stButton>button:active {{
        transform: translateY(-1px);
    }}

    div[data-testid="stWidgetLabel"] p {{ color: #ffffff !important; opacity: 0.8; }}
    input {{ background: rgba(255,255,255,0.05) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    
    <div id="bgVideo"></div>
    <div class="luxury-header">
        <h1>AURUM PRESTIGE</h1>
    </div>
    """, unsafe_allow_html=True)

# --- RESTLICHER CODE (SESSION STATE & PHASEN) BLEIBT GLEICH ---
# ... (Hier folgt der gleiche Code wie zuvor für Audio-Setup, Setup-Phase und Workout-Phase)
