# 📚 Interactive Learning Assistant

Turn any paragraph into a **short summary**, **beautiful visuals**, and **auto-generated quizzes** — all in one sleek Streamlit app.

https://user-images.githubusercontent.com/placeholder/demo.gif

## ✨ Features
- **Summarization** (Transformers with graceful fallbacks to Sumy/NLTK)
- **Visuals**
  - **Timeline** (Plotly)
  - **Map** (Folium + geocoding)
  - **Storyboard / Flow** (Graphviz)
  - **Concept Map** (Graphviz SVO)
- **Quizzes**
  - MCQ, True/False, Fill-in-the-blank, Short answer
  - Instant feedback with explanations
- Attractive Streamlit UI with cards, badges, and tabs

## 🏗 Project Structure
```
learning_assistant/
├─ app.py                  # Streamlit UI
├─ summarizer.py           # Summarization logic (transformers + fallbacks)
├─ visualizer.py           # Timeline, map, flowchart, concept map
├─ quiz_generator.py       # Question generation
├─ nlp_utils.py            # NER + keywords + sentence utils
├─ requirements.txt
└─ README.md
```

## 🚀 Quickstart
```bash
# 1) Create & activate a virtual env (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) (Optional) Download spaCy English model for best NLP
python -m spacy download en_core_web_sm

# 4) Run the app
streamlit run app.py
```

> **Note:** If you have a GPU and PyTorch installed, Transformers models will run faster.  
> **No internet?** The app falls back to rule-based extractive summarization and regex-based NER/keywords.

## 🧩 How it Works
1. **Summarizer**
   - Tries `facebook/bart-large-cnn` → falls back to `t5-small` → falls back to Sumy/NLTK → heuristic.
   - Returns **short bullet points**.
2. **NLP Utils**
   - Entities via spaCy; fallbacks via regex.
   - Keywords via YAKE/RAKE; fallback to common tokens.
3. **Visualizer**
   - **Timeline** from detected dates/years.
   - **Map** from detected GPE/LOC entities (geocoded with Nominatim).
   - **Flow/Storyboard** using sentence order.
   - **Concept Map** from SVO triples (spaCy) or heuristics.
4. **Quiz Generator**
   - Uses entities, keywords, and sentences to create MCQs, T/F, FIB, and short-answer questions.
   - Provides options and explanations.

## 🖌️ UI Highlights
- Clean cards, badges, and dashed KPI tips
- Tabs for **Timeline / Map / Flow / Concept Map**
- Interactive quizzes with immediate feedback

## 🧪 Try with Sample Text
> *"In 1492, Christopher Columbus sailed from Spain and discovered the Americas. This marked the beginning of European colonization. Vasco da Gama reached India in 1498."*

- **Summary**: concise bullets
- **Timeline**: 1492 → Columbus, 1498 → Vasco da Gama
- **Map**: Spain ↦ Americas / India
- **Quiz**: auto-generated MCQ, T/F, FIB

## 🔧 Troubleshooting
- **Graphviz not found**: install system binary (`brew install graphviz` / `sudo apt-get install graphviz` / Windows Graphviz MSI).
- **Folium map empty**: geocoding may require internet access.
- **Transformers too slow**: reduce text length or rely on Sumy/NLTK fallback.

## 📄 License
MIT — feel free to use and adapt in your projects.
