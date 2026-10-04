import streamlit as st
from summarizer import summarize_text
from nlp_utils import extract_entities, keywords, simple_sentences
from visualizer import parse_events, make_timeline, make_map, make_flow, triple_extract, make_concept_map
from quiz_generator import generate_quiz
from input_handler import extract_text_from_pdf, extract_text_from_url

from streamlit_folium import st_folium
import streamlit.components.v1 as components

# ---------- Page Config ----------
st.set_page_config(page_title="Interactive Learning Assistant", page_icon="📚", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
.main > div { padding-top: 1rem; }
.block-container { padding-top: 1.5rem; }
.card {
  background: white;
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.06);
  margin-bottom: 1rem;
}
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #EEF2FF;
  color: #4338CA;
  font-weight: 600;
  font-size: 0.8rem;
  margin: 2px;
}
h1, h2, h3, h4 { font-weight: 800; }
.small { opacity: 0.7; font-size: 0.9rem; }
.kpi {
  display:flex; gap:10px; align-items:center;
  background:#F8FAFF; border:1px dashed #E0E7FF;
  padding:10px 12px; border-radius:12px;
  margin-top:1rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.title("📚 Interactive Learning Assistant")
st.caption("Summarize → Visualize → Quiz — turn any text, PDF, or webpage into an interactive lesson.")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("✍️ Input")
    sample = ("In 1492, Christopher Columbus sailed from Spain and discovered the Americas. "
              "This marked the beginning of European colonization. Vasco da Gama reached India in 1498.")

    mode = st.radio("Provide text via:", ["Text box", "PDF Upload", "Web URL"], horizontal=True)

    text = ""
    if mode == "Text box":
        text = st.text_area("Paste your study text here:", sample, height=180, placeholder="Paste paragraph(s) or notes...")

    elif mode == "PDF Upload":
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file is not None:
            text = extract_text_from_pdf(uploaded_file)

    elif mode == "Web URL":
        url_input = st.text_input("Enter a webpage URL:")
        if url_input:
            text = extract_text_from_url(url_input)

    st.markdown("---")
    max_points = st.slider("📌 Summary length (bullet points)", 3, 10, 6, 1)

    st.markdown("### ⚙️ Visualization Options")
    do_timeline = st.checkbox("Generate timeline", value=True)
    do_map = st.checkbox("Show map", value=True)
    do_flow = st.checkbox("Show storyboard/flow", value=True)
    do_concepts = st.checkbox("Concept map", value=True)

    st.markdown("---")
    st.markdown("#### 📝 Quiz Settings")
    mcq = st.number_input("MCQs", 0, 10, 3)
    tfn = st.number_input("True/False", 0, 10, 2)
    fib = st.number_input("Fill-in-the-blank", 0, 10, 2)
    short = st.number_input("Short answers", 0, 10, 1)

# ---------- Guard clause ----------
if not text.strip():
    st.info("⬅️ Paste text, upload a PDF, or enter a URL in the sidebar to get started.")
    st.stop()

# ---------- NLP & Summary ----------
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 🔍 Summary")
        bullets = summarize_text(text, max_points=max_points)
        if bullets:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            for b in bullets:
                st.markdown(f"- {b}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Could not generate a summary — try shorter text.")

    with col2:
        st.markdown("### 🧩 Entities")
        ents = extract_entities(text)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        for label, items in ents.items():
            if items:
                st.markdown(f'<span class="badge">{label}</span>', unsafe_allow_html=True)
                st.write(", ".join(items[:8]))
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("### 🔑 Keywords")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(", ".join(keywords(text)[:12]))
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Visual Components ----------
st.markdown("## 🎛️ Visual Components")
tab1, tab2, tab3, tab4 = st.tabs(["🗓 Timeline", "🗺 Map", "🎬 Storyboard / Flow", "🧠 Concept Map"])

with tab1:
    if do_timeline:
        events = parse_events(text)
        if events:
            fig = make_timeline(events)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Timeline libraries unavailable.")
        else:
            st.info("No clear dates found for a timeline.")
    else:
        st.info("Timeline disabled in options.")

with tab2:
    if do_map:
        locs = (ents.get("GPE", []) or []) + (ents.get("LOC", []) or [])
        locs = list(dict.fromkeys(locs))[:8]
        if locs:
            m = make_map(locs)
            if m:
                try:
                    st_data = st_folium(m, width=None)
                except Exception:
                    html = m._repr_html_()
                    components.html(html, height=520, scrolling=False)
            else:
                st.info("Map could not be built (geocoding may require internet access).")
        else:
            st.info("No locations detected in text.")
    else:
        st.info("Map disabled in options.")

with tab3:
    if do_flow:
        sents = simple_sentences(text, max_len=140)
        g = make_flow(sents)
        if g:
            st.graphviz_chart(g.source)
        else:
            st.info("Flowchart rendering not available (Graphviz missing).")
    else:
        st.info("Storyboard/flow disabled in options.")

with tab4:
    if do_concepts:
        triples = triple_extract(text)
        g = make_concept_map(triples)
        if g:
            st.graphviz_chart(g.source)
        else:
            st.info("Concept map rendering not available (Graphviz missing).")
    else:
        st.info("Concept map disabled in options.")

# ---------- Quiz ----------
st.markdown("## 📝 Quiz")
quiz = generate_quiz(text, mcq_n=mcq, tf_n=tfn, fib_n=fib, short_n=short)

if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = {}

for i, q in enumerate(quiz):
    key = f"q_{i}"
    st.markdown(f"**Q{i+1}. ({q['type']})** {q['question']}")
    if q["type"] == "MCQ":
        choice = st.radio("Choose one:", q["options"], key=key, horizontal=True)
        if st.button("Check", key=f"chk_{i}"):
            correct = (choice == q["answer"])
            st.success("✅ Correct!") if correct else st.error(f"❌ Incorrect. Answer: **{q['answer']}**")
            st.caption(f"Explanation: {q['explanation']}")
    elif q["type"] == "True/False":
        choice = st.radio("Select:", ["True","False"], key=key, horizontal=True)
        if st.button("Check", key=f"chk_{i}"):
            correct = (choice == q["answer"])
            st.success("✅ Correct!") if correct else st.error(f"❌ Answer: **{q['answer']}**")
            st.caption(f"Explanation: {q['explanation']}")
    elif q["type"] == "Fill-in-the-blank":
        ans = st.text_input("Your answer:", key=key)
        if st.button("Check", key=f"chk_{i}"):
            correct = ans.strip().lower() == str(q["answer"]).strip().lower()
            st.success("✅ Correct!") if correct else st.error(f"❌ Answer: **{q['answer']}**")
            st.caption(f"Explanation: {q['explanation']}")
    else:  # Short answer
        st.text_area("Your response:", key=key, height=80)
        st.caption("This will be auto-graded in future versions.")

# ---------- Footer Tip ----------
st.markdown(
    '<div class="kpi">💡 Tip: Toggle visualization options in the sidebar. '
    'For best results, install optional packages listed in requirements.txt.</div>',
    unsafe_allow_html=True
)
