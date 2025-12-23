import streamlit as st
import json
import os

st.set_page_config(layout="wide")

SAVE_FILE = "game_state.json"

players = ["Player A", "Player B", "Player C", "Player D"]
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

# ---------- LOAD / SAVE ----------
def save_state():
    data = {
        "turn": st.session_state.turn,
        "plays": st.session_state.plays,
        "trump": st.session_state.trump
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        st.session_state.turn = data["turn"]
        st.session_state.plays = data["plays"]
        st.session_state.trump = data["trump"]

# ---------- SESSION STATE ----------
if "initialized" not in st.session_state:
    st.session_state.turn = 1
    st.session_state.plays = []
    st.session_state.trump = "♠"
    load_state()
    st.session_state.initialized = True

# ---------- UI ----------
st.title("🃏 Callbreak Card Tracker")

top1, top2, top3 = st.columns(3)
top1.markdown(f"### Turn: {st.session_state.turn}/13")
player = top2.radio("Player", players, horizontal=True)
st.session_state.trump = top3.radio("Trump", suits, horizontal=True)

# ---------- HELPERS ----------
def card_used(card):
    return any(p[2] == card for p in st.session_state.plays)

def add_card(card):
    st.session_state.plays.append(
        (st.session_state.turn, player, card)
    )

    if len([p for p in st.session_state.plays if p[0] == st.session_state.turn]) == 4:
        if st.session_state.turn < 13:
            st.session_state.turn += 1

    save_state()

def undo():
    if st.session_state.plays:
        st.session_state.plays.pop()
        st.session_state.turn = max(1, st.session_state.turn)
        save_state()

# ---------- CARD GRID ----------
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

        if cols[i].button(label, key=card, disabled=used):
            add_card(card)

# ---------- CONTROLS ----------
st.divider()
c1, c2 = st.columns(2)
c1.button("↩ Undo Last", on_click=undo)
c2.button("🔄 Reset Game", on_click=lambda: (os.remove(SAVE_FILE) if os.path.exists(SAVE_FILE) else None, st.session_state.clear()))

# ---------- HISTORY ----------
st.divider()
st.markdown("### Played Cards")

for t in range(1, st.session_state.turn + 1):
    turn_cards = [p for p in st.session_state.plays if p[0] == t]
    if turn_cards:
        st.write(
            f"Turn {t}: " +
            ", ".join(f"{p[1]} → {p[2]}" for p in turn_cards)
        )
