import streamlit as st
import pandas as pd
import random
import time
import datetime
import unicodedata
from difflib import get_close_matches

st.set_page_config(
    page_title="Celebrity Alphabet Game",
    layout="wide"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fredoka', sans-serif;
}

.stApp {

    background: linear-gradient(
        135deg,
        #FFE6F2 0%,
        #E3F8FF 50%,
        #FFF4CC 100%
    );

}


/* TITLE */
.title {

    font-size: 58px;

    font-weight:700;

    color:#5A3E85;

    margin-bottom:5px;

    text-shadow:
    3px 3px white;

}


/* Subtitle */
.subtitle {

    font-size:20px;

    color:#675875;

    margin-bottom:30px;

}


/* Sidebar */
.sidebar-box {

    background:white;

    padding:25px;

    border-radius:28px;

    border:3px solid white;

    box-shadow:
    0px 10px 30px rgba(90,70,130,.18);

}


/* Big Letter Tiles */
.letter-box {

    background: linear-gradient(
        135deg,
        #7C6DFF,
        #FF7ACD
    );

    color:white;

    border-radius:20px;

    border:4px solid white;

    text-align:center;

    padding:12px;

    font-size:30px;

    font-weight:700;

    box-shadow:
    0px 6px 18px rgba(80,60,120,.30);

}


/* Inputs */
.stTextInput input {

    background:white;

    border-radius:18px;

    border:3px solid #D8CCFF;

    padding:12px;

    font-size:20px;

    font-weight:600;

}


/* Buttons */
.stButton button {

    background: linear-gradient(
        135deg,
        #8E7CFF,
        #FF8FD8
    );

    color:white;

    border-radius:18px;

    border:none;

    font-weight:700;

    font-size:17px;

}


.correct-label {

    color:#20A65A;

    font-size:30px;

}

.close-label {

    color:#D99A00;

    font-size:30px;

}

.wrong-label {

    color:#E84C61;

    font-size:30px;

}

.row-divider {

    border-bottom:2px solid rgba(255,255,255,.7);

    margin:10px 0;

}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_names():

    df = pd.read_csv("combined_names.csv")

    return sorted(
        set(
            df["Name"]
            .dropna()
            .astype(str)
            .str.strip()
        )
    )


celebrity_names = load_names()


def normalize_name(name):

    name = name.lower().strip()

    name = unicodedata.normalize(
        "NFKD",
        name
    )

    return "".join(
        c for c in name 
        if not unicodedata.combining(c)
    )


normalized_names = {
    normalize_name(x):x 
    for x in celebrity_names
}


# -----------------------------
# Game Setup
# -----------------------------
LETTERS = [

"A","B","C","D","E",
"F","G","H","J","K",
"L","M","N","O","P",
"R","S","T","V","W"

]


def make_board(seed=None):

    rng=random.Random(seed)

    first=LETTERS.copy()
    last=LETTERS.copy()

    rng.shuffle(first)
    rng.shuffle(last)

    return dict(
        zip(first,last)
    )


def daily_seed():

    return int(
        datetime.date.today()
        .strftime("%Y%m%d")
    )


def start_daily():

    st.session_state.mode="Daily Puzzle"

    st.session_state.board=make_board(
        daily_seed()
    )

    st.session_state.answers={}

    st.session_state.submitted=False

    st.session_state.start=time.time()



def start_random():

    st.session_state.mode="Random Game"

    st.session_state.board=make_board()

    st.session_state.answers={}

    st.session_state.submitted=False

    st.session_state.start=time.time()



if "board" not in st.session_state:

    start_daily()



# -----------------------------
# Checking
# -----------------------------
def valid(answer,a,b):

    answer=normalize_name(answer)

    if answer in normalized_names:

        parts=normalized_names[answer].split()

        return (
            parts[0][0].upper()==a
            and
            parts[-1][0].upper()==b
        )

    return False



# -----------------------------
# Timer 5 minutes
# -----------------------------
GAME_SECONDS=300

remaining=max(
    0,
    GAME_SECONDS-int(
        time.time()-st.session_state.start
    )
)

minutes=remaining//60

seconds=remaining%60



correct=[]
wrong=[]

if st.session_state.submitted:

    for a,b in st.session_state.board.items():

        key=a+b

        if valid(
            st.session_state.answers.get(key,""),
            a,b
        ):
            correct.append(key)

        else:
            wrong.append(key)


score=len(correct)



# -----------------------------
# Page
# -----------------------------
today=datetime.date.today().strftime(
    "%A, %B %d, %Y"
)


st.markdown(
    '<div class="title">Celebrity Alphabet Game</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Match the initials. Name the celebrity. Beat your friends.</div>',
    unsafe_allow_html=True
)



side,main=st.columns([1.1,3])


with side:

    st.markdown(
        '<div class="sidebar-box">',
        unsafe_allow_html=True
    )

    st.subheader(st.session_state.mode)

    st.write(today)

    st.metric(
        "Time Left",
        f"{minutes}:{seconds:02d}"
    )

    st.metric(
        "Score",
        f"{score}/20"
    )


    if st.button("Submit"):

        st.session_state.submitted=True


    if st.button("Daily Puzzle"):

        start_daily()

        st.rerun()


    if st.button("Random Game"):

        start_random()

        st.rerun()


    st.write("✅ Correct")
    st.write("❌ Incorrect")


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


with main:

    for a,b in st.session_state.board.items():

        key=a+b


        c1,c2,space,c3,c4=st.columns(
            [0.5,0.5,.3,3,.5]
        )


        with c1:

            st.markdown(
                f'<div class="letter-box">{a}</div>',
                unsafe_allow_html=True
            )


        with c2:

            st.markdown(
                f'<div class="letter-box">{b}</div>',
                unsafe_allow_html=True
            )


        with c3:

            ans=st.text_input(
                "",
                key=f"input_{key}",
                disabled=st.session_state.submitted
            )

            st.session_state.answers[key]=ans


        with c4:

            if key in correct:

                st.markdown(
                    '<div class="correct-label">✅</div>',
                    unsafe_allow_html=True
                )

            elif key in wrong:

                st.markdown(
                    '<div class="wrong-label">❌</div>',
                    unsafe_allow_html=True
                )


        st.markdown(
            '<div class="row-divider"></div>',
            unsafe_allow_html=True
        )