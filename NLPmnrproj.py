import streamlit as st
import re
import pandas as pd
import requests

# =====================
# Page Configuration
# =====================
st.set_page_config(
    page_title="Porter Stemmer Interactive Demo",
    page_icon="📚",
    layout="wide"
)

# =====================
# Unified Custom CSS & Theme Toggle
# =====================
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
}
.main { padding: 2rem 3rem; }
.step-box {
    background-color: #346751;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 10px;
    border-left: 4px solid #90C67C;
}
.title-container { text-align: center; margin-bottom: 2rem; }
.tab-content {
    padding: 25px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    margin-top: 10px;
}
.highlight {
    background-color: #90C67C;
    padding: 0 3px;
    border-radius: 3px;
}
.info-box {
    background-color: #143D60;
    border-left: 6px solid #2196F3;
    padding: 10px;
    margin: 15px 0;
    color: white;
}
.pros { color: #4CAF50; }
.cons { color: #F44336; }
</style>
""", unsafe_allow_html=True)

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

st.markdown("""
<div class="custom-header">
    🚀 NLP Project: Porter Stemmer Visualization
</div>
""", unsafe_allow_html=True)

# =====================
# Main Content Tabs
# =====================
from NLPmnrproj_functions import (
    tab_what_is_porter,
    tab_pros_and_cons,
    tab_alternatives,
    tab_step_by_step
)

def main():
    st.markdown("""
    <div class="title-container">
        <h1>📚 Porter Stemmer Interactive Demo</h1>
        <p>Explore word stemming in natural language processing</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 What is Porter Stemmer", 
        "⚖️ Pros & Cons", 
        "🔄 Alternatives", 
        "🛠️ Step-by-Step Guide"
    ])

    with tab1:
        tab_what_is_porter()
    with tab2:
        tab_pros_and_cons()
    with tab3:
        tab_alternatives()
    with tab4:
        tab_step_by_step()

    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
        <p>Porter Stemmer Interactive Demo | Natural Language Processing Tool</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
