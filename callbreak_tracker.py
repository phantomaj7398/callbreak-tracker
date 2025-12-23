import streamlit as st
import json
import os

st.set_page_config(
    page_title="Callbreak Tracker",
    layout="centered"
)

SAVE_FILE = "game_state.json"

suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

# ---------- CSS (MAXIMUM COMPRESSION + COLORS) ----------
st.markdown("""
<style>
/* ===== FORCE WHITE BACKGROUND ===== */
html, body, [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* ===== ROUND TEXT COLORS ===== */
.red { color: #c62828; font-weight: bold; }
.black { color: #000000; font-weight: bold; }
.used { color: #9e9e9e; }

/* ===== BUTTONS: TEXT-ONLY LOOK ===== */
button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.1rem !important;
    font-size: 0.95rem !important;
    color: #000000 !important;
}

/* remove hover / focus visuals */
button:hover,
button:focus,
button:active {
    background: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}

/* ===== TIGHT GRID ===== */
div[data-testid="column"] {
    padding-left: 0.05rem !important;
    padding-right: 0.05rem !important;
}

/* ===== REDUCE LINE GAPS ===== */
div[data-testid="stMarkdown"] p {
    margin-bottom: 0.1rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAVE / LOAD ----------
def save_state():
    with open(SAVE_FILE, "w") as f:
        json.dump({"plays": st.session_state.plays}, f)

def load_state():
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        st.session_state.plays = data.get("plays", [])
    except json.JSONDecodeError:
        st.session_state.plays = []

# ---------- INIT ----------
if "initialized" not in st.session_state:
    st.session_state.plays = []
    load_state()
    st.session_state.initialized = True

# ---------- HELPERS ----------
def card_used(card):
    return card in st.session_state.plays

def add_card(card):
    st.session_state.plays.append(card)
    save_state()
    st.rerun()

def undo():
    if st.session_state.plays:
        st.session_state.plays.pop()
        save_state()
        st.rerun()

def card_class(card):
    if card in st.session_state.plays:
        return "used"
    return "red" if card[-1] in ["♥", "♦"] else "black"

# ---------- ROUNDS (TOP, FAST RENDER) ----------
total_rounds = (len(st.session_state.plays) + 3) // 4

for r in range(total_rounds):
    start = r * 4
    cards = st.session_state.plays[start:start + 4]
    if cards:
        st.markdown(
            " ".join(
                f"<span class='{card_class(c)}'>{c}</span>"
                for c in cards
            ),
            unsafe_allow_html=True
        )

# ---------- CARD GRID (4 × 13, TIGHT) ----------
st.divider()

for suit in suits:
    cols = st.columns(len(ranks), gap="small")
    for i, rank in enumerate(ranks):
        card = f"{rank}{suit}"
        used = card_used(card)

        label = "❌" if used else card

        if cols[i].button(
            label,
            key=card,
            disabled=used
        ):
            add_card(card)

# ---------- CONTROLS ----------
st.divider()
c1, c2 = st.columns(2)
c1.button("↩ Undo", on_click=undo)

def reset_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.session_state.clear()
    st.rerun()

c2.button("🔄 Reset", on_click=reset_game)
