# === Custom CSS ===
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .custom-header {
        background-color: #143D60;
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    div.stButton > button:first-child {
        background-color: #90C67C;
        color: white;
        font-size: 16px;
        padding: 8px 16px;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #5a8e4a;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# === Theme Toggle ===
mode = st.selectbox("🌓 Choose Theme", ["🌞 Light", "🌙 Dark"], index=0)

if "Dark" in mode:
    st.markdown("""
        <style>
            body, .main { background-color: #1e1e1e; color: #f0f0f0; }
            .step-box { background-color: #2a2a2a; border-left: 4px solid #90C67C; }
            .highlight { background-color: #444; }
            .info-box { background-color: #1f3b57; border-left: 6px solid #2196F3; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body, .main { background-color: #ffffff; color: #000000; }
            .step-box { background-color: #f0f0f0; border-left: 4px solid #90C67C; }
            .highlight { background-color: #90C67C; }
            .info-box { background-color: #e3f2fd; border-left: 6px solid #2196F3; }
        </style>
    """, unsafe_allow_html=True)

# === Custom Header ===
st.markdown("""
<div class="custom-header">
    &#128640; NLP Project: Porter Stemmer Visualization
</div>
""", unsafe_allow_html=True)