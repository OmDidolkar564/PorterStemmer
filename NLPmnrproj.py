
import streamlit as st
import re
import pandas as pd
import requests

# Set page configuration
st.set_page_config(
    page_title="Porter Stemmer Interactive Demo",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to improve the UI
st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
    }
    .step-box {
        background-color: #346751;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #90C67C;
    }
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }
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
    }
    .pros {
        color: #4CAF50;
    }
    .cons {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)


# Porter Stemmer functions with step tracking
def measure(word):
    pattern = re.compile(r'([aeiouy]+[^aeiouy]+)')
    return len(pattern.findall(word))


# Include 'y' as a vowel to correctly handle words like 'flying'
def contains_vowel(word):
    return bool(re.search(r'[aeiouy]', word))


def ends_double_consonant(word):
    return len(word) >= 2 and word[-1] == word[-2] and word[-1] not in 'aeiou'


def cvc(word):
    if len(word) < 3:
        return False
    c1, v, c2 = word[-3], word[-2], word[-1]
    # final consonant cannot be w, x, or y
    return (c1 not in 'aeiou' and v in 'aeiou' and c2 not in 'aeiouwy')


# Step 1a
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


# Step 1b and post-processing
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


# Step 1c
def step_1c(word, steps):
    original = word
    if word.endswith("y") and contains_vowel(word[:-1]):
        word = word[:-1] + "i"
        steps.append((original, word, "1c: (v) Y → I"))
    return word


# Step 2 rules
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


# Step 3 rules
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


# Step 4 rules
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


# Step 5 rules
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


# Full Porter Stemmer with steps
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


# Try to load Lottie animation safely
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


