import streamlit as st
import wikipedia
import requests
import random

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


def ask_groq(person: str, situation: str, wiki_text: str) -> str:
    prompt = f"""You are {person}. You are speaking directly to the user who has come to you for advice.

Here is background information about who you are:
---
{wiki_text[:3000]}
---

The user's situation: {situation}

Respond in first person, as {person} speaking directly to the user. Use "I" and "you". Channel {person}'s real personality, values, known beliefs, life experiences and way of speaking.

CRITICAL RULES:
- Do NOT automatically agree with the user's idea or plan. Be honest and critical.
- If the idea contradicts your values, personality, or known preferences, push back strongly.
- If the idea is bad, say so clearly and explain why based on who you are.
- Only support the idea if it genuinely aligns with your character.
- Be direct, opinionated, and authentic — not polite for the sake of it.
- Reference your own real experiences, decisions, or known traits when relevant.
Keep it between 150-250 words.

You MUST end with a clear verdict. Format it as:
**My verdict: [one blunt sentence — approve or reject the idea, and why]**"""

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


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-sub">There are too many decisions to make every single day.<br>Let's get some help from historic figures or your favourite movie characters.</div>
    <div class="hero-badge-sub">AI (Actual Icons) Powered Decisions</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom:6px;">
    <span style="font-size:28px; line-height:1;">💀</span>
    <span style="font-size:16px; font-weight:600; color:#18181b; margin-left:10px; vertical-align:middle;">Please explain what's bothering you right now...</span>
</div>
""", unsafe_allow_html=True)
situation = st.text_area("", placeholder="... e.g. I like the idea of bitcoin but not sure if...", height=120, label_visibility="collapsed")

st.markdown("""
<style>
    .inline-row { display:flex; align-items:center; gap:10px; margin:24px 0 16px 0; flex-wrap:nowrap; }
    .inline-label { font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:#18181b; letter-spacing:-1px; white-space:nowrap; }
    .inline-row .stTextInput { flex:1; min-width:0; }
    .inline-row .stTextInput > div > div > input { font-size:13px !important; padding:10px 14px !important; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    st.markdown('<div style="padding-top:8px;"><span style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#18181b;letter-spacing:-1px;">🔮 WHAT WOULD</span></div>', unsafe_allow_html=True)
with col2:
    person = st.text_input("", placeholder="type a name...", label_visibility="collapsed", key="person_input")
with col3:
    st.markdown('<div style="padding-top:8px;"><span style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#18181b;letter-spacing:-1px;">DO IN MY SITUATION?</span></div>', unsafe_allow_html=True)

ask = st.button("✦  Ask")

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
    <div class="chips-label">Latest advices coming from...</div>
    {chips_html}
</div>
""", unsafe_allow_html=True)

# ── LOGIC ─────────────────────────────────────────────────────────────────────
if ask:
    if not person.strip() or not situation.strip():
        st.warning("Please fill in both fields.")
    else:
        loading = st.empty()
        loading.markdown('<div class="heartbeat">❤️</div>', unsafe_allow_html=True)

        wiki_text, wiki_url, resolved_name, image_url = search_wikipedia(person)

        if not wiki_text:
            loading.empty()
            st.error(f"Could not find **{person}** on Wikipedia. Try a different name.")
        else:
            display_name = resolved_name or person
            if True:
                try:
                    answer = ask_groq(display_name, situation, wiki_text)
                    loading.empty()

                    # Safe HTML rendering
                    import re, html
                    answer_safe = html.escape(answer)
                    answer_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', answer_safe)
                    answer_html = answer_html.replace('\n', '<br>')

                    st.write(f"DEBUG image_url: {image_url}")
                    col_img, col_txt = st.columns([1, 4])
                    with col_img:
                        if image_url:
                            try:
                                img_data = requests.get(image_url, timeout=5).content
                                st.image(img_data, width=120)
                            except Exception:
                                pass
                    with col_txt:
                        st.markdown(f"""
<div style="background:white;border-radius:24px;padding:28px;box-shadow:0 4px 24px rgba(124,58,237,0.08);border:1px solid #e9d5ff;">
  <div style="font-size:20px;font-weight:700;color:#18181b;margin-bottom:14px;">{display_name} tells you...</div>
  <div style="font-size:16px;color:#374151;line-height:1.85;">{answer_html}</div>
</div>
""", unsafe_allow_html=True)

                except Exception as e:
                    loading.empty()
                    st.error(f"Error generating response: {e}")
