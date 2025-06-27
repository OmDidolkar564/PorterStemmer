import streamlit as st
import re
import pandas as pd
import requests

st.set_page_config(
    page_title="Porter Stemmer Interactive Demo",
    page_icon="📚",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.form("theme_switcher"):
    toggle_label = "🌙 Dark Mode" if st.session_state.theme == "Light" else "🌞 Light Mode"
    submitted = st.form_submit_button(toggle_label)
    if submitted:
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"

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
    div[role='form'] {
        position: absolute;
        top: 10px;
        right: 20px;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.theme == "Dark":
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
    &#128640; NLP Project: Porter Stemmer Visualization
</div>
""", unsafe_allow_html=True)

def measure(word):
    pattern = re.compile(r'([aeiouy]+[^aeiouy]+)')
    return len(pattern.findall(word))

def contains_vowel(word):
    return bool(re.search(r'[aeiouy]', word))

def ends_double_consonant(word):
    return len(word) >= 2 and word[-1] == word[-2] and word[-1] not in 'aeiou'

def cvc(word):
    if len(word) < 3:
        return False
    c1, v, c2 = word[-3], word[-2], word[-1]
    return (c1 not in 'aeiou' and v in 'aeiou' and c2 not in 'aeiouwy')

def step_1a(word, steps):
    original = word
    if word.endswith("sses"):
        word = word[:-2]
        steps.append((original, word, "1a: SSES → SS"))
    elif word.endswith("ies"):
        word = word[:-3] + "i"
        steps.append((original, word, "1a: IES → I"))
    elif word.endswith("ss"):
        pass
    elif word.endswith("s"):
        word = word[:-1]
        steps.append((original, word, "1a: S → ''"))
    return word

def step_1b(word, steps):
    original = word
    if word.endswith("eed"):
        stem = word[:-3]
        if measure(stem) > 0:
            word = stem + "ee"
            steps.append((original, word, "1b: (m>0) EED → EE"))
    elif word.endswith("ed"):
        stem = word[:-2]
        if contains_vowel(stem):
            word = stem
            steps.append((original, word, "1b: (v) ED → ''"))
            word = step_1b_post_processing(word, steps)
    elif word.endswith("ing"):
        stem = word[:-3]
        if contains_vowel(stem):
            word = stem
            steps.append((original, word, "1b: (v) ING → ''"))
            word = step_1b_post_processing(word, steps)
    return word

def step_1b_post_processing(word, steps):
    original = word
    if word.endswith("at"):
        word += "e"
        steps.append((original, word, "1b Post: AT → ATE"))
    elif word.endswith("bl"):
        word += "e"
        steps.append((original, word, "1b Post: BL → BLE"))
    elif word.endswith("iz"):
        word += "e"
        steps.append((original, word, "1b Post: IZ → IZE"))
    elif ends_double_consonant(word) and word[-1] not in "lsz":
        word = word[:-1]
        steps.append((original, word, "1b Post: double consonant → single letter"))
    elif measure(word) == 1 and cvc(word):
        word += "e"
        steps.append((original, word, "1b Post: CVC and m=1 → add E"))
    return word

def step_1c(word, steps):
    original = word
    if word.endswith("y") and contains_vowel(word[:-1]):
        word = word[:-1] + "i"
        steps.append((original, word, "1c: (v) Y → I"))
    return word

step2_rules = {
    "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance", "izer": "ize",
    "abli": "able", "alli": "al", "entli": "ent", "eli": "e", "ousli": "ous",
    "ization": "ize", "ation": "ate", "ator": "ate", "alism": "al", "iveness": "ive",
    "fulness": "ful", "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble"
}

def step_2(word, steps):
    for suffix, repl in sorted(step2_rules.items(), key=lambda x: -len(x[0])):
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if measure(stem) > 0:
                original = word
                word = stem + repl
                steps.append((original, word, f"2: (m>0) {suffix.upper()} → {repl.upper()}"))
            break
    return word

step3_rules = {
    "icate": "ic", "ative": "", "alize": "al", "iciti": "ic",
    "ical": "ic", "ful": "", "ness": ""
}

def step_3(word, steps):
    for suffix, repl in sorted(step3_rules.items(), key=lambda x: -len(x[0])):
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if measure(stem) > 0:
                original = word
                word = stem + repl
                repl_label = repl.upper() if repl else "(null)"
                steps.append((original, word, f"3: (m>0) {suffix.upper()} → {repl_label}"))
            break
    return word

step4_suffixes = [
    "al", "ance", "ence", "er", "ic", "able", "ible", "ant",
    "ement", "ment", "ent", "ion", "ou", "ism", "ate", "iti",
    "ous", "ive", "ize"
]

def step_4(word, steps):
    for suffix in step4_suffixes:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if measure(stem) > 1:
                if suffix == "ion" and (stem.endswith("s") or stem.endswith("t")):
                    original = word
                    word = stem
                    steps.append((original, word, "4: (m>1 & *S/*T) ION → ''"))
                    break
                elif suffix != "ion":
                    original = word
                    word = stem
                    steps.append((original, word, f"4: (m>1) {suffix.upper()} → ''"))
                    break
    return word

def step_5(word, steps):
    original = word
    if word.endswith("e"):
        stem = word[:-1]
        m = measure(stem)
        if m > 1:
            word = stem
            steps.append((original, word, "5: (m>1) E → ''"))
        elif m == 1 and not cvc(stem):
            word = stem
            steps.append((original, word, "5: (m=1 and CVC) E → ''"))
    elif word.endswith("ll") and measure(word) > 1:
        word = word[:-1]
        steps.append((original, word, "5: (m>1 and *L) LL → L"))
    return word

def porter_stem_with_steps(word):
    steps = []
    word = word.lower()
    word = step_1a(word, steps)
    word = step_1b(word, steps)
    word = step_1c(word, steps)
    word = step_2(word, steps)
    word = step_3(word, steps)
    word = step_4(word, steps)
    word = step_5(word, steps)
    return steps, word

def tab_step_by_step():
    st.markdown("## Porter Stemmer Step-by-Step Guide")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Try it yourself")
        input_word = st.text_input("Enter a word to stem", value="running")
        if st.button("Stem Word", type="primary"):
            steps, final_stem = porter_stem_with_steps(input_word)
            st.session_state.steps = steps
            st.session_state.final_stem = final_stem
            st.session_state.input_word = input_word
    with col2:
        if 'steps' in st.session_state:
            st.subheader(f"Stemming process for '{st.session_state.input_word}'")
            if st.session_state.steps:
                for i, (before, after, rule) in enumerate(st.session_state.steps):
                    with st.container():
                        st.markdown(f"""
                        <div class='step-box'>
                            <b>Step {i+1}:</b> Rule {rule}<br>
                            <span style='color: #E1EEBC;'>Before:</span> <span class='highlight'>{before}</span> → 
                            <span style='color: #E1EEBC;'>After:</span> <span class='highlight'>{after}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info(f"No rules applied. Word '{st.session_state.input_word}' remains unchanged.")
            st.markdown(
                f"""
                <div style="background-color:#FF4C4B; padding:10px; border-radius:8px">
                    <p style="color:white; font-weight:bold; font-size:16px; margin:0">
                        Final stem: <span style="text-transform: lowercase;">{st.session_state.final_stem}</span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

def main():
    tab1, tab2 = st.tabs([
        "🛠️ Step-by-Step Guide",
        "📊 Example Table"
    ])
    with tab1:
        tab_step_by_step()
    with tab2:
        st.markdown("## Example Words")
        example_df = pd.DataFrame({
            "Original Word": ["running", "connection", "argued", "happily", "analysis"],
            "Porter Stem": ["run", "connect", "argu", "happili", "analysi"]
        })
        st.table(example_df)

if __name__ == "__main__":
    main()
