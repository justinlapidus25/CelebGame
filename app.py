import streamlit as st
import pandas as pd
import random
import string
import time
from rapidfuzz import process, fuzz

st.set_page_config(
    page_title="Celebrity Initials Game",
    page_icon="🎬",
    layout="wide"
)

EXCLUDED_LAST_INITIALS = ["X", "Z", "Q", "U", "V", "I", "O", "Y"]
EXCLUDED_FIRST_INITIALS = ["Z", "Q", "Y", "U", "I", "X"]

GAME_SECONDS = 300

st.markdown("""
<style>

.stApp {
    background: black;
}

.block-container {
    padding-top: .3rem;
    padding-bottom: 0rem;
    max-width: 100%;
}

h1, h2, h3, p, label, span, div {
    font-weight: 900 !important;
}

.big-title {
    text-align: center;
    font-size: 68px;
    color: #FFD700 !important;
    margin-bottom: 10px;
}

.rules-box {
    background: linear-gradient(90deg, #ffcc00, #ffffff);
    color: black !important;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 20px;
    text-align: center;
}

.rules-box p {
    font-size: 21px !important;
    margin: 0px;
}

.letter-box {
    background: linear-gradient(135deg, #ffd400, #ff9d00);
    color: black !important;
    border-radius: 12px;
    text-align: center;
    font-size: 24px !important;
    height: 48px;
    line-height: 48px;
    box-shadow: 0px 0px 10px rgba(255,180,0,.45);
}

.stTextInput {
    margin-bottom: -4px;
}

.stTextInput input {
    font-size: 28px !important;
    color: black !important;
    background: white !important;
    border: none !important;
    border-radius: 14px;
    padding: 4px 14px;
    height: 52px;
    width: 100% !important;
    text-align: center;
    box-shadow: 0px 0px 10px rgba(255,255,255,.18);
}

.timer-box {
    background: linear-gradient(135deg, #ff4d4d, #990000);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 14px;
}

.timer-box h2 {
    color: white !important;
    font-size: 22px !important;
    margin: 0px;
}

.timer-box p {
    color: #FFD700 !important;
    font-size: 42px !important;
    margin: 0px;
}

.score-box {
    background: linear-gradient(135deg, #FFD700, #ffae00);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 14px;
}

.score-box h2 {
    color: black !important;
    font-size: 22px !important;
    margin: 0px;
}

.score-box p {
    color: #660000 !important;
    font-size: 42px !important;
    margin: 0px;
}

.side-panel {
    position: sticky;
    top: 20px;
    z-index: 999;
}

.stButton > button {
    background: linear-gradient(135deg, #ffcc00, #ff9900);
    color: black !important;
    border-radius: 12px;
    border: none;
    font-size: 18px !important;
    padding: 10px 12px;
    width: 100%;
    margin-bottom: 10px;
}

.correct-label {
    color: #00ff66 !important;
    font-size: 24px !important;
    text-align: center;
    margin-top: 6px;
}

.close-label {
    color: #FFD700 !important;
    font-size: 24px !important;
    text-align: center;
    margin-top: 6px;
}

.wrong-label {
    color: #ff4d4d !important;
    font-size: 24px !important;
    text-align: center;
    margin-top: 6px;
}

.row-divider {
    height: 18px;
}

div[data-testid="column"] {
    padding: 0px !important;
}

</style>
""", unsafe_allow_html=True)

df = pd.read_csv("my_celebs.csv")
names = df["Name"].dropna().astype(str).tolist()

def get_initials(name):
    parts = name.split()

    if len(parts) >= 2:
        return parts[0][0].upper(), parts[-1][0].upper()

    return None, None

def get_valid_names(first_letter, last_letter):
    valid = []

    for name in names:
        first, last = get_initials(name)

        if last in EXCLUDED_LAST_INITIALS:
            continue

        if first in EXCLUDED_FIRST_INITIALS:
            continue

        if first == first_letter and last == last_letter:
            valid.append(name)

    return valid

