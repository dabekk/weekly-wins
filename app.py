from pymongo import MongoClient
import streamlit as st
from datetime import datetime, time

st.set_page_config(
    page_title="CEEUR Weekly Wins",
    page_icon="🥇"
)

st.title("CEEUR Weekly Wins")

st.subheader("Share your weekly wins with the team and leadership!")

if "weekly_wins_coll" not in st.session_state:
    CONNECTION_STRING = "mongodb+srv://kamildabek:5dhoi9FqcLJk46QR@weekly-wins-prod.uw7cvo6.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)
    db = client.weekly_wins_db
    st.session_state.weekly_wins_coll = db.weekly_wins_collection

TEAM_MEMBERS = ['Benjamin', 'Josi', 'Kamil', 'Kerstin', 'Steffi', 'Valeria', 
                               'Daniel', 'Mieke', 'Niklas', 'Stani', 'Steph', 'Tobias']

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
    
    # query = {"timestamp": {"$gt": start_of_today}}
    # submitted_today = list(st.session_state.weekly_wins_coll.find(query))
    # for doc in submitted_today:
    #     print(doc) 
    
    return users_who_submitted

def get_who_did_not_submit():
    users_who_did_not_submit = []

    return users_who_did_not_submit
    
with st.form("weekly_win_form", clear_on_submit=True, border=False):
    author = st.selectbox("Select your name", TEAM_MEMBERS, help="""Who are you?""")
   
    weekly_win_text = st.text_area('Weekly Win', placeholder='Input your weekly win here', height=200)    
    weekly_win_json =  {"name": author, "timestamp": datetime.now(), "win_text": weekly_win_text}
    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        add_win(weekly_win_json)

# st.subheader("Not submitted yet 😤😤😤")
st.subheader("Who submitted already 😌🥳😍")
st.write(get_who_submitted())