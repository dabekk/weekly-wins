from pymongo import MongoClient
import streamlit as st
from datetime import datetime, time
from streamlit_lottie import st_lottie
import requests

# Page configuration
st.set_page_config(
    page_title="CEEUR Weekly Wins",
    page_icon="🥇"
)

# Constants
TEAM_MEMBERS = [
    'Select Name','Eline', 'Josi', 'Kamil', 'Kerstin', "Moritz", 'Steffi', 
    'Carolin', 'Mieke', 'Niklas', 'Stani', 'Tobias'
]
LOTTIE_URL = "https://lottie.host/6dab44db-ae63-4dd0-aab7-6f5ebd6cbb32/yz2WTpQJFR.json"

def load_lottie_url(url):
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error loading Lottie animation: {e}")
        return None

def add_wins(weekly_win_json):
    try:
        if weekly_win_json:
            result = st.session_state.weekly_wins_coll.insert_one(weekly_win_json)
            st.success("Wins added successfully!")
        else:
            st.warning("No wins to add.")
    except Exception as e:
        st.error(f"Error adding wins: {e}")

def get_who_submitted():
    start_of_today = datetime.combine(datetime.now(), time.min)
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_of_today}}},
        {"$group": {
            "_id": "$name",
            "latestEntry": {"$max": "$timestamp"},
            "doc": {"$last": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$doc"}}
    ]

    try:
        result = list(st.session_state.weekly_wins_coll.aggregate(pipeline))
        users_who_submitted = [doc.get("name") for doc in result]
        return users_who_submitted
    except Exception as e:
        st.error(f"Error fetching submitted users: {e}")
        return []

def initialize_db():
    CONNECTION_STRING = f"mongodb+srv://{st.secrets.username}:{st.secrets.password}@weekly-wins-prod.uw7cvo6.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)
    db = client.weekly_wins_db
    st.session_state.weekly_wins_coll = db.weekly_wins_collection

# Initialize MongoDB connection
if "weekly_wins_coll" not in st.session_state:
    initialize_db()

# Initialize session state for wins and author if not already set
if "weekly_wins" not in st.session_state:
    st.session_state.weekly_wins = [{"title": "", "text": ""}]
if "author" not in st.session_state:
    st.session_state.author = TEAM_MEMBERS[0]

# Page content
st.title("CEEUR Weekly Wins")

lottie_celebrate = load_lottie_url(LOTTIE_URL)

with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("Share your weekly wins with the team and leadership!")
    with right_column:
        if lottie_celebrate:
            st_lottie(lottie_celebrate, height=300)

# Update author selection directly from selectbox
author = st.selectbox("Select your name", TEAM_MEMBERS, help="Who are you?", key="select_author")
st.session_state.author = author

# Add new weekly win entry button (outside of the form)
if st.button("Add Another Weekly Win", use_container_width=True, type="secondary"):
    st.session_state.weekly_wins.append({"title": "", "text": ""})

# Form to add weekly wins
with st.form("weekly_win_form", clear_on_submit=True):
    for i, win in enumerate(st.session_state.weekly_wins):
        win_title = st.text_input(f'Win Title {i + 1}', value=win['title'], placeholder="Customer Name - Title", key=f'title_{i}')
        win_text = st.text_area(f'Win Description {i + 1}', value=win['text'], placeholder="Win description & impact", key=f'text_{i}')
        
        # Update the session state with the latest input values
        st.session_state.weekly_wins[i] = {"title": win_title, "text": win_text}
        
        if i < len(st.session_state.weekly_wins) - 1:  # Avoid adding separator after the last win
            st.markdown("---")  # Horizontal rule as separator

    # Submit button inside this form
    submit_wins = st.form_submit_button("Submit All Wins", use_container_width=True, type="primary")

    if submit_wins:
        # Build the JSON object with an array of wins
        weekly_win_json = {
            "name": st.session_state.author,
            "timestamp": datetime.now(),
            "wins": [
                {"win_title": win['title'], "win_text": win['text']}
                for win in st.session_state.weekly_wins if win['title'] or win['text']
            ]
        }
        add_wins(weekly_win_json)
        # Clear the form inputs
        st.session_state.weekly_wins = [{"title": "", "text": ""}]  # Reset to default state

# Display users who have submitted
st.subheader("Who submitted already 😌 🥳 😍")
st.write(get_who_submitted())
