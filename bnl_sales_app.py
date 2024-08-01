from pymongo import MongoClient
import streamlit as st
from datetime import datetime, time
from streamlit_lottie import st_lottie
import requests

st.set_page_config(
    page_title="BNL Sales - Weekly Wins",
    page_icon="🥇"
)

def load_lottie_url(url):
    request = requests.get(url, timeout=2)
    if request.status_code != 200:
        return None
    return request.json()

def add_win(weekly_win_json):
    result = st.session_state.weekly_wins_coll.insert_one(weekly_win_json)
    document_id = result.inserted_id
    print(f"_id of inserted document: {document_id}")

    st.toast("Message sent successfully!")

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

    result = list(st.session_state.weekly_wins_coll.aggregate(pipeline))

    users_who_submitted = []    
    # Print the result
    for doc in result:
        users_who_submitted.append(doc.get("name"))
        print(doc)
    
    return users_who_submitted

def get_who_did_not_submit():
    users_who_did_not_submit = []

    return users_who_did_not_submit

st.title("BNL Sales Weekly Wins")

lottie_celebrate = load_lottie_url(
    "https://lottie.host/6dab44db-ae63-4dd0-aab7-6f5ebd6cbb32/yz2WTpQJFR.json")

with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("")
        st.subheader("")
        st.subheader("")
        st.subheader("Share your weekly wins with the team and leadership!")
    with right_column:
        st_lottie(lottie_celebrate, height=300)

if "weekly_wins_coll" not in st.session_state:
    CONNECTION_STRING = "mongodb+srv://" + st.secrets.bnl_sales_username + ":" + st.secrets.bnl_sales_password + "@weekly-wins-prod.uw7cvo6.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)
    db = client.weekly_wins_db
    st.session_state.weekly_wins_coll = db.weekly_wins_bnl_sales

TEAM_MEMBERS = ['Select Name', 'Brice', 'Christian', 'Jeff', 'Jeffrey', 'Jovan',
                 'Karen', 'Kevin', 'Patrick', 'Ruud']
    
with st.form("weekly_win_form", clear_on_submit=True, border=False):
    author = st.selectbox("Select your name", TEAM_MEMBERS, help="""Who are you?""")
   
    weekly_win_text = st.text_area('Weekly Win', placeholder='Input your weekly win here', height=200)    
    weekly_win_json =  {"name": author, "timestamp": datetime.now(), "win_text": weekly_win_text}
    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        add_win(weekly_win_json)

st.subheader("Who submitted already 😌 🥳 😍")
st.write(get_who_submitted())