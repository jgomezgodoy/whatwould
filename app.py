import streamlit as st
import wikipedia
import requests
import random
from duckduckgo_search import DDGS

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WhatWould",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@700;800&display=swap');

    /* ── BACKGROUND: mesh gradient + noise texture ── */
    .stApp {
        background-color: #faf9f7;
        background-image:
            radial-gradient(ellipse 80% 60% at 10% 0%, rgba(199,146,255,0.28) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 90% 10%, rgba(255,179,109,0.22) 0%, transparent 55%),
            radial-gradient(ellipse 50% 60% at 80% 90%, rgba(134,239,172,0.18) 0%, transparent 55%),
            radial-gradient(ellipse 70% 50% at 20% 85%, rgba(147,197,253,0.2) 0%, transparent 55%);
        min-height: 100vh;
    }

    * { font-family: 'DM Sans', sans-serif !important; }

    /* ── HERO ── */
    .hero {
        text-align: center;
        padding: 64px 0 20px 0;
    }

    .hero-badge {
        display: block;
        font-family: 'Syne', sans-serif !important;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        background: linear-gradient(110deg, #7c3aed, #c026d3, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-badge-sub {
        display: block;
        font-family: 'Syne', sans-serif !important;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        background: linear-gradient(110deg, #7c3aed, #c026d3, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 28px;
    }

    .hero-title {
        font-family: 'Syne', sans-serif !important;
        line-height: 0.88;
        letter-spacing: -5px;
        margin-bottom: 28px;
    }
    .hero-title .line1 {
        display: block;
        font-size: 108px;
        font-weight: 800;
        color: transparent;
        -webkit-text-stroke: 2px #18181b;
        opacity: 0.85;
    }
    .hero-title .line2 {
        display: block;
        font-size: 108px;
        font-weight: 800;
        background: linear-gradient(110deg, #7c3aed 0%, #c026d3 40%, #f43f5e 70%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-sub {
        font-size: 22px;
        font-weight: 700;
        font-style: normal;
        color: #18181b;
        line-height: 1.5;
        max-width: 520px;
        margin: 0 auto 28px auto;
    }

    /* ── GLASS CARD (input area) ── */
    .glass-card {
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.8);
        border-radius: 32px;
        padding: 40px 36px 32px 36px;
        margin: 0 0 20px 0;
        box-shadow:
            0 2px 0px rgba(255,255,255,0.9) inset,
            0 8px 40px rgba(124,58,237,0.08),
            0 2px 8px rgba(0,0,0,0.04);
    }

    /* ── ANSWER CARD (Card Play style) ── */
    .answer-card {
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.9);
        border-radius: 28px;
        padding: 36px;
        margin: 20px 0;
        box-shadow:
            0 2px 0 rgba(255,255,255,0.95) inset,
            0 12px 48px rgba(196,39,119,0.07),
            0 2px 8px rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
    }
    .answer-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #7c3aed, #c026d3, #f43f5e, #fb923c);
        border-radius: 28px 28px 0 0;
    }
    .answer-label {
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #a855f7;
        margin-bottom: 10px;
    }
    .answer-name {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 22px;
        font-weight: 700;
        font-style: normal;
        color: #18181b;
        line-height: 1.5;
        margin-bottom: 18px;
        letter-spacing: 0px;
    }
    .answer-text {
        font-size: 16px;
        font-weight: 300;
        color: #3f3f46;
        line-height: 1.9;
    }
    .answer-source {
        font-size: 11px;
        color: #a1a1aa;
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid rgba(0,0,0,0.06);
    }

    /* ── CHIPS ── */
    .chips-wrap {
        text-align: center;
        margin-bottom: 12px;
    }
    .chips-label {
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #a1a1aa;
        margin-bottom: 10px;
    }
    .chip {
        display: inline-block;
        background: rgba(255,255,255,0.65);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.9);
        border-radius: 100px;
        padding: 7px 18px;
        margin: 4px;
        font-size: 12.5px;
        font-weight: 400;
        color: #52525b;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 1.5px solid rgba(228,228,231,0.8) !important;
        border-radius: 16px !important;
        color: #18181b !important;
        font-size: 15px !important;
        padding: 14px 18px !important;
        transition: all 0.2s !important;
        caret-color: #7c3aed !important;
        caret-shape: block !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder { color: #a1a1aa !important; }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(168,85,247,0.5) !important;
        box-shadow: 0 0 0 3px rgba(168,85,247,0.1) !important;
    }
    .stTextInput label {
        color: #3f3f46 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: 0.3px !important;
    }
    .stTextArea label {
        color: #18181b !important;
        font-weight: 700 !important;
        font-size: 39px !important;
        letter-spacing: -0.5px !important;
        line-height: 1.2 !important;
        margin-bottom: 10px !important;
    }

    /* ── BUTTON ── */
    .stButton > button {
        background: linear-gradient(110deg, #7c3aed, #c026d3, #f43f5e) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 15px 32px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.25) !important;
        margin-top: 8px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stSpinner { display: none !important; }

    .heartbeat {
        text-align: center;
        padding: 40px 0;
        font-size: 72px;
        animation: heartbeat 0.8s ease-in-out infinite;
    }
    @keyframes heartbeat {
        0%   { transform: scale(1); }
        14%  { transform: scale(1.2); }
        28%  { transform: scale(1); }
        42%  { transform: scale(1.15); }
        70%  { transform: scale(1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def search_wikipedia(name: str) -> tuple[str, str, str, str]:
    """Returns (summary, page_url, resolved_name, image_url) or raises."""
    wikipedia.set_lang("en")
    try:
        results = wikipedia.search(name, results=3)
        if not results:
            return "", "", "", ""
        best_match = results[0]

        try:
            page = wikipedia.page(best_match, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)

        summary = page.content[:4000]

        # Get thumbnail from Wikipedia REST API
        image_url = ""
        try:
            slug = page.title.replace(" ", "_")
            rest = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
                timeout=5
            ).json()
            image_url = rest.get("thumbnail", {}).get("source", "")
        except Exception:
            pass

        return summary, page.url, page.title, image_url
    except Exception as e:
        st.error(f"Wikipedia error: {e}")
        return "", "", "", ""


def get_person_image(name: str, wiki_image_url: str) -> str:
    """Returns a usable image URL: Wikipedia thumbnail or DuckDuckGo fallback."""
    if wiki_image_url:
        return wiki_image_url
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(f"{name} portrait photo", max_results=3))
            for r in results:
                url = r.get("image", "")
                if url:
                    return url
    except Exception:
        pass
    return ""


def search_web_context(name: str) -> str:
    """Search DuckDuckGo for quotes, interviews and opinions from this person."""
    queries = [
        f"{name} quotes interview",
        f"{name} opinions beliefs values",
        f"{name} advice philosophy life",
    ]
    snippets = []
    try:
        with DDGS() as ddgs:
            for q in queries:
                results = ddgs.text(q, max_results=3)
                for r in results:
                    snippets.append(f"[{r['title']}] {r['body']}")
    except Exception:
        pass
    return "\n".join(snippets[:9])


def ask_groq(person: str, situation: str, wiki_text: str, web_context: str, lang_prompt: str = "Respond in English.") -> str:
    prompt = f"""You are {person}. You are speaking directly to the user who has come to you for advice.

BIOGRAPHICAL INFO (Wikipedia):
---
{wiki_text[:2500]}
---

REAL QUOTES, INTERVIEWS & KNOWN OPINIONS (from web sources):
---
{web_context[:2500]}
---

The user's situation: {situation}

Respond in first person, as {person} speaking directly to the user. Use "I" and "you".

CRITICAL RULES:
- Ground EVERYTHING in your real documented life: cite actual events, decisions, projects, failures, quotes, or moments from your biography above. Be HYPER-SPECIFIC — no generic advice.
- If a real quote or known opinion from you is directly relevant, paraphrase or echo it naturally in your voice.
- Do NOT automatically agree with the user's idea. Be honest and critical.
- If the idea contradicts your known values, beliefs or track record, push back hard with specific reasons from your life.
- Only support the idea if it genuinely maps to who you are and what you've done.
- Sound unmistakably like YOU — your rhythm, your known vocabulary, your attitude.
Keep it between 150-250 words.
{lang_prompt}

You MUST end with a clear verdict. Format it as:
**My verdict: [one blunt sentence — approve or reject the idea, and why, referencing a specific fact about your life]**"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 512,
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers=headers, json=payload, timeout=30)
    if not r.ok:
        raise Exception(f"Groq error {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"].strip()


# ── TRANSLATIONS ──────────────────────────────────────────────────────────────
T = {
    "en": {
        "hero_sub": "There are too many decisions to make every single day.<br>Let's get some advice from historic figures or your favourite movie characters.",
        "badge": "AI (Actual Icons) Powered Decisions",
        "situation_label": "Please explain what's bothering you right now...",
        "situation_placeholder": "... e.g. I like the idea of bitcoin but not sure if...",
        "what_would": "🔮 WHAT WOULD",
        "do_in": "DO IN MY SITUATION?",
        "name_placeholder": "type a name...",
        "ask_btn": "✦  Ask",
        "chips_label": "LAST QUERIES MADE TO...",
        "warning": "Please fill in both fields.",
        "not_found": "Could not find **{name}** on Wikipedia. Try a different name.",
        "tells_you": "{name} tells you...",
        "lang_prompt": "Respond in English.",
    },
    "es": {
        "hero_sub": "Hay demasiadas decisiones que tomar cada día.<br>Pidamos consejo a figuras históricas.",
        "badge": "¿Qué harían ellos en tú situación?",
        "situation_label": "Explica qué te preocupa ahora mismo...",
        "situation_placeholder": "... ej. Me gusta la idea del bitcoin pero no sé si...",
        "what_would": "🔮 QUÉ HARÍA",
        "do_in": "EN MI SITUACIÓN?",
        "name_placeholder": "escribe un nombre...",
        "ask_btn": "✦  Preguntar",
        "chips_label": "ÚLTIMAS CONSULTAS REALIZADAS A...",
        "warning": "Por favor, rellena los dos campos.",
        "not_found": "No encontré a **{name}** en Wikipedia. Prueba con otro nombre.",
        "tells_you": "{name} te dice...",
        "lang_prompt": "Responde en español.",
    },
}

# ── UI ────────────────────────────────────────────────────────────────────────

# Language selector
# Language via query params
if "lang" in st.query_params:
    st.session_state["lang"] = st.query_params["lang"]
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

lang = st.session_state["lang"]

st.markdown(f"""
<div style="display:flex;gap:8px;margin-bottom:16px;">
  <a href="?lang=en" style="text-decoration:none;">
    <img src="https://flagcdn.com/w40/gb.png" style="
      width:46px;height:30px;object-fit:cover;border-radius:8px;cursor:pointer;display:block;
      box-shadow:{'0 0 0 2.5px #7c3aed' if lang=='en' else '0 1px 4px rgba(0,0,0,0.15)'};
      opacity:{'1' if lang=='en' else '0.55'};" />
  </a>
  <a href="?lang=es" style="text-decoration:none;">
    <img src="https://flagcdn.com/w40/es.png" style="
      width:46px;height:30px;object-fit:cover;border-radius:8px;cursor:pointer;display:block;
      box-shadow:{'0 0 0 2.5px #7c3aed' if lang=='es' else '0 1px 4px rgba(0,0,0,0.15)'};
      opacity:{'1' if lang=='es' else '0.55'};" />
  </a>
</div>
""", unsafe_allow_html=True)

tx = T[lang]

st.markdown(f"""
<div class="hero">
    <div class="hero-sub">{tx["hero_sub"]}</div>
    <div class="hero-badge-sub">{tx["badge"]}</div>
</div>
""", unsafe_allow_html=True)

ICONS = [
    "Keanu Reeves", "Elon Musk", "Steve Jobs", "Frida Kahlo", "Napoleon Bonaparte",
    "Albert Einstein", "Nikola Tesla", "Oprah Winfrey", "Bruce Lee", "Marie Curie",
    "Sherlock Holmes", "Tony Stark", "Walter White", "Daenerys Targaryen", "Batman",
    "Taylor Swift", "Kanye West", "Barack Obama", "Coco Chanel", "Salvador Dalí",
    "Cristiano Ronaldo", "Beyoncé", "Mahatma Gandhi", "Winston Churchill", "Cleopatra",
    "Kobe Bryant", "Muhammad Ali", "Leonardo da Vinci", "Sigmund Freud", "Karl Marx",
    "Marilyn Monroe", "Pablo Picasso", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg",
    "Che Guevara", "Nelson Mandela", "Mother Teresa", "Julius Caesar", "Aristotle",
]

daily_seed = int(st.session_state.get("chip_seed", random.randint(0, 9999)))
if "chip_seed" not in st.session_state:
    st.session_state["chip_seed"] = daily_seed

rng = random.Random(daily_seed)
shown = rng.sample(ICONS, 6)

chips_html = "".join(f'<span class="chip">{name}</span>' for name in shown)

st.markdown(f"""
<div class="chips-wrap">
    <div class="chips-label">{tx["chips_label"]}</div>
    {chips_html}
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="margin-top:40px;"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-bottom:6px;">
    <span style="font-size:28px; line-height:1;">💀</span>
    <span style="font-size:16px; font-weight:600; color:#18181b; margin-left:10px; vertical-align:middle;">{tx["situation_label"]}</span>
</div>
""", unsafe_allow_html=True)
situation = st.text_area("", placeholder=tx["situation_placeholder"], height=120, label_visibility="collapsed")

st.markdown("""
<style>
    .inline-row { display:flex; align-items:center; gap:10px; margin:24px 0 16px 0; flex-wrap:nowrap; }
    .inline-label { font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:#18181b; letter-spacing:-1px; white-space:nowrap; }
    .inline-row .stTextInput { flex:1; min-width:0; }
    .inline-row .stTextInput > div > div > input { font-size:13px !important; padding:10px 14px !important; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2.5, 2, 3])
with col1:
    st.markdown(f'<div style="padding-top:8px;text-align:right;"><span style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#18181b;letter-spacing:-1px;">{tx["what_would"]}</span></div>', unsafe_allow_html=True)
with col2:
    person = st.text_input("", placeholder=tx["name_placeholder"], label_visibility="collapsed", key="person_input")
with col3:
    st.markdown(f'<div style="padding-top:8px;"><span style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#18181b;letter-spacing:-1px;">{tx["do_in"]}</span></div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

_, col_btn, _ = st.columns([3, 2, 3])
with col_btn:
    ask = st.button(tx["ask_btn"])

# ── LOGIC ─────────────────────────────────────────────────────────────────────
if ask:
    if not person.strip() or not situation.strip():
        st.warning(tx["warning"])
    else:
        loading = st.empty()
        loading.markdown('<div class="heartbeat">❤️</div>', unsafe_allow_html=True)

        wiki_text, wiki_url, resolved_name, image_url = search_wikipedia(person)

        if not wiki_text:
            loading.empty()
            st.error(tx["not_found"].format(name=person))
        else:
            display_name = resolved_name or person
            if True:
                try:
                    web_context = search_web_context(display_name)
                    answer = ask_groq(display_name, situation, wiki_text, web_context, tx["lang_prompt"])
                    loading.empty()

                    # Safe HTML rendering
                    import re, html
                    answer_safe = html.escape(answer)
                    answer_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', answer_safe)
                    answer_html = answer_html.replace('\n', '<br>')

                    final_image_url = get_person_image(display_name, image_url)

                    if final_image_url:
                        try:
                            img_data = requests.get(final_image_url, timeout=5).content
                            col_l, col_m, col_r = st.columns([2, 1, 2])
                            with col_m:
                                st.image(img_data, width=110)
                        except Exception:
                            pass

                    st.markdown(f"""
<div style="background:white;border-radius:24px;padding:28px;box-shadow:0 4px 24px rgba(124,58,237,0.08);border:1px solid #e9d5ff;margin-top:12px;">
  <div style="font-size:20px;font-weight:700;color:#18181b;text-align:center;margin-bottom:14px;">{tx["tells_you"].format(name=display_name)}</div>
  <div style="font-size:16px;color:#374151;line-height:1.85;">{answer_html}</div>
</div>
""", unsafe_allow_html=True)

                except Exception as e:
                    loading.empty()
                    st.error(f"Error generating response: {e}")
