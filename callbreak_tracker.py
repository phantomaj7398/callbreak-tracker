import streamlit as st
import json
import os

st.set_page_config(page_title="Callbreak Tracker", layout="centered")

SAVE_FILE = "game_state.json"

players = ["A", "B", "C", "D"]
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
rank_value = {r: i for i, r in enumerate(ranks[::-1])}  # higher = stronger

TRUMP = "♠"

# ---------- CSS ----------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.1rem !important;
    font-size: 0.95rem !important;
}
button:hover, button:focus, button:active {
    background: transparent !important;
    outline: none !important;
}
div[data-testid="column"] {
    padding-left: 0.05rem !important;
    padding-right: 0.05rem !important;
}
div[data-testid="stMarkdown"] p {
    margin-bottom: 0.1rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAVE / LOAD ----------
def save_state():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.state, f)

def load_state():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

# ---------- GAME LOGIC ----------
def card_strength(card, lead_suit):
    rank = card[:-1]
    suit = card[-1]

    if suit == TRUMP:
        return 100 + rank_value[rank]
    if suit == lead_suit:
        return 50 + rank_value[rank]
    return rank_value[rank]

def trick_winner(cards, starter_index):
    lead_suit = cards[0][-1]
    strengths = [card_strength(c, lead_suit) for c in cards]
    winner_offset = strengths.index(max(strengths))
    return (starter_index + winner_offset) % 4

# ---------- INIT ----------
if "state" not in st.session_state:
    saved = load_state()
    if saved:
        st.session_state.state = saved
    else:
        st.session_state.state = {
            "rounds": [],        # list of {starter, cards, winner}
            "current": {
                "starter": 0,    # index in players
                "cards": []
            }
        }

state = st.session_state.state

# ---------- HELPERS ----------
def add_card(card):
    state["current"]["cards"].append(card)

    if len(state["current"]["cards"]) == 4:
        starter = state["current"]["starter"]
        cards = state["current"]["cards"]

        winner = trick_winner(cards, starter)

        state["rounds"].append({
            "starter": starter,
            "cards": cards,
            "winner": winner
        })

        state["current"] = {
            "starter": winner,
            "cards": []
        }

    save_state()
    st.rerun()

def undo():
    if state["current"]["cards"]:
        state["current"]["cards"].pop()
    elif state["rounds"]:
        last = state["rounds"].pop()
        state["current"] = {
            "starter": last["starter"],
            "cards": last["cards"][:-1]
        }
    save_state()
    st.rerun()

def used_cards():
    used = []
    for r in state["rounds"]:
        used.extend(r["cards"])
    used.extend(state["current"]["cards"])
    return set(used)

# ---------- DISPLAY ROUNDS ----------
for r in state["rounds"]:
    starter = players[r["starter"]]
    cards = " ".join(r["cards"])
    st.markdown(f"**{starter} →** {cards}")

# current round
if state["current"]["cards"]:
    starter = players[state["current"]["starter"]]
    cards = " ".join(state["current"]["cards"])
    st.markdown(f"**{starter} →** {cards}")

# ---------- CARD GRID ----------
st.divider()
used = used_cards()

for suit in suits:
    cols = st.columns(len(ranks), gap="small")
    for i, rank in enumerate(ranks):
        card = f"{rank}{suit}"
        if cols[i].button(
            "❌" if card in used else card,
            key=card,
            disabled=card in used
        ):
            add_card(card)

# ---------- CONTROLS ----------
st.divider()
c1, c2 = st.columns(2)
c1.button("↩ Undo", on_click=undo)

def reset():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.session_state.clear()
    st.rerun()

c2.button("🔄 Reset", on_click=reset)
