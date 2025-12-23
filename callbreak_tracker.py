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

# ---------- CSS (TIGHT SPACING) ----------
st.markdown("""
<style>
div[data-testid="stMarkdown"] p {
    margin-bottom: 0.2rem;
}
button {
    padding: 0.25rem !important;
    font-size: 0.8rem !important;
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

# ---------- ROUNDS (NO HEADINGS) ----------
total_rounds = (len(st.session_state.plays) + 3) // 4

for r in range(total_rounds):
    start = r * 4
    cards = st.session_state.plays[start:start + 4]
    if cards:
        st.markdown(" ".join(cards))

# ---------- CARD GRID (4 × 13) ----------
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
