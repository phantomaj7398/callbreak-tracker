import streamlit as st
import json
import os

st.set_page_config(
    layout="centered",
    page_title="Callbreak Tracker"
)

SAVE_FILE = "game_state.json"

players = ["Player A", "Player B", "Player C", "Player D"]
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

# ----------------- SAVE / LOAD -----------------
def save_state():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state, f)

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            st.session_state[k] = v

# ----------------- INIT -----------------
if "initialized" not in st.session_state:
    st.session_state.plays = []  # list of cards in order
    st.session_state.trump = "♠"
    load_state()
    st.session_state.initialized = True

# ----------------- GAME STATE -----------------
play_count = len(st.session_state.plays)
current_player = players[play_count % 4]
current_round = play_count // 4 + 1

# ----------------- HEADER -----------------
st.markdown("## 🃏 Callbreak Tracker")
st.markdown(f"Round: {current_round} / 13")
st.markdown(f"Turn: {current_player}")

st.session_state.trump = st.radio(
    "Trump",
    suits,
    horizontal=True
)

# ----------------- HELPERS -----------------
def card_used(card):
    return card in st.session_state.plays

def add_card(card):
    st.session_state.plays.append(card)
    save_state()

def undo():
    if st.session_state.plays:
        st.session_state.plays.pop()
        save_state()

# ----------------- CURRENT ROUND VIEW -----------------
st.divider()
st.markdown("### Current Round")

round_start = (current_round - 1) * 4
round_cards = st.session_state.plays[round_start:round_start + 4]

round_cols = st.columns(4)
for i in range(4):
    if i < len(round_cards):
        round_cols[i].markdown(
            f"{players[i]}  \n{round_cards[i]}"
        )
    else:
        round_cols[i].markdown(
            f"{players[i]}  \n—"
        )

# ----------------- CARD GRID -----------------
st.divider()
st.markdown("### Tap a card")

for suit in suits:
    cols = st.columns(len(ranks))
    for i, rank in enumerate(ranks):
        card = f"{rank}{suit}"
        used = card_used(card)

        label = card
        if used:
            label = f"❌ {card}"
        elif suit == st.session_state.trump:
            label = f"⭐ {card}"

        if cols[i].button(
            label,
            key=card,
            disabled=used
        ):
            add_card(card)

# ----------------- CONTROLS -----------------
st.divider()
c1, c2 = st.columns(2)

c1.button("↩ Undo", on_click=undo)

def reset_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.session_state.clear()

c2.button("🔄 Reset", on_click=reset_game)
