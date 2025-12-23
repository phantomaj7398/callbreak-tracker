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
    except json.JSONDecodeError:
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
    f"Round: {current_round}/13 &nbsp;&nbsp; | &nbsp;&nbsp; "
    f"Turn: {current_player}"
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
    st.rerun()   # 🔑 immediate UI update

def undo():
    if st.session_state.plays:
        st.session_state.plays.pop()
        save_state()
        st.rerun()   # 🔑 immediate UI update

# ---------- CURRENT ROUND ----------
st.divider()
st.markdown("### 🟢 Current Round")

round_start = (current_round - 1) * 4
round_cards = st.session_state.plays[round_start: round_start + 4]

cols = st.columns(4)
for i in range(4):
    card = round_cards[i] if i < len(round_cards) else "—"
    cols[i].markdown(f"{players[i]}<br>{card}", unsafe_allow_html=True)

# ---------- PREVIOUS ROUNDS ----------
st.divider()
st.markdown("### 📜 Previous Rounds")

for r in range(1, current_round):
    start = (r - 1) * 4
    cards = st.session_state.plays[start: start + 4]
    if len(cards) == 4:
        st.markdown(
            f"Round {r}: " +
            " | ".join(f"{players[i]} → {cards[i]}" for i in range(4))
        )

# ---------- CARD GRID (13 × 4) ----------
st.divider()
st.markdown("### 🃏 Tap a Card")

header = st.columns(5)
header[0].markdown("Rank")
for i, suit in enumerate(suits):
    header[i + 1].markdown(f"{suit}")

for rank in ranks:
    row = st.columns(5)
    row[0].markdown(f"{rank}")

    for i, suit in enumerate(suits):
        card = f"{rank}{suit}"
        used = card_used(card)

        label = card
        if used:
            label = "❌"
        elif suit == st.session_state.trump:
            label = f"⭐{rank}"

        if row[i + 1].button(
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
