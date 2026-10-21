
import streamlit as st
from pymongo import MongoClient
import certifi
import socket

st.set_page_config(page_title="Suggestion Box", page_icon="", layout="centered")

# -------------------------------------------------
# MongoDB Setup
# -------------------------------------------------
def init_mongo():
    ca = certifi.where()
    client = MongoClient(
        st.secrets["MONGO_URI"],
        tlsCAFile=ca
    )
    db = client["improveit"]  # your DB name
    return db["suggestions"]  # return suggestions collection

collection = init_mongo()

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def get_next_id():
    """Auto-increment ID field for suggestions."""
    last_entry = collection.find_one(sort=[("id", -1)])
    if last_entry and "id" in last_entry:
        return last_entry["id"] + 1
    return 1

def submit_suggestion(name, department, location, suggestion, host, ip):
    entry = {
        "id": get_next_id(),
        "name": name,
        "department": department,
        "location": location,
        "suggestion": suggestion,
        "host": host,
        "ip": ip
    }
    collection.insert_one(entry)

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("Suggestion Box")

st.markdown(
    """
    Please fill out the form below to submit your suggestion.
    Your feedback is valuable and helps improve our organization.
    """
)

name = st.text_input("Your Name")
department = st.text_input("Department")
location = st.text_input("Location / Building")
suggestion = st.text_area("Your Suggestion")

host = socket.gethostname()
ip = socket.gethostbyname(host)

if st.button("Submit Suggestion"):
    if not name or not department or not location or not suggestion:
        st.error("Please complete all fields before submitting.")
    else:
        submit_suggestion(name, department, location, suggestion, host, ip)
        st.success("Thank you! Your suggestion has been submitted.")

        # Optional: Clear fields
        st.rerun()
