st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* VOLLSTÄNDIGER RESET DER STREAMLIT ABSTÄNDE */
    .block-container {{
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }}

    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -2; object-fit: cover; 
        background: url('{BG_IMAGE_URL}') center/cover no-repeat;
        filter: brightness(25%) grayscale(100%);
    }}
    
    /* ... restlicher Style von vorhin ... */
    
    /* ZUSÄTZLICH: Toolbar ausblenden */
    [data-testid="stToolbar"], [data-testid="stHeader"] {{
        display: none !important;
    }}
    </style>
    
    <div id="bgVideo"></div>
    <div class="luxury-header">
        <h1>AURUM PRESTIGE</h1>
    </div>
    """, unsafe_allow_html=True)