def make_board():
    possible_last_letters = [
        letter for letter in string.ascii_uppercase
        if letter not in EXCLUDED_LAST_INITIALS
    ]

    possible_first_letters = [
        letter for letter in string.ascii_uppercase
        if letter not in EXCLUDED_FIRST_INITIALS
    ]

    board = {}

    for first_letter in possible_first_letters:
        valid_last_letters = [
            last_letter for last_letter in possible_last_letters
            if len(get_valid_names(first_letter, last_letter)) > 0
        ]

        if valid_last_letters:
            board[first_letter] = random.choice(valid_last_letters)

    return board

if "board" not in st.session_state:
    st.session_state.board = make_board()

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

elapsed = time.time() - st.session_state.start_time
remaining = max(0, GAME_SECONDS - int(elapsed))

minutes = remaining // 60
seconds = remaining % 60

total_rows = len(st.session_state.board)

score = 0
correct_keys = []
close_keys = []
wrong_keys = []

if st.session_state.submitted or remaining == 0:
    for first_letter, last_letter in st.session_state.board.items():
        key = f"{first_letter}{last_letter}"

        answer = st.session_state.answers.get(key, "").strip().lower()

        valid_names = get_valid_names(first_letter, last_letter)
        valid_lower = [name.lower() for name in valid_names]

        if answer in valid_lower:
            score += 1
            correct_keys.append(key)

        elif answer != "":
            match = process.extractOne(
                answer,
                valid_lower,
                scorer=fuzz.ratio
            )

            if match and match[1] >= 82:
                close_keys.append(key)
            else:
                wrong_keys.append(key)

st.markdown(
    '<div class="big-title">🎬 Celebrity Initials Game 🎬</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="rules-box">
<p>
Guess one celebrity for each row • Left letter = first initial • Right letter = last initial • Example: E L = Eva Longoria • 🟡 means close spelling
</p>
</div>
""", unsafe_allow_html=True)

main_col, side_col = st.columns([6.3, 1.4])

with side_col:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="timer-box">
            <h2>⏱ TIME</h2>
            <p>{minutes}:{seconds:02d}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="score-box">
            <h2>🏆 SCORE</h2>
            <p>{score}/{total_rows}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Submit"):
        st.session_state.submitted = True
        st.rerun()

    if st.button("New Game"):
        st.session_state.board = make_board()
        st.session_state.answers = {}
        st.session_state.submitted = False
        st.session_state.start_time = time.time()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with main_col:
    for first_letter, last_letter in st.session_state.board.items():
        key = f"{first_letter}{last_letter}"

        col1, col2, spacer1, col3, spacer2, col4 = st.columns(
            [0.55, 0.55, 0.4, 2.8, 0.4, 0.3]
        )

        with col1:
            st.markdown(
                f'<div class="letter-box">{first_letter}</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f'<div class="letter-box">{last_letter}</div>',
                unsafe_allow_html=True
            )

        with spacer1:
            st.markdown("")

        with col3:
            answer_value = st.text_input(
    label=f"{key}",
    value=st.session_state.answers.get(key, ""),
    label_visibility="collapsed",
    disabled=remaining == 0,
    key=f"input_{key}",
    autocomplete="off"
)

            st.session_state.answers[key] = answer_value

        with spacer2:
            st.markdown("")

        with col4:
            if (st.session_state.submitted or remaining == 0) and key in correct_keys:
                st.markdown('<div class="correct-label">✅</div>', unsafe_allow_html=True)

            elif (st.session_state.submitted or remaining == 0) and key in close_keys:
                st.markdown('<div class="close-label">🟡</div>', unsafe_allow_html=True)

            elif (st.session_state.submitted or remaining == 0) and key in wrong_keys:
                st.markdown('<div class="wrong-label">❌</div>', unsafe_allow_html=True)

            else:
                st.markdown("")

        st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

if remaining == 0:
    st.error("Time is up!")