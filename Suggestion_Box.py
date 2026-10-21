import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import socket
from PIL import Image
import certifi
import time

# -----------------------------
# MongoDB Initialization
# -----------------------------
def init_mongo():
    ca = certifi.where()

    client = MongoClient(st.secrets["MONGO_URI"],
        tlsCAFile=ca
    )

    db = client["improveit"]          # database
    collection = db["suggestions"]    # collection
    return collection


collection = init_mongo()


def submit_suggestion(name, department, location, suggestion, host, ip):
    doc = {
        "name": name,
        "department": department,
        "location": location,
        "suggestion": suggestion,
        "machine_host": host,
        "machine_ip": ip,
        "date_submitted": datetime.now().isoformat()
    }
    collection.insert_one(doc)


# -----------------------------
# Machine Info
# -----------------------------
def get_machine_info():
    host = socket.gethostname()
    try:
        ip = socket.gethostbyname(host)
    except:
        ip = "Unknown"
    return host, ip


# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="ImproveIt", page_icon="", layout="wide")

header = Image.open("assets/improveit_header_120.png")
st.image(header, width="stretch")

machine_host, machine_ip = get_machine_info()

st.subheader("Submit a Suggestion")


# -----------------------------------------
# Session state initialization
# -----------------------------------------
if "clear_form" not in st.session_state:
    st.session_state.clear_form = False

if "success_banner" not in st.session_state:
    st.session_state.success_banner = None

if "banner_time" not in st.session_state:
    st.session_state.banner_time = None


# -----------------------------------------
# Clear form fields BEFORE rendering widgets
# -----------------------------------------
if st.session_state.clear_form:
    st.session_state.name_field = ""
    st.session_state.dept_field = None
    st.session_state.loc_field = None
    st.session_state.sugg_field = ""
    st.session_state.clear_form = False


# -----------------------------
# Suggestion Form
# -----------------------------
with st.form("suggestion_form"):

    name = st.text_input("Your Name (required)", key="name_field")

    department = st.selectbox("Department", [
        "250 Overhead","310 Mixing","350 SG&A","650 Maintenance","740 Tubing",
        "741 Bladder Bags","742 Pressroom","743 Finishing","744 Metal Prep","745 Urethane",
        "747 Military Assembly","760 Desma","820 Rubber Track","830 Hayrolls","Accounting",
        "Administration","Assembly","Blast","Business Development","CAD/PLM","Compliance",
        "Contracts","Cutting","Cyber + Software","Engineering","Estimating","Executive",
        "Finance","Finishing","Gear","GMD","Grind","Halt Qual Test","Heat Assembly",
        "Human Resources","Industrialization","IT","Kitting","Lathe","Logistics/Product Support",
        "Maintenance","Manufacturing","Materials","Mill","Mobility","MPI","Operations",
        "PA&T","Paint/Packaging","Press Brake","Product Development","Product Support",
        "Production Control","Production Planning","Program Management","Programs","Purchasing",
        "Quality","Sales","Saw","Ship/Rcv","Supply Chain","Survivability","Systems Integration",
        "Tooling","Vetronics","Weld","Wood Shop","XM30"
    ], key="dept_field")

    location = st.selectbox("Location", ["AUBR", "BIDD", "LAPR", "LNSG", "PLYM", "STMY"], key="loc_field")

    suggestion = st.text_area("Your Suggestion", key="sugg_field")

    submitted = st.form_submit_button("Submit")


# -----------------------------
# Handle submission
# -----------------------------
if submitted:
    if not name.strip():
        st.error("Name is required.")
    elif not suggestion.strip():
        st.error("Suggestion cannot be empty.")
    else:
        submit_suggestion(name, department, location, suggestion, machine_host, machine_ip)

        st.session_state.success_banner = "Your suggestion has been submitted successfully!"
        st.session_state.banner_time = time.time()

        st.session_state.clear_form = True
        st.rerun()


# -----------------------------
# Display temporary success banner (5 seconds)
# -----------------------------
if st.session_state.success_banner:

    if time.time() - st.session_state.banner_time < 5:
        st.markdown(
            f"""
            <div style="
                background-color:#d4edda;
                color:#155724;
                padding:15px;
                border-radius:8px;
                border:1px solid #c3e6cb;
                margin-top:10px;
                font-size:16px;
                font-weight:600;">
                {st.session_state.success_banner}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.session_state.success_banner = None
        st.session_state.banner_time = None
