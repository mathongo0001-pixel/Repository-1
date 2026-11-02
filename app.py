import base64
import os
import random
from pathlib import Path

import streamlit as st
from sarvamai import SarvamAI

st.set_page_config(page_title="Memory Match", page_icon="🧠", layout="centered")

# ---------- API key: environment / .env locally, Streamlit Secrets when deployed ----------
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() and not key.startswith("#"):
            os.environ.setdefault(key.strip(), value.strip())


def get_key():
    key = os.environ.get("SARVAM_API_KEY")
    if key:
        return key
    try:
        return st.secrets["SARVAM_API_KEY"]
    except Exception:
        return None


# ---------- Text ----------
LANGS = {"English": "en-IN", "हिन्दी": "hi-IN", "मराठी": "mr-IN"}

T = {
    "en-IN": {
        "title": "Memory Match",
        "help": "Tap a card to turn it over. Find the two cards that match.",
        "pairs": "Number of pairs",
        "new": "New game",
        "next": "Try again",
        "speak": "Speak aloud",
        "match": "Well done! That is a match.",
        "nomatch": "Not a match. Take your time and try again.",
        "win": "Wonderful! You found all the pairs.",
        "novoice": "Voice is not available right now.",
        "nokey": "Voice is off: no Sarvam key was found.",
    },
    "hi-IN": {
        "title": "याददाश्त का खेल",
        "help": "किसी भी कार्ड को छूकर पलटिए। एक जैसे दो कार्ड ढूंढिए।",
        "pairs": "जोड़ियों की संख्या",
        "new": "नया खेल",
        "next": "फिर से कोशिश करें",
        "speak": "बोलकर सुनाएँ",
        "match": "बहुत बढ़िया! यह जोड़ी मिल गई।",
        "nomatch": "यह जोड़ी नहीं है। कोई बात नहीं, फिर से कोशिश कीजिए।",
        "win": "शाबाश! आपने सभी जोड़ियाँ ढूंढ लीं।",
        "novoice": "अभी आवाज़ उपलब्ध नहीं है।",
        "nokey": "आवाज़ बंद है: Sarvam की कुंजी नहीं मिली।",
    },
    "mr-IN": {
        "title": "आठवणीचा खेळ",
        "help": "पत्त्याला स्पर्श करून तो उलटा. सारखे दोन पत्ते शोधा.",
        "pairs": "जोड्यांची संख्या",
        "new": "नवीन खेळ",
        "next": "पुन्हा प्रयत्न करा",
        "speak": "मोठ्याने बोला",
        "match": "खूप छान! ही जोडी जुळली.",
        "nomatch": "ही जोडी नाही. काळजी करू नका, पुन्हा प्रयत्न करा.",
        "win": "शाबास! तुम्हाला सर्व जोड्या सापडल्या.",
        "novoice": "आवाज सध्या उपलब्ध नाही.",
        "nokey": "आवाज बंद आहे: Sarvam ची किल्ली सापडली नाही.",
    },
}

SYMBOLS = ["🍎", "🐶", "🌸", "⭐", "🚗", "🎈"]


# ---------- Voice (Sarvam Bulbul text-to-speech) ----------
@st.cache_data(show_spinner=False)
def speak(text: str, lang_code: str) -> bytes:
    client = SarvamAI(api_subscription_key=get_key())
    common = dict(text=text, model="bulbul:v3", speaker="shubh")
    try:
        response = client.text_to_speech.convert(target_language_code=lang_code, **common)
    except TypeError:  # some SDK versions name this parameter differently
        response = client.text_to_speech.convert(language_code=lang_code, **common)
    audios = getattr(response, "audios", None) or getattr(response, "audio", None)
    if isinstance(audios, str):
        audios = [audios]
    return base64.b64decode("".join(audios))


# ---------- Game state ----------
def new_game():
    n = st.session_state.get("pairs_choice", 3)
    cards = SYMBOLS[:n] * 2
    random.shuffle(cards)
    st.session_state.update(
        cards=cards, up=[], matched=set(), mismatch=False, status=None, say=None
    )


