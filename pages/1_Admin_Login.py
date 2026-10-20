import streamlit as st
import sqlite3
import bcrypt
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", page_icon="", layout="wide")

# -------------------------------------------------
# Database Functions
# -------------------------------------------------
def get_data():
    conn = sqlite3.connect("suggestions.db")
    df = pd.read_sql_query("SELECT * FROM suggestions", conn)
    conn.close()
    return df

def verify_admin(username, password):
    conn = sqlite3.connect("suggestions.db")
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM admin WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False

    stored_hash = row[0]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    return bcrypt.checkpw(password.encode(), stored_hash)

def delete_suggestion(entry_id):
    conn = sqlite3.connect("suggestions.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM suggestions WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

# -------------------------------------------------
# Dialog Function (Native Streamlit Modal)
# -------------------------------------------------
@st.dialog("Delete Suggestion?")
def delete_dialog(entry_id):
    st.markdown(
        """
        <div style='padding: 10px;'>
            <p style="font-size: 16px; margin-bottom: 15px;">
                Are you sure you want to permanently delete this suggestion?
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    colA, colB = st.columns(2)

    with colA:
        if st.button("Yes, delete", key="confirm_delete"):
            delete_suggestion(entry_id)
            st.success("The suggestion has been deleted.")
            st.rerun()

    with colB:
        if st.button("Cancel", key="cancel_delete"):
            st.rerun()

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "expand_all" not in st.session_state:
    st.session_state.expand_all = False


# -------------------------------------------------
# Title & Login
# -------------------------------------------------
st.title("Admin Dashboard")

if not st.session_state.admin_logged_in:
    st.subheader("Administrator Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

    if login:
        if verify_admin(username, password):
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

st.success("Logged in as admin")

logout = st.button("Log out")
if logout:
    st.session_state.admin_logged_in = False
    st.rerun()

# -------------------------------------------------
# Load Data
# -------------------------------------------------
df = get_data()

if df.empty:
    st.info("No suggestions have been submitted yet.")
    st.stop()

# -------------------------------------------------
# Analytics
# -------------------------------------------------
st.header("Suggestion Analytics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Suggestions by Location (Building)")
    st.bar_chart(df["location"].value_counts())

with col2:
    st.subheader("Suggestions by Department")
    st.bar_chart(df["department"].value_counts())


st.divider()

# -------------------------------------------------
# Expand / Collapse All Toggle
# -------------------------------------------------
toggle = st.button("Collapse All" if st.session_state.expand_all else "Expand All")
if toggle:
    st.session_state.expand_all = not st.session_state.expand_all
    st.rerun()

# -------------------------------------------------
# Suggestions List with Card Layout & Dialog Delete
# -------------------------------------------------
st.subheader("All Suggestions")

for _, row in df.iterrows():

    # Nice clean card layout
    with st.container(border=True):
        st.markdown(f"### Suggestion #{row['id']}")

        with st.expander("Details", expanded=st.session_state.expand_all):

            for col in df.columns:
                if col != "id":
                    st.write(f"**{col.capitalize()}:** {row[col]}")

            st.divider()

            if st.button(f"Delete Suggestion #{row['id']}", key=f"del_{row['id']}"):
                delete_dialog(row["id"])