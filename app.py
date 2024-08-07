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
    'Select Name', 'Benjamin', 'Josi', 'Kamil', 'Kerstin', 'Steffi', 'Valeria', 
    'Carolin', 'Daniel', 'Mieke', 'Niklas', 'Stani', 'Steph', 'Tobias'
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

def add_win(weekly_win_json):
    try:
        result = st.session_state.weekly_wins_coll.insert_one(weekly_win_json)
        st.success("Message sent successfully!")
        return result.inserted_id
    except Exception as e:
        st.error(f"Error adding win: {e}")
        return None

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

with st.form("weekly_win_form", clear_on_submit=True):
    # Selectbox for author
    author = st.selectbox("Select your name", TEAM_MEMBERS, help="Who are you?")
    
    # Text area for weekly win
    weekly_win_text = st.text_area('Weekly Win', placeholder='Input your weekly win here', height=200)    
    
    # Create JSON object with form data
    weekly_win_json = {
        "name": author,
        "timestamp": datetime.now(),
        "win_text": weekly_win_text
    }
    
    # Submit button
    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    # Handle form submission
    if submitted:
        add_win(weekly_win_json)

st.subheader("Who submitted already 😌 🥳 😍")
st.write(get_who_submitted())
