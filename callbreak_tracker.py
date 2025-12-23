import streamlit as st
import json
import os

st.set_page_config(
    page_title="Callbreak Tracker",
    layout="centered"
)

SAVE_FILE = "game_state.json"

players = ["Player A", "Player B", "Player C", "Player D"]
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

# ---------- CSS (MOBILE FIRST) ----------
st.markdown("""
<style>
button[kind="secondary"] {
    width: 100%;
    height: 42px;
    font-size: 14px;
}
.small-text {
    font-size: 14px;
}
.center {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAVE / LOAD ----------
def save_state():
    data = {
        "plays": st.session_state.plays,
        "trump": st.session_state.trump
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_state():
    if not os.path.exists(SAVE_FILE):
        return

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        st.session_state.plays = data.get("plays", [])
        st.session_state.trump = data.get("trump", "♠")

    except (json.JSONDecodeError, ValueError):
        # Corrupted or empty file → reset safely
        st.session_state.plays = []
        st.session_state.trump = "♠"

# ---------- INIT ----------
if "initialized" not in st.session_state:
    st.session_state.plays = []
    st.session_state.trump = "♠"
    load_state()
    st.session_state.initialized = True

# ---------- GAME STATE ----------
play_count = len(st.session_state.plays)
current_player = players[play_count % 4]
current_round = play_count // 4 + 1

# ---------- HEADER ----------
st.markdown("## 🃏 Callbreak Tracker")
st.markdown(
    f"<div class='center small-text'>Round {current_round} / 13 · Turn: <b>{current_player}</b></div>",
    unsafe_allow_html=True
)

st.session_state.trump = st.radio(
    "Trump",
    suits,
    horizontal=True
)

# ---------- HELPERS ----------
def card_used(card):
    return card in st.session_state.plays

def add_card(card):
    st.session_state.plays.append(card)
    save_state()

def undo():
    if st.session_state.plays:
        st.session_state.plays.pop()
        save_state()

# ---------- CURRENT ROUND ----------
st.divider()
st.markdown("### Current Round")

round_start = (current_round - 1) * 4
round_cards = st.session_state.plays[round_start: round_start + 4]

cols = st.columns(4)
for i in range(4):
    player_name = players[(round_start + i) % 4]
    card = round_cards[i] if i < len(round_cards) else "—"
    cols[i].markdown(f"{player_name}<br>{card}", unsafe_allow_html=True)

# ---------- CARD GRID (MOBILE SAFE) ----------
st.divider()
st.markdown("### Tap a card")

for suit in suits:
    st.markdown(f"{suit}")
    row = []
    for rank in ranks:
        row.append(f"{rank}{suit}")

    # 4 cards per row for mobile
    for i in range(0, len(row), 4):
        cols = st.columns(4)
        for j, card in enumerate(row[i:i+4]):
            used = card_used(card)
            label = card

            if used:
                label = f"❌ {card}"
            elif suit == st.session_state.trump:
                label = f"⭐ {card}"

            if cols[j].button(
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

c2.button("🔄 Reset", on_click=reset_game)