# Tab 1: What is Porter Stemmer
def tab_what_is_porter():
    col1, col2 = st.columns([2, 1])    
    with col1:
        st.markdown("## What is the Porter Stemmer?")
        st.markdown("""
        The Porter Stemmer is a widely-used rule-based algorithm for stemming English words, developed by 
        Martin Porter in 1980. Stemming is the process of reducing words to their word stem or root form.
        
        For example, the words:
        - "connection", "connections", "connective", "connected", "connecting"
        
        All share the same stem: "connect"
        
        ### How it Works
        
        The Porter Stemmer operates through a series of sequential steps (5 phases), where each step applies 
        different rules for removing or replacing suffixes based on specific patterns and constraints.
        
        1. **Step 1**: Handles plural forms and past participles (split into 1a, 1b, and 1c)
        2. **Step 2**: Converts various suffixes to standardized forms
        3. **Step 3**: Deals with derivational suffixes
        4. **Step 4**: Handles more derivational suffixes
        5. **Step 5**: Final tidy-up (removing 'e' and double consonants)
        
        ### Key Concept: Measure (m)
        
        The algorithm uses the concept of "measure" (m) to determine when to apply certain rules. The measure 
        represents the number of vowel-consonant sequences in a word.
        
        For example:
        - "tree" has measure m=0 (no complete VC sequence)
        - "trouble" has measure m=1 (one VC sequence)
        - "beautiful" has measure m=2 (two VC sequences)
        """)
        
        st.markdown("""
        <div class="info-box">
        <b>Historical Note:</b> The Porter Stemmer was one of the first stemming algorithms for English and 
        continues to be popular due to its simplicity and efficiency, despite being developed over 40 years ago.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Try to load lottie animation if streamlit_lottie is installed
        
            
        st.markdown("### Example Stemming Results")
        example_df = pd.DataFrame({
            "Original Word": ["running", "connection", "argued", "happily", "analysis"],
            "Porter Stem": ["run", "connect", "argu", "happili", "analysi"]
        })
        st.table(example_df)

# Tab 2: Pros and Cons of Stemming
def tab_pros_and_cons():
    st.markdown("## Pros and Cons of Using Porter Stemmer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### <span class='pros'>Advantages</span>", unsafe_allow_html=True)
        st.markdown("""
        - **Simplicity**: The algorithm is straightforward to implement and understand
        - **Efficiency**: Fast processing with low computational requirements
        - **Language Independence**: Works well for English without requiring dictionaries
        - **Consistency**: Produces consistent stems for related word forms
        - **Reduced Index Size**: In information retrieval, reduces storage needs by 20-50%
        - **Well-Established**: Extensively tested and used in many applications
        - **Improved Search Recall**: Groups similar words together, increasing recall rates
        """)
        
        st.markdown("### <span class='pros'>Best Use Cases</span>", unsafe_allow_html=True)
        st.markdown("""
        - Information retrieval systems
        - Search engines (especially for English text)
        - Text classification
        - Document clustering
        - Systems where processing speed is more important than linguistic accuracy
        """)
    
    with col2:
        st.markdown("### <span class='cons'>Disadvantages</span>", unsafe_allow_html=True)
        st.markdown("""
        - **Over-stemming**: Can strip too much from a word, causing different words to produce the same stem
        - **Under-stemming**: Sometimes fails to reduce related words to the same stem
        - **Language Specific**: Optimized for English, performs poorly with other languages
        - **Linguistic Inaccuracy**: Doesn't always produce linguistically valid stems
        - **Irregular Words**: Doesn't handle irregular word forms well (e.g., "be", "am", "was")
        - **Linguistic Context**: Ignores word context and sentence structure
        - **Not Adaptive**: Rule-based approach can't learn from new data or adapt to specific domains
        """)
        
        st.markdown("### <span class='cons'>Limitations</span>", unsafe_allow_html=True)
        st.markdown("""
        - **No Semantic Understanding**: Doesn't understand word meanings
        - **Proper Nouns**: May incorrectly stem proper nouns
        - **Technical Terminology**: May not handle domain-specific terms well
        - **Multilingual Text**: Poor performance on mixed-language documents
        """)
    
    st.markdown("""
    <div class="info-box">
    <b>When to Use Porter Stemmer:</b> Porter Stemmer is ideal for quick text processing tasks in English where computational efficiency is a priority and perfect linguistic accuracy isn't required. It shines in search applications, document indexing, and text classification tasks.
    </div>
    """, unsafe_allow_html=True)

# Tab 3: Alternatives
def tab_alternatives():
    st.markdown("## Alternatives to Porter Stemmer")
    
    st.markdown("""
    While Porter Stemmer remains popular, several alternatives exist that offer different approaches to word normalization:
    """)
    
    alternatives = [
        {
            "name": "Snowball Stemmer (Porter2)",
            "description": "An improved version of the Porter Stemmer by the same author, with better handling of irregular forms and adaptations for multiple languages.",
            "pros": "More accurate than the original Porter, supports 20+ languages, handles edge cases better",
            "cons": "Slightly more complex implementation, marginally slower processing speed",
            "languages": "Multi-language support (English, French, Spanish, German, etc.)"
        },
        {
            "name": "Lancaster Stemmer",
            "description": "A more aggressive stemming algorithm that iteratively applies rules until no more can be applied.",
            "pros": "Very aggressive stemming leading to shorter stems, faster processing of large texts",
            "cons": "Often over-stems words, resulting in unrecognizable stems, less intuitive results",
            "languages": "Primarily English"
        },
        {
            "name": "Lemmatization",
            "description": "Unlike stemming, lemmatization reduces words to their linguistically valid base form (lemma) using vocabulary and morphological analysis.",
            "pros": "Produces actual dictionary words, higher accuracy, considers word context",
            "cons": "Computationally expensive, requires dictionary and POS tagging, slower processing",
            "languages": "Available for many languages depending on the implementation"
        },
        {
            "name": "Krovetz Stemmer",
            "description": "A lightweight stemmer that focuses on removing inflectional suffixes and handling special cases.",
            "pros": "More linguistically accurate than Porter, produces recognizable words",
            "cons": "Less aggressive than Porter, which may reduce recall in search applications",
            "languages": "English only"
        },
        {
            "name": "WordNet Lemmatizer",
            "description": "Uses the WordNet database to look up lemmas of words, providing context-aware normalization.",
            "pros": "Highly accurate, produces dictionary words, considers word meaning",
            "cons": "Requires WordNet database, slowest option, needs part-of-speech information",
            "languages": "English focused, with some limited support for other languages"
        }
    ]
    
    for i, alt in enumerate(alternatives):
        with st.expander(f"{alt['name']}"):
            st.markdown(f"**Description**: {alt['description']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Advantages:**")
                st.markdown(alt['pros'])
            with col2:
                st.markdown("**Disadvantages:**")
                st.markdown(alt['cons'])
            st.markdown(f"**Language Support**: {alt['languages']}")
    
    st.markdown("### Comparison Table")
    
    comparison_df = pd.DataFrame({
        "Algorithm": ["Porter Stemmer", "Snowball (Porter2)", "Lancaster", "Lemmatization", "Krovetz"],
        "Speed": ["Very Fast", "Fast", "Fast", "Slow", "Medium"],
        "Accuracy": ["Medium", "Medium-High", "Low", "High", "Medium-High"],
        "Aggressiveness": ["Medium", "Medium", "High", "Low", "Low"],
        "Multi-language": ["No", "Yes", "No", "Yes", "No"]
    })
    
    st.table(comparison_df)
    
    st.markdown("""
    <div class="info-box">
    <b>Choosing the Right Approach:</b> Consider your specific needs when selecting between stemming and lemmatization. Stemming is faster and simpler but less accurate, while lemmatization provides linguistically correct results but requires more resources. For search engines and large document collections, stemming often offers a better speed/accuracy trade-off.
    </div>
    """, unsafe_allow_html=True)

# Tab 4: Step-by-Step Guide
def tab_step_by_step():
    st.markdown("## Porter Stemmer Step-by-Step Guide")
    
    # Create two columns for input and results
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
            
            # st.success(f"Final stem: **{st.session_state.final_stem}**")
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

    
    # Porter Stemmer Algorithm Explanation
    st.markdown("### Porter Stemmer Algorithm Steps")
    
    with st.expander("View Full Algorithm Steps"):
        st.markdown("""
        #### Step 1: Deal with plurals and past participles
        
        **Step 1a:**
        - SSES → SS (caresses → caress)
        - IES → I (ponies → poni)
        - SS → SS (caress → caress)
        - S → "" (cats → cat)
        
        **Step 1b:**
        - (m>0) EED → EE (agreed → agree)
        - (*v*) ED → "" (plastered → plaster)
        - (*v*) ING → "" (motoring → motor)
        
        After 1b, if the second or third rule fired, apply these:
        - AT → ATE (conflat(ed) → conflate)
        - BL → BLE (troubl(ed) → trouble)
        - IZ → IZE (formal(iz)ing → formalize)
        - Double consonant to single (hopp(ing) → hop)
        - (m=1 and *o) → E (fil(ing) → file)
        
        **Step 1c:**
        - (*v*) Y → I (happy → happi)
        
        #### Step 2: Turn various suffixes into common forms
        
        - (m>0) ATIONAL → ATE (relational → relate)
        - (m>0) TIONAL → TION (conditional → condition)
        - (m>0) ENCI → ENCE (valenci → valence)
        - (m>0) ANCI → ANCE (hesitanci → hesitance)
        - (m>0) IZER → IZE (digitizer → digitize)
        - And many more...
        
        #### Step 3: Remove longer suffixes
        
        - (m>0) ICATE → IC (triplicate → triplic)
        - (m>0) ATIVE → "" (formative → form)
        - (m>0) ALIZE → AL (formalize → formal)
        - And more...
        
        #### Step 4: Remove suffixes in specific contexts
        
        - (m>1) AL → "" (revival → reviv)
        - (m>1) ANCE → "" (allowance → allow)
        - (m>1) ENCE → "" (inference → infer)
        - And many more...
        
        #### Step 5: Final cleanup
        
        - (m>1) E → "" (probate → probat)
        - (m=1 and not *o) E → "" (cease → ceas)
        - (m>1 and *d and *L) → single letter (controll → control)
        
        Where:
        - m = measure (number of vowel-consonant sequences)
        - *v* = contains vowel
        - *o = ends with consonant-vowel-consonant sequence
        - *d = ends with double consonant
        - *L = ends with 'l'
        """)

    # Example with visualization
    st.markdown("### Visual Example: Stemming 'traditionally'")
    
    traditional_steps = [
        ("traditionally", "traditional", "2: (m>0) ALLY → AL"),
        ("traditional", "tradition", "4: (m>1) AL → ''"),
    ]
    
    st.markdown("""
    <div style="border:1px solid #ddd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h4>Word: "traditionally"</h4>
        <ol>
            <li><b>traditionally</b> → <b>traditional</b> (Rule 2: ALLY → AL)</li>
            <li><b>traditional</b> → <b>tradition</b> (Rule 4: AL → '')</li>
        </ol>
        <p><b>Final stem:</b> "tradition"</p>
    </div>
    """, unsafe_allow_html=True)

# Main Streamlit app
def main():
    # Header with logo and title
    st.markdown("""
    <div class="title-container">
        <h1>📚 Porter Stemmer Interactive Demo</h1>
        <p>Explore word stemming in natural language processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs using Streamlit's native tab functionality
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
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
        <p>Porter Stemmer Interactive Demo | Natural Language Processing Tool</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()