def flip(i):
    s = st.session_state
    if s.mismatch or i in s.matched or i in s.up:
        return
    s.up.append(i)
    if len(s.up) == 2:
        a, b = s.up
        if s.cards[a] == s.cards[b]:
            s.matched.update(s.up)
            s.up = []
            s.status = "win" if len(s.matched) == len(s.cards) else "match"
            s.say = s.status
        else:
            s.mismatch = True
            s.status = "nomatch"
            s.say = "nomatch"


def try_again():
    st.session_state.update(up=[], mismatch=False, status=None, say=None)


if "cards" not in st.session_state:
    new_game()

# ---------- Look: calm, high contrast, very large targets ----------
st.markdown(
    """
<style>
html, body, [class*="st-"] { font-family: "Verdana", "Segoe UI", sans-serif; }
h1 { font-size: 2.6rem !important; color: #0B2545; }
[class*="st-key-down_"] button, [class*="st-key-up_"] button, [class*="st-key-done_"] button {
    height: 120px; border-radius: 16px; border: 5px solid #0B2545; opacity: 1;
}
[class*="st-key-down_"] button { background: #0B2545; }
[class*="st-key-down_"] button:hover, [class*="st-key-down_"] button:focus,
[class*="st-key-down_"] button:active { background: #1D4F91; border-color: #0B2545; }
[class*="st-key-down_"] button:hover p, [class*="st-key-down_"] button:focus p,
[class*="st-key-down_"] button:active p { color: #FFFFFF; }
[class*="st-key-up_"] button { background: #FFFFFF; }
[class*="st-key-done_"] button, [class*="st-key-done_"] button:disabled {
    background: #D8F3DC; border-color: #1B7F3B;
}
[class*="st-key-down_"] button p { color: #FFFFFF; font-size: 3.2rem; line-height: 1; }
[class*="st-key-up_"] button p, [class*="st-key-done_"] button p {
    color: #000000; font-size: 3.8rem; line-height: 1;
}
[class*="st-key-again"] button, [class*="st-key-newgame"] button {
    height: 80px; border: 4px solid #0B2545; border-radius: 16px;
}
[class*="st-key-again"] button p, [class*="st-key-newgame"] button p { font-size: 1.6rem; }
.msg { font-size: 1.7rem; padding: 16px 20px; border-radius: 12px;
       border: 4px solid #0B2545; background: #FFF8DC; color: #000; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Controls ----------
lang_name = st.radio("Language / भाषा", list(LANGS), horizontal=True)
lang = LANGS[lang_name]
t = T[lang]

st.title(t["title"])
st.write(t["help"])

c1, c2 = st.columns(2)
with c1:
    st.radio(t["pairs"], [2, 3, 4, 5, 6], index=1, horizontal=True,
             key="pairs_choice", on_change=new_game)
with c2:
    voice_on = st.checkbox(t["speak"], value=True)

# ---------- Board ----------
s = st.session_state
cols = st.columns(4)
for i, symbol in enumerate(s.cards):
    with cols[i % 4]:
        if i in s.matched:
            st.button(symbol, key=f"done_{i}", disabled=True, use_container_width=True)
        elif i in s.up:
            st.button(symbol, key=f"up_{i}", use_container_width=True)
        else:
            st.button("?", key=f"down_{i}", on_click=flip, args=(i,),
                      use_container_width=True)

# ---------- Feedback ----------
if s.status:
    st.markdown(f'<div class="msg">{t[s.status]}</div>', unsafe_allow_html=True)

if s.mismatch:
    st.button(t["next"], key="again", on_click=try_again, use_container_width=True)

if s.status == "win":
    st.balloons()

# Speak once, in the run where the event happened
if s.say:
    phrase = t[s.say]
    s.say = None
    if voice_on:
        if not get_key():
            st.caption(t["nokey"])
        else:
            try:
                st.audio(speak(phrase, lang), format="audio/wav", autoplay=True)
            except Exception as e:
                st.caption(f'{t["novoice"]} [{type(e).__name__}: {str(e)[:300]}]')

st.divider()
st.button(t["new"], key="newgame", on_click=new_game, use_container_width=True)
