import streamlit as st
import json
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Callbreak Tracker", layout="centered")

SAVE_FILE = "game_state.json"

players = ["A", "B", "C", "D"]
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
rank_power = {r: i for i, r in enumerate(ranks[::-1])}

TRUMP = "♠"

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: white !important;
    color: black !important;
}
button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.1rem !important;
    font-size: 0.95rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SAVE / LOAD ----------------
def save_state(plays):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(plays, f)
    except Exception:
        pass

def load_state():
    if not os.path.exists(SAVE_FILE):
        return []
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

# ---------------- INIT ----------------
if "plays" not in st.session_state:
    st.session_state.plays = load_state()

plays = st.session_state.plays

# ---------------- GAME LOGIC ----------------
def card_strength(card, lead_suit):
    rank, suit = card[:-1], card[-1]
    if suit == TRUMP:
        return 100 + rank_power[rank]
    if suit == lead_suit:
        return 50 + rank_power[rank]
    return rank_power[rank]

def determine_winner(cards, starter):
    lead_suit = cards[0][-1]
    strengths = [card_strength(c, lead_suit) for c in cards]
    winner_offset = strengths.index(max(strengths))
    return (starter + winner_offset) % 4

# ---------------- ROUNDS ----------------
def rebuild_rounds(plays):
    rounds = []
    starter = 0  # A starts first round
    i = 0

    while i < len(plays):
        chunk = plays[i:i + 4]

        cards = []
        for idx, card in enumerate(chunk):
            player = players[(starter + idx) % 4]
            cards.append((player, card))

        rounds.append(cards)

        if len(chunk) == 4:
            starter = determine_winner([c for _, c in cards], starter)

        i += 4

    return rounds

rounds = rebuild_rounds(plays)

# ---------------- CARD RENDERING ----------------
def render_card(card):
    suit = card[-1]
    color = "red" if suit in ["♥", "♦"] else "black"
    return f"<span style='color:{color}; font-weight:600'>{card}</span>"

# ---------------- DISPLAY ----------------
for cards in rounds:
    line = " &nbsp;&nbsp; ".join(
        [f"<b>{p}</b> → {render_card(c)}" for p, c in cards]
    )
    st.markdown(line, unsafe_allow_html=True)

# ---------------- CARD GRID ----------------
st.divider()
used = set(plays)

for suit in suits:
    cols = st.columns(len(ranks))
    for i, rank in enumerate(ranks):
        card = f"{rank}{suit}"
        cols[i].button(
            "❌" if card in used else card,
            key=card,
            disabled=card in used,
            on_click=lambda c=card: (plays.append(c), save_state(plays), st.rerun())
        )

# ---------------- CONTROLS ----------------
st.divider()
c1, c2 = st.columns(2)

c1.button("↩ Undo", on_click=lambda: (plays.pop(), save_state(plays), st.rerun()) if plays else None)
c2.button("🔄 Reset", on_click=lambda: (os.remove(SAVE_FILE) if os.path.exists(SAVE_FILE) else None, st.session_state.clear(), st.rerun()))
